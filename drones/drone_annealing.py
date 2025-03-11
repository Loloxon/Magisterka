import math

from drone_no_descent import DroneNoDescent


class DroneAnnealing(DroneNoDescent):
    def __init__(self, starting_position, start_temp, temp_multiplier, epoch_size, color="black",
                 ignore_value_step_num=8, params_id=-1, id=-1):
        super().__init__(starting_position, color=color, ignore_value_step_num=ignore_value_step_num,
                         params_id=params_id, id=id)
        self.epoch_size = epoch_size
        self.temp_multiplier = temp_multiplier
        self.temp = start_temp
        self.round_cnt = 0

    def do_move(self):
        self.curr_signal = self.signal_received()

        # print(f"(x,y): {(self.x, self.y)}", end=" ")
        if self.patrol_mode:

            # print("patrol", end = " ")
            self.do_move_patrol()
        else:
            self.update_descent_probab()
            self.update_temp()
            # print("follow", end = " ")
            self.do_move_follow()

        # print()
        self.max_signal = max(self.max_signal, self.curr_signal)
        self.prev_signal = self.curr_signal

    def update_descent_probab(self):
        # Calculate the difference in signal between current and new solution
        if self.prev_signal is None:
            self.descent_probab = 0
            return

        signal_diff = self.curr_signal - self.prev_signal

        # Calculate the probability of accepting a worse solution using Boltzmann distribution
        if signal_diff >= 0:  # New solution is better
            self.descent_probab = 1.0
        else:  # New solution is worse
            self.descent_probab = math.exp(signal_diff / self.temp)

    def update_temp(self):
        self.round_cnt += 1
        if self.round_cnt == self.epoch_size:
            self.temp *= self.temp_multiplier
