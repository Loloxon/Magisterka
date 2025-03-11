import random

from drone import DroneInterface


class DroneNoDescent(DroneInterface):
    def __init__(self, starting_position, color="black", descent_probab=0.05, ignore_value_step_num=8, params_id=-1, id=-1):
        super().__init__(starting_position, color=color, params_id=params_id, id=id)
        self.distance = None
        self.direction = None
        self.orientation = None
        self.need_movement_orders = True
        self.d_x = 0
        self.d_y = 0
        self.ignore_value_step_num_original = ignore_value_step_num
        self.ignore_value_step_num_current = ignore_value_step_num
        self.ignore_value_step_num_counter = ignore_value_step_num
        self.patrol_mode = True
        self.prev_signal = None
        self.redirect_probab = 0.05
        self.descent_probab = descent_probab

    def do_move(self):
        self.curr_signal = self.signal_received()

        # print(f"(x,y): {(self.x, self.y)}", end=" ")
        if self.patrol_mode:
            # print("patrol", end = " ")
            self.do_move_patrol()
        else:
            # print("follow", end = " ")
            self.do_move_follow()

        # print()
        self.max_signal = max(self.max_signal, self.curr_signal)
        self.prev_signal = self.curr_signal

    def do_move_follow(self):
        if self.ignore_value_step_num_counter <= 0:
            if self.prev_signal is not None and \
                    (self.prev_signal > self.curr_signal and random.random() > self.descent_probab or
                     (self.prev_signal == self.curr_signal and random.random() < self.redirect_probab)):
                self.d_x, self.d_y = self.create_movement_orders(False)
            self.ignore_value_step_num_counter = self.ignore_value_step_num_current
        else:
            self.ignore_value_step_num_counter -= 1

        if not self.move(self.d_x, self.d_y):
            if self.orientation == 0:
                self.d_x = -self.d_x
            else:
                self.d_y = -self.d_y

    def do_move_patrol(self):
        if self.ignore_value_step_num_counter <= 0:
            if self.prev_signal is not None and self.prev_signal < self.curr_signal:
                self.patrol_mode = False
                self.need_movement_orders = False
            self.ignore_value_step_num_counter = self.ignore_value_step_num_current
        else:
            self.ignore_value_step_num_counter -= 1

        if self.need_movement_orders:
            self.d_x, self.d_y = self.create_movement_orders(True)

        if not self.move(self.d_x, self.d_y):
            if self.orientation == 0:
                self.d_x = -self.d_x
            else:
                self.d_y = -self.d_y
        else:
            self.distance -= 1
        if self.distance == 0:

            self.need_movement_orders = True

    def create_movement_orders(self, patrol):
        self.need_movement_orders = False
        self.orientation = random.randint(0, 1)
        self.direction = random.randint(0, 1)
        if patrol:
            self.distance = random.randint(50, 100)
            self.ignore_value_step_num_current = self.ignore_value_step_num_original * 5
            self.ignore_value_step_num_counter = self.ignore_value_step_num_current
        else:
            self.distance = random.randint(10, 20)
            self.ignore_value_step_num_current = self.ignore_value_step_num_original
            self.ignore_value_step_num_counter = self.ignore_value_step_num_current
        d_x = 0
        d_y = 0
        if self.orientation == 0:
            if self.direction == 0:
                d_x = -1
            else:
                d_x = 1
        else:
            if self.direction == 0:
                d_y = -1
            else:
                d_y = 1
        return d_x, d_y

    def draw(self):
        if not self.GUI.simulation_hidden:
            x0 = self.x - self.drone_size // 2
            y0 = self.y - self.drone_size // 2
            x1 = self.x + self.drone_size // 2
            y1 = self.y + self.drone_size // 2

            if self.rectangle_id is None:
                self.rectangle_id = self.canvas.create_oval(x0, y0, x1, y1, fill="black" if self.patrol_mode else "white", outline=self.color, width=3)

            self.canvas.coords(self.rectangle_id, x0, y0, x1, y1)