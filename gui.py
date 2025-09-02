import os

import itertools
import threading
import tkinter as tk
from time import sleep
import numpy as np
from tqdm import tqdm

from map import Map
from utils import plot_scores


class GUI:
    def __init__(self, master, grid_matrix, drones, drone_hives, max_signal, conf):
        self.conf = conf

        self.master = master
        self.master.title("Simple GUI")

        self.drones_movement_thread = None

        self.cell_size = conf.cell_size
        self.iterations = conf.iterations

        self.drones_parameters = conf.drones_parameters
        self.drone_hives_parameters = conf.drone_hives_parameters

        self.refresh_interval = conf.refresh_interval
        self.save_to_file_interval = conf.save_to_file_interval

        self.visualization_hidden = conf.visualization_hidden
        self.drones_hidden = conf.drones_hidden

        self.canvas = tk.Canvas(self.master,
                                width=len(grid_matrix[0]) * self.cell_size,
                                height=len(grid_matrix) * self.cell_size)
        # self.canvas = tk.Canvas(self.master,
        #                         width=200,
        #                         height=100)
        self.canvas.grid(row=0, column=0)
        # self.canvas = None

        self.drones_released = False
        self.drones_control_btn = tk.Button(self.master, text="Uruchom symulacje",
                                            command=self.drones_control_btn_clicked)
        self.drones_control_btn.grid(row=1, column=0, pady=10)

        self.simulation_hidden = False
        self.hide_btn = tk.Button(self.master, text="Ukryj podgląd", command=self.hide_btn_clicked)
        self.hide_btn.grid(row=2, column=0, pady=10)

        self.plots_btn = tk.Button(self.master, text="Stwórz wykresy", command=self.plots_btn_clicked)
        self.plots_btn.grid(row=3, column=0, pady=10)

        self.grid_matrix = grid_matrix

        self.map = Map(self.canvas, grid_matrix, self.cell_size, max_signal)

        if not self.visualization_hidden:
            self.map.draw_grid()

        self.drones = drones
        for drone in self.drones:
            drone.set_values(self.canvas, self.map, self, master)
            if not self.drones_hidden:
                drone.draw()

        self.drone_hives = drone_hives
        for drone_hive in self.drone_hives:
            drone_hive.set_values(self.canvas, self.map, self, master)
            if not self.drones_hidden:
                drone_hive.draw()

        self.prepare_file_new()

    def run(self):
        self.drones_movement_thread = threading.Thread(target=self.move_drones)
        self.drones_movement_thread.daemon = True
        self.drones_movement_thread.start()

        self.drones_released = True
        self.drones_control_btn.config(text="Zatrzymaj symulacje")

        self.conf.update_names()
        self.drones_movement_thread.join()

        # # save canva as png to file:
        # self.canvas.update()
        # self.canvas.postscript(file="canvas_output.ps", colormode="color")

        # self.master.mainloop()


    def drones_control_btn_clicked(self):
        if self.drones_released:
            self.drones_released = False
            print("Drones stopped!")
            self.drones_control_btn.config(text="Uruchom symulacje")
        else:
            self.drones_released = True
            print("Drones released!")
            self.drones_control_btn.config(text="Zatrzymaj symulacje")

    def hide_btn_clicked(self):
        if self.simulation_hidden:
            self.simulation_hidden = False
            self.canvas.delete(self.map.curtain)
            for drone in self.drones:
                drone.draw()
            for drone_hive in self.drone_hives:
                drone_hive.draw()
            print("Simulation shown!")
            self.hide_btn.config(text="Ukryj podgląd")
        else:
            self.simulation_hidden = True
            self.map.hide_grid()
            print("Simulation hidden!")
            self.hide_btn.config(text="Pokaż podgląd")

    def plots_btn_clicked(self):
        # print("Drawing plots!")
        self.conf.update_names()

        plot_scores(self.conf.log_avg_max_sig, "Average max signal", self.drones_parameters,
                    self.drone_hives_parameters, self.conf.map_name)
        # plot_scores(self.conf.log_max_count, "Winners", self.drones_parameters, self.drone_hives_parameters,
        #             self.conf.map_name)
        # plot_scores(self.conf.log_avg_current_sig, "Average current signal", self.drones_parameters,
        #             self.drone_hives_parameters, self.conf.map_name)

    def prepare_file(self):
        self.conf.update_names()
        for file_name in [self.conf.log_avg_max_sig, self.conf.log_max_count, self.conf.log_avg_current_sig]:
            with open(file_name, 'w') as file:
                file.write(";")
                for _, params in enumerate(self.drones_parameters):
                    name = params[0]
                    if name == "DroneNoDescent":
                        info = params[2]
                    elif name == "DroneRandom":
                        info = ""
                    elif name == "DroneModelEstimator":
                        info = params[3]
                    elif name == "DroneAnnealing":
                        info = params[2:5]
                    else:
                        info = params[1:]
                    file.write(str(name) + ": " + str(info) + ";")

                for _, params in enumerate(self.drone_hives_parameters):
                    name = params[0]
                    if name == "DroneHiveRandomTaboo":
                        info = ""
                    elif name == "DroneHiveTry1":
                        info = ""
                    else:
                        info = params[1:]
                    file.write(str(name) + ": " + str(info) + ";")
                file.write("\n")

    def prepare_file_new(self):
        self.conf.update_names()
        for file_name in [self.conf.log_avg_max_sig, self.conf.log_max_count, self.conf.log_avg_current_sig]:
            for _, params in enumerate(self.drone_hives_parameters):
                file_name_new = file_name[:-4] + "_" + str(params[0])[9:] + ".csv"

                # path = "assets\\graphs_v3_new"
                os.makedirs(file_name_new[:-10], exist_ok=True)

                with open(file_name_new, 'w') as file:
                    file.write(";")
                    for i in range(self.conf.drones_starting_per_point):

                        file.write(f"version_{i};")
                    file.write("\n")

    def save_to_file_new(self):
        self.prepare_file_new()
        self.conf.update_names()
        for file_name in [self.conf.log_avg_max_sig, self.conf.log_max_count, self.conf.log_avg_current_sig]:
            for params_id, params in enumerate(self.drone_hives_parameters):
                file_name_new = file_name[:-4] + "_" + str(params[0])[9:] + ".csv"

                with open(file_name_new, 'a') as file:
                    # file.write(str(iteration_no) + ";")
                    values_to_save = []
                    for drone_hive in self.drone_hives:
                        # summed_curr = 0

                        if drone_hive.params_id == params_id:
                            # summed_curr += drone_hive.curr_signal

                            if file_name.startswith(self.conf.log_avg_max_sig):
                                values_to_save.append(drone_hive.max_signal_for_metric)
                                # value_to_save = np.round(summed_curr / self.map.max_signal, 4)

                            elif file_name.startswith(self.conf.log_max_count):
                                values_to_save.append(drone_hive.max_count_for_metric)
                                # value_to_save = np.round(drone_hive.visited_max_signal, 4)

                            elif file_name.startswith(self.conf.log_avg_current_sig):
                                values_to_save.append(drone_hive.curr_signal_for_metric)
                                # value_to_save = np.round(summed_curr / self.map.max_signal, 4)
                            else:
                                raise ValueError("Unknown file name")
                            # file.write(str(value_to_save) + ";")

                            values_to_save[-1].append(drone_hive.first_iteration_hit_max)

                    transposed = list(zip(*values_to_save))
                    for i, row in enumerate(transposed, start=1):
                        line = [str(i)] + [str(val) for val in row]
                        file.write(";".join(line) + "\n")

                    file.write("\n")

    def move_drones(self):
        finishing_moves = 100
        end_condition = False  # Initialize outside the loop

        for iteration in tqdm(range(self.iterations)):
            while not self.drones_released:
                sleep(0.01)  # Increase sleep duration to reduce CPU usage

            # Perform moves and draw for drones and drone hives
            for entity in itertools.chain(self.drones, self.drone_hives):
                if len(self.drones) > 0 and isinstance(entity, type(self.drones[0])):  # Check if it's a drone
                    entity.do_move()
                else:  # Assume it's a drone hive
                    entity.do_move(iteration, self.iterations)

                if iteration % self.refresh_interval == 0:
                    if not self.conf.drones_hidden:
                        entity.draw()

            # # Save to file at intervals
            # if iteration % 100 == 0:
            #     self.save_to_file_new(iteration)

            # Check end condition only once per iteration
            # if not end_condition:
            #     end_condition = all(
            #         entity.max_signal >= self.map.max_signal for entity in
            #         itertools.chain(self.drones, self.drone_hives)
            #     )
            if not end_condition:
                end_condition = all(
                    hive.can_end for hive in self.drone_hives
                )

            if end_condition:
                finishing_moves -= 1
            if finishing_moves <= 0:
                break

        # print("Ending simulation!")

        self.drones_released = True
        self.save_to_file_new()
        # self.drones_control_btn.config(text="Drones are done!")
        # self.drones_control_btn.config(state="disabled")
        # self.plots_btn_clicked()

        # self.master.destroy()
