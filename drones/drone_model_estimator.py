import random

import numpy as np

from drone_no_descent import DroneNoDescent


class DroneModelEstimator(DroneNoDescent):
    def __init__(self, starting_position, signal_to_distance, map_dims: tuple, probab_map_relative_dims,
                 source_estimation_frequency, color="black", ignore_value_step_num=8, params_id=-1, id=-1):
        super().__init__(starting_position, color=color, ignore_value_step_num=ignore_value_step_num,
                         params_id=params_id, id=id)
        self.line_id = None
        self.source_icon_id = None
        self.map_dims = map_dims
        self.probab_map_relative_dims = probab_map_relative_dims
        self.signal_to_distance = signal_to_distance
        self.source_estimation_frequency = source_estimation_frequency
        self.round_cnt = 0
        self.estimation_step_cnt = 0
        # create a numpy 2D array
        # this map holds a value relative to the probability that the signal source is at the coordinates corresponding to the indexes
        self.probab_map = np.ones((int(map_dims[0] * probab_map_relative_dims[0]),
                                   int(map_dims[1] * probab_map_relative_dims[1])))
        self.source_x = None
        self.source_y = None
        # self.visited =

    def indices_to_coordinates(self, indices: tuple):
        return (indices[0] / self.probab_map_relative_dims[0],
                indices[1] / self.probab_map_relative_dims[1])

    def do_move(self):
        self.curr_signal = self.signal_received()

        self.estimate_source()
        # print(f"(x,y): {(self.x, self.y)}", end=" ")
        if self.patrol_mode or (self.source_x is None or self.source_y is None):
            # print("patrol", end = " ")
            self.do_move_patrol()
        else:
            # print("follow", end = " ")
            # print(f"follows from {(self.x, self.y)} to {(self.source_y, self.source_y)}")
            self.do_move_follow()

        # print()
        self.max_signal = max(self.max_signal, self.curr_signal)
        self.prev_signal = self.curr_signal

    def estimate_source(self):
        """
        1. Update probab_map based on distance between the drone (position self.x, self.y)
        and the coordinates of each cell (using indices_to_coordinates), self.curr_signal, and the signal_to_distance function
        which models the most probable distance for a given signal strength.
        2. Find the point with the highest probability, when there are more than one pick the closest to (self.x, self.y).
        """

        if self.curr_signal == 0:
            return

        if self.estimation_step_cnt % self.source_estimation_frequency != 0:
            self.estimation_step_cnt += 1
            return

        self.estimation_step_cnt += 1
        self.patrol_mode = False

        for i in range(self.probab_map.shape[0]):
            for j in range(self.probab_map.shape[1]):
                coord = self.indices_to_coordinates((i, j))
                distance = np.sqrt((self.x - coord[0])**2 + (self.y - coord[1])**2)
                expected_distance = self.signal_to_distance(self.curr_signal)
                # Update the probability map with Gaussian-like probability based on the distance difference
                self.probab_map[i, j] += np.exp(-((distance - expected_distance)**2) / (2 * (expected_distance / 2)**2))

        # Find the index with the highest probability
        max_prob_idx = np.unravel_index(np.argmax(self.probab_map, axis=None), self.probab_map.shape)
        self.source_x, self.source_y = self.indices_to_coordinates(max_prob_idx)

    def do_move_follow(self):
        """
        Set the speeds self.dx and self.dy to make the drone at (self.x, self.y) point towards (self.source_x, self.source_y).
        The vector (dx, dy) should be unitary.
        """
        direction = np.array([self.source_x - self.x, self.source_y - self.y])
        norm = np.linalg.norm(direction)
        if norm != 0:
            unit_direction = direction / norm
            self.d_x, self.d_y = unit_direction[0], unit_direction[1]

        if not self.move(self.d_x, self.d_y):
            if self.orientation == 0:
                self.d_x = -self.d_x
            else:
                self.d_y = -self.d_y

    def draw(self):
        super().draw()

        if not self.GUI.simulation_hidden and (self.source_x is not None and self.source_y is not None):
            x0 = self.source_x - self.drone_size // 4
            y0 = self.source_y - self.drone_size // 4
            x1 = self.source_x + self.drone_size // 4
            y1 = self.source_y + self.drone_size // 4

            if self.source_icon_id is None:
                self.source_icon_id = self.canvas.create_oval(x0, y0, x1, y1, fill=("orange" if self.patrol_mode else "black"), outline=self.color, width=3)

            self.canvas.coords(self.source_icon_id, x0, y0, x1, y1)

            if self.source_x is not None and self.source_y is not None:
                if self.line_id is None:
                    self.line_id = self.canvas.create_line(self.source_x, self.source_y, self.x, self.y, fill="white", width=0.5)
                else:
                    self.canvas.coords(self.line_id, self.source_x, self.source_y, self.x, self.y)