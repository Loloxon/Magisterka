import copy

from drone_random import DroneRandom


class DroneHiveTry1:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.children = [DroneRandom(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]

        self.color = color
        self.params_id = params_id
        self.id = id

        self.max_signal = 0
        self.curr_signal = None

        assert conf is not None
        self.conf = conf

        self.cells_number = 30
        self.cell_size = self.conf.map_size // self.cells_number

        self.highest_registered_signal = [[0 for _ in range(self.cells_number)] for _ in range(self.cells_number)]
        self.target_probabilities = [[None for _ in range(self.cells_number)] for _ in range(self.cells_number)]

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            if not self.conf.drones_hidden:
                child.draw()

    def do_move(self):
        max_signal_tmp = 0
        curr_signal_tmp = 0
        for i, child in enumerate(self.children):
            child.do_move()
            max_signal_tmp += child.max_signal
            curr_signal_tmp += child.curr_signal

            child_cell = self.locate_cell(child.get_position())
            self.update_highest_registered_signal(child_cell, child.curr_signal)

        self.smoothen_probabilities()

        self.max_signal = max_signal_tmp / len(self.children)
        self.curr_signal = curr_signal_tmp / len(self.children)

    def smoothen_probabilities(self):
        new_target_probabilities = copy.deepcopy(self.target_probabilities)
        for y, row in enumerate(self.target_probabilities):
            for x, probability in enumerate(row):
                value = 0
                if self.target_probabilities[y][x] is not None:
                    value += self.target_probabilities[y][x]
                if y > 0 and self.target_probabilities[y - 1][x] is not None:
                    value += self.target_probabilities[y - 1][x]
                if x > 0 and self.target_probabilities[y][x - 1] is not None:
                    value += self.target_probabilities[y][x - 1]
                if y < len(self.target_probabilities) - 1 and self.target_probabilities[y + 1][x] is not None:
                    value += self.target_probabilities[y + 1][x]
                if x < len(row) - 1 and self.target_probabilities[y][x + 1] is not None:
                    value += self.target_probabilities[y][x + 1]
                if value is not None:
                    new_target_probabilities[y][x] = round(value / 5, 4)
        # self.target_probabilities = copy.deepcopy(new_target_probabilities)

    def locate_cell(self, position) -> tuple:
        return position[0] // self.cell_size, position[1] // self.cell_size

    def update_highest_registered_signal(self, child_cell: tuple, signal):
        if self.highest_registered_signal[child_cell[0]][child_cell[1]] < signal:
            self.highest_registered_signal[child_cell[0]][child_cell[1]] = round(signal, 2)

            self.target_probabilities[child_cell[0]][child_cell[1]] = round(signal / self.conf.max_signal, 4)
