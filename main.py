import tkinter as tk

import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit, fsolve

from drones.drone_annealing import DroneAnnealing
from drones.drone_model_estimator import DroneModelEstimator
from drones.drone_no_descent import DroneNoDescent
from drones.drone_random import DroneRandom
from gui import GUI
from utils import preprocess, load_matrix


def custom_function(x, A, B, C, D, max_val):
    return A * max_val / ((x + D) ** 2) + B * max_val / (x + D) + C


def custom_function2(x, A, C, D, max_val):
    return A * max_val / ((x + D) ** 2) + C


def custom_function_strength(value, A, B, C, max_val):
    return A * (value ** 2) / max_val + B * value / max_val + C


# def inverse_function(A, B, C, D, max_val, y):
#     return (np.sqrt(-4 * A * C * E + 4 * A * E * x + B^2 E^2) + B E + 2 C D - 2 D x)/(2 (x - C))
# def inverse_function(A, B, C, D, max_val, y):
#     # Define symbolic variables
#     x = sp.Symbol('x')
#     # Define the equation A * max_val / ((x + D)**2) + B * max_val / (x + D) + C - y = 0
#     equation = A * max_val / ((x + D) ** 2) + B * max_val / (x + D) + C - y
#     # Solve the equation for x
#     solutions = sp.solve(equation, x)
#     return solutions


class MainClass:

    def analyze_map(map_matrix: np.ndarray, eps: float = 0.1):
        # Step 1: Find the source point (average coordinates of the maximum value)
        max_value = np.max(map_matrix)
        max_coords = np.argwhere(map_matrix == max_value)
        source_point = np.mean(max_coords, axis=0)

        # Step 2: Calculate distances from the source point and round them
        distances = np.zeros_like(map_matrix, dtype=float)
        for i in range(map_matrix.shape[0]):
            for j in range(map_matrix.shape[1]):
                distances[i, j] = np.round(np.sqrt((i - source_point[0]) ** 2 + (j - source_point[1]) ** 2))

        # Step 3: Calculate the average value and standard deviation of map_matrix for each unique distance
        unique_distances = np.unique(distances)
        avg_values = []
        std_devs = []
        for d in unique_distances:
            values_at_distance = map_matrix[distances == d]
            avg_values.append(values_at_distance.mean())
            std_devs.append(values_at_distance.std())

        # Convert to numpy arrays for easier indexing
        unique_distances = np.array(unique_distances)
        avg_values = np.array(avg_values)
        std_devs = np.array(std_devs)

        # Step 4: Filter out distances where average value is below eps
        mask = avg_values >= eps
        filtered_distances = unique_distances[mask]
        filtered_avg_values = avg_values[mask]
        filtered_std_devs = std_devs[mask]

        # Step 5: Fit the custom functions to the filtered data
        if len(filtered_distances) > 0:
            try:
                popt1, pcov1 = curve_fit(lambda x, A, B, C, D: custom_function(x, A, B, C, D, max_value),
                                         filtered_distances, filtered_avg_values, p0=(1, 1, 1, 1))
                A1, B1, C1, D1 = popt1
                # Print the fitted coefficients for the first function
                print(f"Fitted parameters for custom_function: A={A1}, B={B1}, C={C1}, D={D1}")

                # Generate points for plotting the fitted curve for the first function
                x_fit1 = np.linspace(filtered_distances.min(), filtered_distances.max(), 100)
                y_fit1 = custom_function(x_fit1, A1, B1, C1, D1, max_value)
            except Exception as e:
                print(f"Curve fitting failed for custom_function: {e}")
                x_fit1 = np.array([])
                y_fit1 = np.array([])

            try:
                popt2, pcov2 = curve_fit(lambda x, A, C, D: custom_function2(x, A, C, D, max_value),
                                         filtered_distances, filtered_avg_values, p0=(1, 1, 1))
                A2, C2, D2 = popt2
                # Print the fitted coefficients for the second function
                print(f"Fitted parameters for custom_function2: A={A2}, C={C2}, D={D2}")

                # Generate points for plotting the fitted curve for the second function
                x_fit2 = np.linspace(filtered_distances.min(), filtered_distances.max(), 100)
                y_fit2 = custom_function2(x_fit2, A2, C2, D2, max_value)
            except Exception as e:
                print(f"Curve fitting failed for custom_function2: {e}")
                x_fit2 = np.array([])
                y_fit2 = np.array([])
        else:
            print("Not enough points to fit the curves. Adjust the eps value.")
            x_fit1 = np.array([])
            y_fit1 = np.array([])
            x_fit2 = np.array([])
            y_fit2 = np.array([])

        # Step 6: Plot the results with uncertainty visualization
        plt.figure(figsize=(10, 6))
        plt.errorbar(filtered_distances, filtered_avg_values, yerr=filtered_std_devs, fmt='o', label='Data points')
        if x_fit1.size > 0:
            plt.plot(x_fit1, y_fit1, label='Fitted curve (custom_function)')
        if x_fit2.size > 0:
            plt.plot(x_fit2, y_fit2, label='Fitted curve (custom_function2)')
        plt.xlabel('Distance from Source Point')
        plt.ylabel('Average Value')
        plt.title('Average Value of Map by Distance to Source Point')
        plt.legend()
        plt.grid(True)
        plt.show()

        # Return the requested values
        return max_value, source_point, lambda x: custom_function(x, A1, B1, C1, D1, max_value)

    def analyze_map_strength(map_matrix: np.ndarray, map_size: int, eps: float = 0.1):
        # Step 1: Find the source point (average coordinates of the maximum value)
        max_value = np.max(map_matrix)
        max_coords = np.argwhere(map_matrix == max_value)
        source_point = np.mean(max_coords, axis=0)

        # Step 2: Calculate distances from the source point, considering the map size
        distances = np.zeros_like(map_matrix, dtype=float)
        for i in range(map_matrix.shape[0]):
            for j in range(map_matrix.shape[1]):
                x_coord = i * (map_size / map_matrix.shape[0])
                y_coord = j * (map_size / map_matrix.shape[1])
                source_x_coord = source_point[0] * (map_size / map_matrix.shape[0])
                source_y_coord = source_point[1] * (map_size / map_matrix.shape[1])
                distances[i, j] = np.sqrt((x_coord - source_x_coord) ** 2 + (y_coord - source_y_coord) ** 2)


        # Step 3: Calculate the average distance and standard deviation for each rounded value
        rounded_values = np.round(map_matrix, decimals=2)
        unique_values = np.unique(rounded_values)
        avg_distances = []
        std_devs = []
        for value in unique_values:
            distances_at_value = distances[rounded_values == value]
            avg_distances.append(distances_at_value.mean())
            std_devs.append(distances_at_value.std())

        # Convert to numpy arrays for easier indexing
        unique_values = np.array(unique_values)
        avg_distances = np.array(avg_distances)
        std_devs = np.array(std_devs)

        # Step 4: Filter out values where average distance is below eps
        mask = avg_distances >= eps
        filtered_values = unique_values[mask]
        filtered_avg_distances = avg_distances[mask]
        filtered_std_devs = std_devs[mask]

        # Step 5: Fit the custom function to the filtered data
        if len(filtered_values) > 0:
            try:
                popt, pcov = curve_fit(lambda value, A, B, C: custom_function_strength(value, A, B, C, max_value),
                                       filtered_values, filtered_avg_distances, p0=(1, 1, 1))
                A, B, C = popt
                # Print the fitted coefficients for the function
                print(f"Fitted parameters for custom_function: A={A}, B={B}, C={C}")

                # Generate points for plotting the fitted curve
                value_fit = np.linspace(filtered_values.min(), filtered_values.max(), 100)
                distance_fit = custom_function_strength(value_fit, A, B, C, max_value)
            except Exception as e:
                print(f"Curve fitting failed for custom_function: {e}")
                value_fit = np.array([])
                distance_fit = np.array([])
        else:
            print("Not enough points to fit the curves. Adjust the eps value.")
            value_fit = np.array([])
            distance_fit = np.array([])

        # Step 6: Plot the results with uncertainty visualization
        plt.figure(figsize=(10, 6))
        plt.errorbar(filtered_values, filtered_avg_distances, yerr=filtered_std_devs, fmt='o', label='Data points')
        if value_fit.size > 0:
            plt.plot(value_fit, distance_fit, label='Fitted curve (custom_function)')
        plt.xlabel('Value')
        plt.ylabel('Average Distance')
        plt.title('Average Distance by Value')
        plt.legend()
        plt.grid(True)
        plt.show()

        # Return the requested values
        return max_value, source_point, lambda value: custom_function_strength(value, A, B, C, max_value)

    def __init__(self):
        root = tk.Tk()
        image_size = 1000
        cells_number = 125
        map_size = 600
        cell_size = map_size // cells_number
        file_name = "góry"
        preprocess("assets/original/" + file_name + ".tiff", cells_number, image_size,
                   "assets/processed/" + file_name + ".csv")
        grid_matrix = load_matrix("assets/processed/" + file_name + ".csv")
        # max_value, source_point, signal_func = MainClass.analyze_map(grid_matrix)
        max_value, source_point, distance_from_signal = MainClass.analyze_map_strength(grid_matrix, map_size)
        drones = []

        iterations = 10000
        refresh_interval = 1
        save_to_file_interval = 1

        start_border_margin = 50
        number_of_drones_per_side = 1
        number_of_drones_per_place = 1

        # descent_probabs = [0, 0.25, 0.5, 0.75, 0.85]
        descent_probabs = [0.25, 0.5, 0.75]
        # colors = ["blue", "green", "orange", "red", "yellow"]
        colors = ["orange", "orange", "orange"]
        # all_ignore_value_step_nums = [
        #     [1, 2, 4],
        #     [1, 2, 4],
        #     [1, 2, 4],
        #     [1, 2, 4],
        #     [1, 2, 4]
        # ]
        all_ignore_value_step_nums = [
            [4],
            [4],
            [4]
        ]


        possible_params = {}
        idx = 0
        for color, descent_probab, ignore_value_step_nums in zip(colors, descent_probabs, all_ignore_value_step_nums):
            for ignore_value_step_num in ignore_value_step_nums:
                possible_params[idx] = ("DroneNoDescent", "orange", descent_probab, ignore_value_step_num)
                idx += 1

        possible_params[idx] = ("DroneRandom", "green")
        idx += 1

        all_ignore_value_step_nums_estimator = [
            [4]
        ]

        # signal_to_distance, map_dims: tuple, probab_map_relative_dims,
        # source_estimation_frequency
        # for ignore_value_step_nums in all_ignore_value_step_nums_estimator:
        #     for ignore_value_step_num in ignore_value_step_nums:
        #         possible_params[idx] = (
        #         "DroneModelEstimator", "red", distance_from_signal, (0.05, 0.05), ignore_value_step_num)
        #         idx += 1

        start_temps = [1]
        temp_muls = [0.9, 0.4]
        # temp_muls = [0.9, 0.4, 0.2]
        epoch_sizes = [10, 1]

        for start_temp in start_temps:
            for temp_mul in temp_muls:
                for epoch in epoch_sizes:
                    possible_params[idx] = (
                        "DroneAnnealing", "blue", start_temp, temp_mul, epoch, ignore_value_step_num)
                    idx += 1
        possible_params[idx] = (
            "DroneAnnealing", "blue", 100, 0.4, 10, 4)
        idx += 1
        possible_params[idx] = (
            "DroneAnnealing", "blue", 100, 0.4, 1, 4)
        idx += 1

        for params_id, params in possible_params.items():
            print(params[0])
            for id in range(number_of_drones_per_place):

                for i in range(start_border_margin * 2, map_size, map_size // number_of_drones_per_side):
                    for starting_position in [(i, start_border_margin),
                                              (i, map_size - start_border_margin),
                                              (start_border_margin, i),
                                              (map_size - start_border_margin, i)]:

                        if params[0] == "DroneNoDescent":
                            drones.append(DroneNoDescent(starting_position,
                                                         color=params[1],
                                                         descent_probab=params[2],
                                                         ignore_value_step_num=params[3],
                                                         params_id=params_id,
                                                         id=id))
                        elif params[0] == "DroneRandom":
                            drones.append(DroneRandom(starting_position,
                                                      color=params[1],
                                                      params_id=params_id,
                                                      id=id))
                        elif params[0] == "DroneAnnealing":
                            drones.append(DroneAnnealing(starting_position,
                                                         color=params[1],
                                                         start_temp=params[2],
                                                         temp_multiplier=params[3],
                                                         epoch_size=params[4],
                                                         params_id=params_id,
                                                         ))
                        elif params[0] == "DroneModelEstimator":
                            params_id
                            drones.append(DroneModelEstimator(starting_position,
                                                              color=params[1],
                                                              signal_to_distance=params[2],
                                                              map_dims=(map_size, map_size),
                                                              probab_map_relative_dims=params[3],
                                                              ignore_value_step_num=params[4],
                                                              source_estimation_frequency=params[4],
                                                              params_id=params_id,
                                                              ))

        max_value = np.max(grid_matrix)
        print(max_value)

        GUI(root, grid_matrix, cell_size, drones, max_value, iterations, refresh_interval, save_to_file_interval,
            possible_params)
        root.mainloop()


if __name__ == "__main__":
    obj = MainClass()
