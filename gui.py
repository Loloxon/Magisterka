from tqdm import tqdm
import threading
import tkinter as tk
from time import sleep

from map import Map
from utils import plot_scores


class GUI:
    def __init__(self, master, grid_matrix, drones, max_value, conf):
        self.conf = conf

        self.master = master
        self.master.title("Simple GUI")

        self.cell_size = conf.cell_size
        self.iterations = conf.iterations

        self.drones_parameters = conf.drones_parameters

        self.refresh_interval = conf.refresh_interval
        self.save_to_file_interval = conf.save_to_file_interval

        self.canvas = tk.Canvas(self.master,
                                width=len(grid_matrix[0]) * self.cell_size,
                                height=len(grid_matrix) * self.cell_size)
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

        self.map = Map(self.canvas, grid_matrix, self.cell_size, max_value)
        self.map.draw_grid()

        self.drones = drones
        for drone in self.drones:
            drone.set_values(self.canvas, self.map, self, master)
            drone.draw()

        self.prepare_file()

    def run(self):
        drones_movement_thread = threading.Thread(target=self.move_drones)
        drones_movement_thread.daemon = True
        drones_movement_thread.start()

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
            print("Simulation shown!")
            self.hide_btn.config(text="Hide simulation")
        else:
            self.simulation_hidden = True
            self.map.hide_grid()
            print("Simulation hidden!")
            self.hide_btn.config(text="Show simulation")

    def plots_btn_clicked(self):
        print("Drawing plots!")
        plot_scores(self.conf.log_avg_max_sig, "Average max signal")
        plot_scores(self.conf.log_max_count, "Winners")
        plot_scores(self.conf.log_avg_current_sig, "Average current signal")

    def prepare_file(self):
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
                file.write("\n")

    def save_to_file(self, iteration_no):
        with open(self.conf.log_avg_max_sig, 'a') as file:
            file.write(str(iteration_no) + ";")
        with open(self.conf.log_max_count, 'a') as file:
            file.write(str(iteration_no) + ";")
        with open(self.conf.log_avg_current_sig, 'a') as file:
            file.write(str(iteration_no) + ";")

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
                    if drone.max_signal == self.map.max_value:
                        max_visited += 1

            with open(self.conf.log_avg_max_sig, 'a') as file:
                file.write(str((summed_max / no) / self.map.max_value) + ";")
            with open(self.conf.log_max_count, 'a') as file:
                file.write(str(max_visited / no) + ";")
            with open(self.conf.log_avg_current_sig, 'a') as file:
                file.write(str((summed_curr / no) / self.map.max_value) + ";")

        with open(self.conf.log_avg_max_sig, 'a') as file:
            file.write("\n")
        with open(self.conf.log_max_count, 'a') as file:
            file.write("\n")
        with open(self.conf.log_avg_current_sig, 'a') as file:
            file.write("\n")

    def move_drones(self):
        for iteration in tqdm(range(self.iterations)):
            while not self.drones_released:
                sleep(0.0001)

            for drone in self.drones:
                drone.do_move()
                if iteration % self.refresh_interval == 0:
                    drone.draw()

            if iteration % self.save_to_file_interval == 0:
                self.save_to_file(iteration)


        self.drones_released = True
        self.drones_control_btn.config(text="Drones are done!")
        self.drones_control_btn.config(state="disabled")
