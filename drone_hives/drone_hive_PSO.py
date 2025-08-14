import numpy as np
from drone_PSO import DronePSO


class DroneHivePSO:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.children = [DronePSO(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]

        assert conf is not None
        self.conf = conf
        self.color = color
        self.params_id = params_id
        self.id = id

        self.gbest_position = np.array([conf.map_size / 2, conf.map_size / 2])
        self.gbest_score = float('-inf')

        self.max_signal = float('-inf')
        self.curr_signal = None

        # PSO params
        self.w = 0.7     # inertia
        self.c1 = 1.5    # cognitive
        self.c2 = 2.5    # social

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            if not self.conf.drones_hidden:
                child.draw()

    def do_move(self, t, max_iter):
        for child in self.children:
            child.update_signal()

        # Step 1: Find max score among children
        scores = [child.curr_signal for child in self.children]
        max_score = max(scores)

        # Step 2: Get all drones that match max score
        best_candidates = [child for child in self.children if child.curr_signal == max_score]

        # Step 3: Randomly choose one
        chosen = np.random.choice(best_candidates)
        self.gbest_score = max_score
        self.gbest_position = np.array([chosen.x, chosen.y], dtype=float)


        for child in self.children:
            pos = np.array([child.x, child.y], dtype=float)
            v = child.velocity

            r1, r2 = np.random.rand(2), np.random.rand(2)

            cognitive = self.c1 * r1 * (child.best_position - pos)
            social = self.c2 * r2 * (self.gbest_position - pos)

            new_velocity = self.w * v + cognitive + social
            child.velocity = new_velocity

            target = pos + new_velocity
            new_x, new_y = self.move_toward((child.x, child.y), target, child.step_size)

            child.x, child.y = new_x, new_y
            child.update_signal()

        self.curr_signal = self.gbest_score
        self.max_signal = max(self.max_signal, self.curr_signal)

    def move_toward(self, current, target, step_size=1):
        x, y = current
        tx, ty = target

        dx = int(np.clip(round(tx - x), -step_size, step_size))
        dy = int(np.clip(round(ty - y), -step_size, step_size))

        return x + dx, y + dy
