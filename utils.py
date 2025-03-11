import math
import re

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.ticker import FuncFormatter
from scipy.signal import convolve2d


def preprocess(file_path, cells_number, total_size=None, to_file=None):
    def tiff_to_matrix():
        img = Image.open(file_path)
        if img.mode != 'L':
            img = img.convert('L')
        img_array = np.array(img)
        return img_array

    def adjust_dimensions(matrix):
        zoomed_out = np.zeros((total_size, total_size))
        if total_size >= max(len(basic_matrix), len(basic_matrix[0])):
            start_row = (total_size - matrix.shape[0]) // 2
            end_row = start_row + matrix.shape[0]
            start_col = (total_size - matrix.shape[1]) // 2
            end_col = start_col + matrix.shape[1]

            zoomed_out[start_row:end_row, start_col:end_col] = matrix
        else:
            start_row = (matrix.shape[0] - total_size) // 2
            end_row = start_row + total_size
            start_col = (matrix.shape[1] - total_size) // 2
            end_col = start_col + total_size

            zoomed_out = matrix[start_row:end_row, start_col:end_col]
        return zoomed_out

    def remap(matrix):
        counter = {}
        for mat in matrix:
            for m in mat:
                if m not in counter:
                    counter[m] = 1
                else:
                    counter[m] = counter[m] + 1
        mapped = {}
        for i, key in enumerate(counter.keys()):
            mapped[key] = i * 30

        matrix_copy = np.copy(matrix)
        for i, mat in enumerate(matrix):
            for j, m in enumerate(mat):
                matrix_copy[i, j] = mapped[m]
        return matrix_copy

    def gaussian_kernel(size, sigma=1):
        """Generate a 2D Gaussian kernel."""
        kernel = np.fromfunction(lambda x, y: (1 / (2 * np.pi * sigma ** 2)) * np.exp(
            -((x - (size - 1) / 2) ** 2 + (y - (size - 1) / 2) ** 2) / (2 * sigma ** 2)), (size, size))
        gauss = kernel / np.sum(kernel)
        return gauss

    def display_matrix(matrix):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(matrix, cmap='viridis', interpolation='nearest')
        cbar = plt.colorbar(ax.imshow(matrix, cmap='viridis', interpolation='nearest'))
        cbar.set_label('Value')

        plt.show()

    basic_matrix = tiff_to_matrix()
    print(basic_matrix.shape)
    display_matrix(basic_matrix)

    if total_size is None:
        total_size = max(len(basic_matrix), len(basic_matrix[0]))

    matrix_adjusted = adjust_dimensions(basic_matrix)
    print(matrix_adjusted.shape)
    display_matrix(matrix_adjusted)

    matrix_remapped = remap(matrix_adjusted)
    display_matrix(matrix_remapped)

    reshaped_mat = matrix_remapped.reshape(
        cells_number, total_size // cells_number,
        cells_number, total_size // cells_number)

    reshaped_rounded_mat = np.round(reshaped_mat.mean(axis=(1, 3))).astype(int)

    display_matrix(reshaped_rounded_mat)

    matrix_zeroed = np.zeros_like(reshaped_rounded_mat)
    step = max(min(int(cells_number / total_size * 10), 3), 1)
    print(reshaped_rounded_mat.shape)
    print(matrix_zeroed.shape)
    matrix_zeroed[::step, ::step] = reshaped_rounded_mat[::step, ::step]
    display_matrix(matrix_zeroed)

    kernel_size = max(1, cells_number // 17)
    convolved_arr = convolve2d(matrix_zeroed, gaussian_kernel(kernel_size, 3), mode='same')
    # convolved_arr = convolve2d(matrix_remapped, gaussian_kernel(50, 1), mode='same')
    reshaped_mat = convolved_arr.reshape(
        cells_number, 1,
        cells_number, 1)

    result_1 = np.round(reshaped_mat.mean(axis=(1, 3))).astype(int)
    display_matrix(result_1)

    kernel_size2 = max(1, cells_number // 50)
    convolved_arr_2 = convolve2d(result_1, gaussian_kernel(kernel_size2, 2), mode='same')
    # convolved_arr = convolve2d(matrix_remapped, gaussian_kernel(50, 1), mode='same')
    reshaped_mat_2 = convolved_arr_2.reshape(
        cells_number, 1,
        cells_number, 1)

    result_2 = np.round(reshaped_mat_2.mean(axis=(1, 3))).astype(int)
    display_matrix(result_2)

    if to_file:
        np.savetxt(to_file, result_2, delimiter=",")
    return result_2


def load_matrix(file_path):
    return np.genfromtxt(file_path, delimiter=",")


def viridis_colormap(color_value, grid_matrix):
    normalized_value = (color_value - np.min(grid_matrix)) / (
            np.max(grid_matrix) - np.min(grid_matrix))
    cmap = cm.get_cmap('viridis')
    rgba = cmap(normalized_value)
    return "#{:02x}{:02x}{:02x}".format(int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255))


def in_bounds(squares, max_size):
    squares_in_bound = []
    for square in squares:
        squares_in_bound.append((
            min(max(0, square[0]), max_size),
            min(max(0, square[1]), max_size)
        ))
    return squares_in_bound


def cords_to_square(cords, square_size, drone_size, max_size=float('inf')):
    square = (cords[0] // square_size, cords[1] // square_size)

    square = in_bounds([square], max_size)[0]
    return square


def cords_to_square_2x2(cords, square_size, drone_size, max_size=float('inf')):
    N = int((cords[0] - drone_size / 2) // square_size)
    W = int((cords[1] - drone_size / 2) // square_size)
    S = int((cords[0] + drone_size / 2) // square_size)
    E = int((cords[1] + drone_size / 2) // square_size)

    squares = [
        (N, W),
        (N, E),
        (S, W),
        (S, E)
    ]
    squares = in_bounds(squares, max_size)
    return squares


def cords_to_square_3x3(cords, square_size, drone_size, max_size=float('inf')):
    middle_square = (cords[0] // square_size, cords[1] // square_size)

    squares = [(int(middle_square[0] + i), int(middle_square[1] + j)) for i in range(-1, 2) for j in range(-1, 2)]

    squares = in_bounds(squares, max_size)
    return squares


def square_middle_to_cords(square, square_size):
    cords = (square[0] * square_size + square_size / 2, square[1] * square_size + square_size / 2)
    return cords


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def area(point1, point2):
    return abs(point1[0] - point2[0]) * abs(point1[1] - point2[1])


def remove_angle_brackets_content(text):
    # Use regex to find and remove everything between < and >
    result = re.sub(r'<.*?>', '', text)
    return result


def plot_scores(filename, values_name):
    df = pd.read_csv(filename, sep=";", index_col=0)
    plt.figure(figsize=(10, 10))

    df_filtered = df.drop(df.columns[-1], axis=1)

    linestyles = ['-', '--', ':', '-.']
    # plt.rc('axes', prop_cycle=linestyle_cycler)

    for i, column in enumerate(df_filtered.columns):
        plt.plot(df_filtered.index, df_filtered[column], label=remove_angle_brackets_content(column),
                 linestyle=linestyles[i % (len(linestyles))])

    plt.xlabel("Iterations")
    plt.ylabel(values_name)
    plt.title(values_name + " by iterations")
    plt.legend()

    formatter = FuncFormatter(lambda y, _: '{:.2%}'.format(y))  # Format the tick labels to display percentages
    plt.gca().yaxis.set_major_formatter(formatter)

    plt.show()
