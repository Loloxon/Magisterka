import numpy as np
from drone_interface import DroneInterface


class DroneACO(DroneInterface):
    def __init__(self, starting_position, color="black", params_id=-1, id=-1):
        super().__init__(starting_position, color=color, params_id=params_id, id=id)
        self.curr_signal = None
        self.max_signal = float("-inf")
        self.path = [starting_position]
        self.total_signal = 0

    def reset(self):
        self.path = [(self.x, self.y)]
        self.total_signal = 0

    def move(self, dx, dy):
        if super().move(dx, dy):
            self.path.append((self.x, self.y))
            self.curr_signal = self.signal_received()
            self.max_signal = max(self.max_signal, self.curr_signal)
            self.total_signal += self.curr_signal
            return True
        return False

    def signal_received_at(self, x, y):
        return self.map.get_value_on((int(x), int(y)), self.drone_size)
