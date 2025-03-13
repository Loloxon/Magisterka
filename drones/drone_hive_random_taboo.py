import numpy as np

from drone_random import DroneRandom


class DroneHiveRandomTaboo:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.divider = 3

        self.children = [DroneRandom(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]

        # self.already_visited: list[tuple] = [(starting_position, i) for i, starting_position in
        #                                      enumerate(starting_positions)]
        self.already_visited: list[tuple] = [(starting_position[0]//self.divider, starting_position[0]//self.divider) for starting_position in
                                             starting_positions]

        self.color = color
        self.params_id = params_id
        self.id = id

        self.max_signal = 0
        self.curr_signal = None

        assert conf is not None
        self.conf = conf

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            child.draw()

    def do_move(self):
        max_signal_tmp = 0
        curr_signal_tmp = 0
        for i, child in enumerate(self.children):
            counter = 0
            visited = True
            while counter < 4 and visited:
                visited = False
                if (child.get_position()[0]//self.divider, child.get_position()[1]//self.divider) in self.already_visited:
                    visited = True

                # for visited_place, id in self.already_visited:
                #     if self.overlap(child.target_position(), visited_place, id == i):
                #         visited = True

                # print("Taboo!")
                    child.d_x, child.d_y = next_direction(child.d_x, child.d_y)
                    counter += 1

            child.do_move()
            max_signal_tmp += child.max_signal
            curr_signal_tmp += child.curr_signal

            # self.already_visited.append((child.get_position(), i))
            self.already_visited.append((child.get_position()[0]//self.divider, child.get_position()[1]//self.divider))

        self.max_signal = max_signal_tmp / len(self.children)
        self.curr_signal = curr_signal_tmp / len(self.children)

    def overlap(self, target_position, visited_place, is_its_trace):
        if is_its_trace:
            # return target_position[0] == visited_place[0] and target_position[1] == visited_place[1]
            return False
        else:
            return (np.sqrt(abs(target_position[0] - visited_place[0]) ** 2 +
                            abs(target_position[1] - visited_place[1]) ** 2)
                    < self.conf.visited_area_radius)


def next_direction(d_x, d_y):
    match (d_x, d_y):
        case (0, 1):
            return 1, 0
        case (1, 0):
            return 0, -1
        case (0, -1):
            return -1, 0
        case (-1, 0):
            return 0, 1
        case (0, 0):
            return 1, 0
        case _:
            return d_x, d_y
