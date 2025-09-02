import copy
import time
import tkinter as tk

import numpy as np

import utils
from conf import Conf
from drone_hive_ACO import DroneHiveACO
from drone_hive_PSA import DroneHivePSA
from drone_hive_PSO import DroneHivePSO
from drone_hives.drone_hive_random_taboo import DroneHiveRandomTaboo
from drone_hives.drone_hive_try1 import DroneHiveTry1
from drone_hives.drone_hive_GWO import DroneHiveGWO
from drones.drone_annealing import DroneAnnealing
from drones.drone_no_descent import DroneNoDescent
from drones.drone_random import DroneRandom
from gui import GUI


def initialize_drones(conf: Conf):
    drones = []

    for params_id, params in enumerate(conf.drones_parameters):
        for id in range(conf.drones_starting_per_point):
            for i in range(conf.drones_starting_margin * 2, conf.map_size - conf.drones_starting_margin * 2 + 1,
                           (conf.map_size - conf.drones_starting_margin * 4) // (
                                   conf.drones_starting_per_side - 1)):
                for starting_position in [(i, conf.drones_starting_margin),
                                          (i, conf.map_size - conf.drones_starting_margin),
                                          (conf.drones_starting_margin, i),
                                          (conf.map_size - conf.drones_starting_margin, i)]:

                    match params[0]:
                        case "DroneNoDescent":
                            drones.append(DroneNoDescent(starting_position,
                                                         color=params[1],
                                                         descent_probab=params[2],
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
                        # case "DroneModelEstimator":
                        #     drones.append(DroneModelEstimator(starting_position,
                        #                                       color=params[1],
                        #                                       signal_to_distance=params[2],
                        #                                       map_dims=(conf.map_size, conf.map_size),
                        #                                       probab_map_relative_dims=params[3],
                        #                                       ignore_value_step_num=params[4],
                        #                                       source_estimation_frequency=params[4],
                        #                                       params_id=params_id,
                        #                                       ))
    return drones


def spaced_with_margin(length, num_per_side, margin):
    if num_per_side == 1:
        return np.array([length / 2.0])
    return np.linspace(margin * 2, length - margin * 2, num=num_per_side)


def initialize_drone_hives(conf: Conf):
    drone_hives = []

    starting_positions = []

    # step = (conf.map_size-conf.drones_starting_margin * 2)//(conf.drones_starting_per_side+1)
    # spaced_with_margin(conf.map_size, conf.drones_starting_per_side, conf.drones_starting_margin)
    # if conf.drones_starting_per_side%2==0:
    for i in spaced_with_margin(conf.map_size, conf.drones_starting_per_side, conf.drones_starting_margin):
        for starting_position in [(i, conf.drones_starting_margin),
                                  (i, conf.map_size - conf.drones_starting_margin),
                                  (conf.drones_starting_margin, i),
                                  (conf.map_size - conf.drones_starting_margin, i)]:
            starting_positions.append(starting_position)
    # else:
    #     for i in range(conf.drones_starting_margin * 2, conf.map_size,
    #                    conf.map_size // conf.drones_starting_per_side):
    #         for starting_position in [(i, conf.drones_starting_margin),
    #                                   (i, conf.map_size - conf.drones_starting_margin),
    #                                   (conf.drones_starting_margin, i),
    #                                   (conf.map_size - conf.drones_starting_margin, i)]:
    #             starting_positions.append(starting_position)

    for params_id, params in enumerate(conf.drone_hives_parameters):
        for id in range(conf.drones_starting_per_point):
            match params[0]:
                case "DroneHiveRandomTaboo":
                    drone_hives.append(DroneHiveRandomTaboo(copy.deepcopy(starting_positions),
                                                            color=params[1],
                                                            params_id=params_id,
                                                            id=id,
                                                            conf=conf))
                case "DroneHiveTry1":
                    drone_hives.append(DroneHiveTry1(copy.deepcopy(starting_positions),
                                                     color=params[1],
                                                     params_id=params_id,
                                                     id=id,
                                                     conf=conf))
                case "DroneHiveACO":
                    drone_hives.append(DroneHiveACO(copy.deepcopy(starting_positions),
                                                    color=params[1],
                                                    params_id=params_id,
                                                    id=id,
                                                    conf=conf))
                case "DroneHiveGWO":
                    drone_hives.append(DroneHiveGWO(copy.deepcopy(starting_positions),
                                                    color=params[1],
                                                    params_id=params_id,
                                                    id=id,
                                                    conf=conf))
                case "DroneHivePSA":
                    drone_hives.append(DroneHivePSA(copy.deepcopy(starting_positions),
                                                    color=params[1],
                                                    params_id=params_id,
                                                    id=id,
                                                    conf=conf))
                case "DroneHivePSO":
                    drone_hives.append(DroneHivePSO(copy.deepcopy(starting_positions),
                                                    color=params[1],
                                                    params_id=params_id,
                                                    id=id,
                                                    conf=conf))
    return drone_hives


if __name__ == "__main__":
    start_0 = time.time()
    # Took: 164:34
    # for map_name in ["baseline"]:
    for map_name in ["góry", "hell", "krakow"]:
    # for map_name in ["baseline", "fuerta", "góry", "hell", "krakow"]:
        start_1 = time.time()
        print("=" * 30 + "|  " + map_name)
        # for mode in ["_std"]:
        for mode in ["_std", "_zmd_out", "_zmd_out_moved"]:
            if not(map_name == "góry" and mode != "_zmd_out_moved"):
                start_2 = time.time()
                print("=" * 20 + "|  " + map_name + mode)
                # for drones_starting_per_side in [2]:
                for drones_starting_per_side in [2, 4, 8]:
                    start_3 = time.time()
                    print("=" * 5 + "|  " + map_name + mode + "_" + str(drones_starting_per_side))
                    try:
                        # mode = "_zmd_out_moved"
                        full_map_name = "assets/processed/" + map_name + mode + ".csv"

                        # for map_name in ["baseline", "fuerta", "góry", "hell", "krakow"]:
                        # for map_name in ["krakow"]:
                        # for map_name in ["góry", "hell", "krakow"]:

                        conf = Conf()

                        conf.map_name = map_name + mode
                        conf.drones_starting_per_side = drones_starting_per_side
                        # conf.map_name = "góry"
                        if conf.map_name.startswith("baseline") or conf.map_name.startswith("fuerta") or conf.map_name.startswith("góry"):
                            conf.image_size = 800
                        elif conf.map_name.startswith("hell"):
                            conf.image_size = 600
                        elif conf.map_name.startswith("krakow"):
                            conf.image_size = 400
                        else:
                            raise ValueError(f"Unknown map name: {conf.map_name}")

                        root = tk.Tk()

                        # start = time.time()
                        # utils.preprocess("assets/original/" + conf.map_name + ".tiff", conf.cells_number, conf.image_size,
                        #                  "assets/processed/" + conf.map_name + ".csv", True, conf.map_start_coords_center)
                        # print(f"Preparing map took: {time.time() - start:.4f}[s]")

                        # utils.display_from_file(full_map_name)
                        # break
                        # break

                        start = time.time()
                        grid_matrix = utils.load_matrix(full_map_name)
                        # print(f"Loading matrix took: {time.time() - start:.4f}[s]")

                        start = time.time()
                        drones = initialize_drones(conf)
                        # print(f"Initializing drones took: {time.time() - start:.4f}[s]")


                        max_signal = np.max(grid_matrix)
                        conf.max_signal = max_signal
                        # print("Max value on whole map:", max_signal)

                        start = time.time()
                        drone_hives = initialize_drone_hives(conf)
                        # print(f"Initializing drones hives took: {time.time() - start:.4f}[s]")


                        start = time.time()
                        gui = GUI(root, grid_matrix, drones, drone_hives, max_signal, conf)
                        # print(f"Initializing GUI took: {time.time() - start:.4f}[s]")

                        gui.run()

                    except Exception as e:
                        print(f"An error occurred: {e}")
                        continue

                    elapsed_time = time.time() - start_3
                    minutes, seconds = divmod(elapsed_time, 60)
                    print("-" * 5 + f"|  Took: {int(minutes)}:{int(seconds):02}")
                elapsed_time = time.time() - start_2
                minutes, seconds = divmod(elapsed_time, 60)
                print("-" * 20 + f"|  Took: {int(minutes)}:{int(seconds):02}")
        elapsed_time = time.time() - start_1
        minutes, seconds = divmod(elapsed_time, 60)
        print("-" * 30 + f"|  Took: {int(minutes)}:{int(seconds):02}")
    elapsed_time = time.time() - start_0
    minutes, seconds = divmod(elapsed_time, 60)
    print("=" * 40 + f"|  Took: {int(minutes)}:{int(seconds):02}")
        #         break
        #     break
        # break
