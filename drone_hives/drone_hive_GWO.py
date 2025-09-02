import numpy as np
from drone_GWO import DroneGWO


class DroneHiveGWO:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.children = [DroneGWO(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]

        self.color = color
        self.params_id = params_id
        self.id = id
        assert conf is not None
        self.conf = conf

        self.alpha_pos = np.array([conf.map_size / 2, conf.map_size / 2])
        self.beta_pos = np.copy(self.alpha_pos)
        self.delta_pos = np.copy(self.alpha_pos)

        self.alpha_score = float('-inf')
        self.beta_score = float('-inf')
        self.delta_score = float('-inf')

        self.max_signal = float('-inf')
        self.curr_signal = None
        self.max_signal_for_metric = []
        self.max_count_for_metric = []
        self.curr_signal_for_metric = []
        self.first_iteration_hit_max = float('-inf')
        self.visited_max_signal = 0
        self.total_max_signal = conf.max_signal
        self.can_end = False

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            if not self.conf.drones_hidden:
                child.draw()

    def do_move(self, t, max_iter):
        a = 2 - t * (2 / max_iter)  # exploration coefficient

        # Update signal for all and collect info
        for child in self.children:
            child.update_signal()

        scores = [child.curr_signal for child in self.children]
        positions = [np.array([child.x, child.y]) for child in self.children]

        max_score = max(scores)
        if scores.count(max_score) == len(scores):
            # All same score — pick alpha randomly
            alpha_idx = np.random.choice(len(self.children))
            self.alpha_score = max_score
            self.alpha_pos = positions[alpha_idx]

            # Random beta and delta from remaining
            other_indices = [i for i in range(len(self.children)) if i != alpha_idx]
            beta_idx = np.random.choice(other_indices)
            other_indices.remove(beta_idx)
            delta_idx = np.random.choice(other_indices) if other_indices else beta_idx

            self.beta_score = max_score
            self.beta_pos = positions[beta_idx]
            self.delta_score = max_score
            self.delta_pos = positions[delta_idx]
        else:
            # Standard selection
            sorted_agents = sorted(zip(scores, positions), key=lambda x: x[0], reverse=True)
            self.alpha_score, self.alpha_pos = sorted_agents[0]
            self.beta_score, self.beta_pos = sorted_agents[1]
            self.delta_score, self.delta_pos = sorted_agents[2]


        visited_max_signal = 0
        for child in self.children:
            pos = np.array([child.x, child.y], dtype=float)

            # GWO vector update
            A1 = 2 * a * np.random.rand(2) - a
            C1 = 2 * np.random.rand(2)
            D_alpha = abs(C1 * self.alpha_pos - pos)
            X1 = self.alpha_pos - A1 * D_alpha

            A2 = 2 * a * np.random.rand(2) - a
            C2 = 2 * np.random.rand(2)
            D_beta = abs(C2 * self.beta_pos - pos)
            X2 = self.beta_pos - A2 * D_beta

            A3 = 2 * a * np.random.rand(2) - a
            C3 = 2 * np.random.rand(2)
            D_delta = abs(C3 * self.delta_pos - pos)
            X3 = self.delta_pos - A3 * D_delta

            new_target = (X1 + X2 + X3) / 3.0
            new_x, new_y = self.move_toward((child.x, child.y), new_target, child.step_size)

            child.x, child.y = new_x, new_y
            child.update_signal()

            if child.max_signal == self.total_max_signal:
                visited_max_signal += 1

        self.curr_signal = self.alpha_score
        self.visited_max_signal = visited_max_signal
        self.max_signal = max(self.max_signal, self.curr_signal)
        self.max_signal_for_metric.append(np.round(self.max_signal / self.total_max_signal, 4))
        self.max_count_for_metric.append(np.round(self.visited_max_signal / len(self.children), 4))
        self.curr_signal_for_metric.append(np.round(np.mean([c.curr_signal for c in self.children]) / self.total_max_signal, 4))
        if self.first_iteration_hit_max == float('-inf') and self.max_signal == self.total_max_signal:
            self.first_iteration_hit_max = t
        if self.curr_signal_for_metric[-1] == 1.0:
            self.can_end = True

    def move_toward(self, current, target, step_size=1):
        x, y = current
        tx, ty = target

        dx = int(np.clip(round(tx - x), -step_size, step_size))
        dy = int(np.clip(round(ty - y), -step_size, step_size))

        return x + dx, y + dy
