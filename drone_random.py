import random

from drone import DroneInterface


class DroneRandom(DroneInterface):
    def __init__(self, starting_position, color="black", params_id=-1, id=-1):
        super().__init__(starting_position, color=color, params_id=params_id, id=id)
        self.distance = None
        self.direction = None
        self.orientation = None
        self.need_movement_orders = True
        self.d_x = 0
        self.d_y = 0
        self.step_size = 1

    def do_move(self):
        self.curr_signal = self.signal_received()
        if self.need_movement_orders:
            self.d_x, self.d_y = self.create_movement_orders()

        self.move(self.d_x, self.d_y)
        self.distance -= self.step_size
        if self.distance == 0:
            self.need_movement_orders = True

        self.max_signal = max(self.max_signal, self.curr_signal)

    def create_movement_orders(self):
        self.need_movement_orders = False
        self.orientation = random.randint(0, 1)
        self.direction = random.randint(0, 1)
        self.distance = random.randint(20, 50)
        d_x = 0
        d_y = 0
        if self.orientation == 0:
            if self.direction == 0:
                d_x = -self.step_size
            else:
                d_x = self.step_size
        else:
            if self.direction == 0:
                d_y = -self.step_size
            else:
                d_y = self.step_size
        return d_x, d_y
