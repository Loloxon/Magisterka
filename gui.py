import itertools
import threading
import tkinter as tk
from time import sleep

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

        # self.canvas = tk.Canvas(self.master,
        #                         width=len(grid_matrix[0]) * self.cell_size,
        #                         height=len(grid_matrix) * self.cell_size)
        self.canvas = tk.Canvas(self.master,
                                width=200,
                                height=100)
        self.canvas.grid(row=0, column=0)

        self.drones_released = False
        self.drones_control_btn = tk.Button(self.master, text="Release the Drones!",
                                            command=self.drones_control_btn_clicked)
        self.drones_control_btn.grid(row=1, column=0, pady=10)

        self.simulation_hidden = False
        self.hide_btn = tk.Button(self.master, text="Hide simulation", command=self.hide_btn_clicked)
        self.hide_btn.grid(row=2, column=0, pady=10)

        self.plots_btn = tk.Button(self.master, text="Draw plots", command=self.plots_btn_clicked)
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

        self.prepare_file()

    def run(self):
        self.drones_movement_thread = threading.Thread(target=self.move_drones)
        self.drones_movement_thread.daemon = True
        self.drones_movement_thread.start()

        self.drones_released = True
        self.drones_control_btn.config(text="Stop the Drones!")

        self.conf.update_names()
        print("Starting simulation: " + self.conf.map_name + ", " + str(self.conf.drones_starting_per_side))
        self.master.mainloop()

    def drones_control_btn_clicked(self):
        if self.drones_released:
            self.drones_released = False
            print("Drones stopped!")
            self.drones_control_btn.config(text="Release the Drones!")
        else:
            self.drones_released = True
            print("Drones released!")
            self.drones_control_btn.config(text="Stop the Drones!")

    def hide_btn_clicked(self):
        if self.simulation_hidden:
            self.simulation_hidden = False
            self.canvas.delete(self.map.curtain)
            for drone in self.drones:
                drone.draw()
            for drone_hive in self.drone_hives:
                drone_hive.draw()
            print("Simulation shown!")
            self.hide_btn.config(text="Hide simulation")
        else:
            self.simulation_hidden = True
            self.map.hide_grid()
            print("Simulation hidden!")
            self.hide_btn.config(text="Show simulation")

    def plots_btn_clicked(self):
        print("Drawing plots!")
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

    def save_to_file(self, iteration_no):
        self.conf.update_names()
        with open(self.conf.log_avg_max_sig, 'a') as file1, \
                open(self.conf.log_max_count, 'a') as file2, \
                open(self.conf.log_avg_current_sig, 'a') as file3:
            file1.write(str(iteration_no) + ";")
            file2.write(str(iteration_no) + ";")
            file3.write(str(iteration_no) + ";")

            for params_id, params in enumerate(self.drones_parameters):
                summed_max = 0
                summed_curr = 0
                max_visited = 0
                no = 0
                for drone in self.drones:
                    if drone.params_id == params_id:
                        summed_max += drone.max_signal
                        summed_curr += drone.curr_signal
                        no += 1
                        if drone.max_signal == self.map.max_signal:
                            max_visited += 1

                # with open(self.conf.log_avg_max_sig, 'a') as file:
                file1.write(str((summed_max / no) / self.map.max_signal) + ";")
                # with open(self.conf.log_max_count, 'a') as file:
                file2.write(str(max_visited / no) + ";")
                # with open(self.conf.log_avg_current_sig, 'a') as file:
                file3.write(str((summed_curr / no) / self.map.max_signal) + ";")

            for params_id, params in enumerate(self.drone_hives_parameters):
                summed_max = 0
                summed_curr = 0
                max_visited = 0
                no = 0
                for drone_hive in self.drone_hives:
                    if drone_hive.params_id == params_id:
                        summed_max += drone_hive.max_signal
                        summed_curr += drone_hive.curr_signal
                        no += 1
                        if drone_hive.max_signal == self.map.max_signal:
                            max_visited += 1

                # with open(self.conf.log_avg_max_sig, 'a') as file:
                file1.write(str((summed_max / no) / self.map.max_signal) + ";")
                # with open(self.conf.log_max_count, 'a') as file:
                file2.write(str(max_visited / no) + ";")
                # with open(self.conf.log_avg_current_sig, 'a') as file:
                file3.write(str((summed_curr / no) / self.map.max_signal) + ";")

            # with open(self.conf.log_avg_max_sig, 'a') as file:
            file1.write("\n")
            # with open(self.conf.log_max_count, 'a') as file:
            file2.write("\n")
            # with open(self.conf.log_avg_current_sig, 'a') as file:
            file3.write("\n")

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

            # Save to file at intervals
            if iteration % self.save_to_file_interval == 0:
                self.save_to_file(iteration)

            # Check end condition only once per iteration
            if not end_condition:
                end_condition = all(
                    entity.max_signal >= self.map.max_signal for entity in
                    itertools.chain(self.drones, self.drone_hives)
                )

            if end_condition:
                finishing_moves -= 1
            if finishing_moves <= 0:
                break

        print("Ending simulation!")

        self.drones_released = True
        self.drones_control_btn.config(text="Drones are done!")
        self.drones_control_btn.config(state="disabled")
        self.plots_btn_clicked()

        self.master.destroy()
