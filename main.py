import tkinter as tk
import time

import numpy as np

import utils
from conf import Conf
from drones.drone_annealing import DroneAnnealing
from drones.drone_model_estimator import DroneModelEstimator
from drones.drone_no_descent import DroneNoDescent
from drones.drone_random import DroneRandom
from gui import GUI


def initialize_drones(conf: Conf):
    drones = []

    for params_id, params in enumerate(conf.drones_parameters):
        for id in range(conf.drones_starting_per_point):
            for i in range(conf.drones_starting_margin * 2, conf.map_size,
                           conf.map_size // conf.drones_starting_per_side):
                for starting_position in [(i, conf.drones_starting_margin),
                                          (i, conf.map_size - conf.drones_starting_margin),
                                          (conf.drones_starting_margin, i),
                                          (conf.map_size - conf.drones_starting_margin, i)]:

                    match params[0]:
                        case "DroneNoDescent":
                            drones.append(DroneNoDescent(starting_position,
                                                         color=params[1],
                                                         descent_probab=params[2],
                                                         ignore_value_step_num=params[3],
                                                         params_id=params_id,
                                                         id=id))
                        case "DroneRandom":
                            drones.append(DroneRandom(starting_position,
                                                      color=params[1],
                                                      params_id=params_id,
                                                      id=id))
                        case "DroneAnnealing":
                            drones.append(DroneAnnealing(starting_position,
                                                         color=params[1],
                                                         start_temp=params[2],
                                                         temp_multiplier=params[3],
                                                         epoch_size=params[4],
                                                         params_id=params_id,
                                                         ))
                        case "DroneModelEstimator":
                            drones.append(DroneModelEstimator(starting_position,
                                                              color=params[1],
                                                              signal_to_distance=params[2],
                                                              map_dims=(conf.map_size, conf.map_size),
                                                              probab_map_relative_dims=params[3],
                                                              ignore_value_step_num=params[4],
                                                              source_estimation_frequency=params[4],
                                                              params_id=params_id,
                                                              ))
    return drones


if __name__ == "__main__":
    conf = Conf()
    root = tk.Tk()

    start = time.time()
    utils.preprocess("assets/original/" + conf.map_name + ".tiff", conf.cells_number, conf.image_size,
                     "assets/processed/" + conf.map_name + ".csv", False)
    print(f"Preparing map took: {time.time()-start:.4f}[s]")

    start = time.time()
    grid_matrix = utils.load_matrix("assets/processed/" + conf.map_name + ".csv")
    print(f"Loading matrix took: {time.time()-start:.4f}[s]")

    start = time.time()
    drones = initialize_drones(conf)
    print(f"Initializing drones took: {time.time()-start:.4f}[s]")


    max_value = np.max(grid_matrix)
    print("Max value on whole map:", max_value)
    gui = GUI(root, grid_matrix, drones, max_value, conf)
    gui.run()
