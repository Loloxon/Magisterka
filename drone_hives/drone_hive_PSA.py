import numpy as np
import random
from drone_PSA import DronePSA


class DroneHivePSA:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.children = [DronePSA(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]

        self.color = color
        self.params_id = params_id
        self.id = id
        assert conf is not None
        self.conf = conf

        self.population_memory = [((child.x, child.y), float('-inf')) for child in self.children]

        self.T0 = 100
        self.T = self.T0
        self.iteration = 1
        self.max_iter = 1000

        self.w_max = 1.25
        self.w_min = 0.25

        self.max_signal = float('-inf')
        self.curr_signal = None

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            if not self.conf.drones_hidden:
                child.draw()

    def do_move(self, t, max_iter):
        self.iteration = t
        self.max_iter = max_iter

        if t == 0:
            self.T = 0
        else:
            self.T = self.T0 / np.log(t + 1)
        w = self.w_max - (self.w_max - self.w_min) * (t / max_iter)

        for child in self.children:
            child.update_signal()

        self.update_memory()

        for child in self.children:
            curr_pos = np.array((child.x, child.y), dtype=float)
            curr_val = child.curr_signal

            elite_positions = [pos for pos, _ in self.population_memory]
            elite_scores = [score for _, score in self.population_memory]

            probs = np.array(elite_scores) - min(elite_scores)
            probs = probs / probs.sum() if probs.sum() != 0 else np.ones(len(probs)) / len(probs)

            xe1 = np.array(elite_positions[np.random.choice(len(probs), p=probs)])
            xe2 = np.array(elite_positions[np.random.choice(len(probs), p=probs)])

            r1, r2 = np.random.rand(2)
            new_pos = curr_pos + w * (r1 * (xe1 - curr_pos) + r2 * (xe2 - curr_pos))

            # Constrain movement to max 1 unit per axis
            new_pos = self.move_toward((child.x, child.y), new_pos, child.step_size)

            new_x, new_y = new_pos
            old_signal = curr_val
            child.x, child.y = new_x, new_y
            child.update_signal()
            new_signal = child.curr_signal

            delta_f = new_signal - old_signal
            if delta_f < 0 and np.random.rand() >= np.exp(delta_f / self.T):
                child.x, child.y = int(curr_pos[0]), int(curr_pos[1])  # Revert move

        self.curr_signal = max(c.best_signal for c in self.children)
        self.max_signal = max(self.max_signal, self.curr_signal)

    def move_toward(self, current, target, step_size=1):
        x, y = current
        tx, ty = target

        dx = int(np.clip(round(tx - x), -step_size, step_size))
        dy = int(np.clip(round(ty - y), -step_size, step_size))

        return x + dx, y + dy

    def update_memory(self):
        for child in self.children:
            pos = (child.x, child.y)
            signal = child.curr_signal
            updated = False

            for i, (mem_pos, mem_score) in enumerate(self.population_memory):
                if pos == mem_pos:
                    if signal > mem_score:
                        self.population_memory[i] = (pos, signal)
                    updated = True
                    break

            if not updated:
                self.population_memory.append((pos, signal))
