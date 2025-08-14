from utils import *


class Map:
    def __init__(self, canvas, grid_matrix, square_size, max_signal):
        self.canvas = canvas
        self.grid_matrix = grid_matrix
        self.matrix_height = len(grid_matrix) - 1
        self.matrix_length = len(grid_matrix[0]) - 1
        self.square_size = square_size
        self.rendered_map = [[None for _ in range(len(grid_matrix[0]))] for __ in range(len(grid_matrix))]
        self.curtain = None
        self.max_signal = max_signal

    # def draw_grid(self):
    #     for i in range(len(self.grid_matrix)):
    #         for j in range(len(self.grid_matrix[0])):
    #             x0 = j * self.square_size
    #             y0 = i * self.square_size
    #             x1 = x0 + self.square_size
    #             y1 = y0 + self.square_size
    #             color_value = self.grid_matrix[i][j]
    #
    #             fill_color = viridis_colormap(color_value, self.grid_matrix)
    #
    #             self.rendered_map[i][j] = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="")

    def draw_grid(self):
        # Dictionary to group rectangles by color
        color_groups = {}

        # Precompute fill colors for all grid cells
        for i in range(len(self.grid_matrix)):
            for j in range(len(self.grid_matrix[0])):
                color_value = self.grid_matrix[i][j]
                fill_color = viridis_colormap(color_value, self.grid_matrix)

                if fill_color not in color_groups:
                    color_groups[fill_color] = []

                # Calculate rectangle coordinates
                x0 = j * self.square_size
                y0 = i * self.square_size
                x1 = x0 + self.square_size
                y1 = y0 + self.square_size

                # Group rectangles by color
                color_groups[fill_color].append((x0, y0, x1, y1))

        # Render rectangles in bulk for each color group
        for fill_color, rectangles in color_groups.items():
            for rect in rectangles:
                x0, y0, x1, y1 = rect
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="")

    def hide_grid(self):
        self.curtain = self.canvas.create_rectangle(0, 0,
                                                    (len(self.grid_matrix[0]) + 1) * self.square_size,
                                                    (len(self.grid_matrix) + 1) * self.square_size,
                                                    fill="grey", outline="")

    def get_value_on(self, cords, drone_size):
        nominator = 0
        denominator = 0

        squares = cords_to_square_2x2(cords, self.square_size, drone_size, self.matrix_height)
        for square in squares:
            middle_cords = square_middle_to_cords(square, self.square_size)

            dist = distance(cords, middle_cords)
            value = self.grid_matrix[square[1]][square[0]]

            if middle_cords == cords:
                return round(value, 5)

            nominator += value / dist
            denominator += 1 / dist
        return round(nominator / denominator, 5)

    def is_in_map(self, drone):
        return (self.square_size <= drone.x <= self.matrix_length * self.square_size
                and self.square_size <= drone.y <= self.matrix_height * self.square_size)
