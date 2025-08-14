import random
import numpy as np
from drone_interface import DroneInterface


class DronePSA(DroneInterface):
    def __init__(self, starting_position, color="black", params_id=-1, id=-1):
        super().__init__(starting_position, color=color, params_id=params_id, id=id)
        self.best_position = (self.x, self.y)
        self.best_signal = float('-inf')
        self.curr_signal = None
        self.max_signal = float('-inf')

        self.step_size = 1  # Maximum step in any direction per move

    def update_signal(self):
        self.curr_signal = self.signal_received()
        self.max_signal = max(self.max_signal, self.curr_signal)

        if self.curr_signal > self.best_signal:
            self.best_signal = self.curr_signal
            self.best_position = (self.x, self.y)
