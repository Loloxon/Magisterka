import numpy as np
import random
from drone_ACO import DroneACO


class DroneHiveACO:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.children = [DroneACO(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]
        self.conf = conf
        assert conf is not None

        self.color = color
        self.params_id = params_id
        self.id = id

        self.map_size = self.conf.map_size

        # 🔀 Break symmetry in pheromone initialization
        self.pheromone_map = 1.0 + 0.01 * np.random.rand(self.map_size, self.map_size)

        # ⚙️ ACO parameters
        self.alpha = 1     # pheromone influence
        self.beta = 0.7    # signal influence (lowered from 2)
        self.rho = 0.01    # evaporation rate (raised from 0.001)
        self.Q = 100       # pheromone deposit scaling
        self.exploration_rate = 0.2  # 20% chance to explore randomly
        self.max_steps = 50          # longer ant walks per iteration

        self.max_signal = 0
        self.curr_signal = None

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            if not self.conf.drones_hidden:
                child.draw()

    def do_move(self, t, max_iter):
        self.evaporate_pheromones()

        for child in self.children:
            child.reset()

            for _ in range(self.max_steps):  # 🐜 let ants walk longer
                next_step = self.choose_next_move(child)
                if next_step is None:
                    break
                dx, dy = next_step
                moved = child.move(dx, dy)
                if not moved:
                    break

            self.deposit_pheromones(child)

        best_ant = max(self.children, key=lambda a: a.total_signal)
        self.curr_signal = best_ant.total_signal
        self.max_signal = max(self.max_signal, self.curr_signal)

    def evaporate_pheromones(self):
        self.pheromone_map *= (1 - self.rho)

    def deposit_pheromones(self, ant):
        for (x, y) in ant.path:
            if 0 <= x < self.map_size and 0 <= y < self.map_size:
                self.pheromone_map[int(x), int(y)] += self.Q / (1 + len(ant.path))

    def choose_next_move(self, ant):
        x, y = ant.x, ant.y
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        move_scores = []
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.map_size and 0 <= ny < self.map_size):
                continue

            pheromone = self.pheromone_map[int(nx), int(ny)]
            heuristic = ant.signal_received_at(nx, ny)
            if heuristic is None or heuristic <= 0:
                heuristic = 1e-6

            score = (pheromone ** self.alpha) * (heuristic ** self.beta)
            move_scores.append(((dx, dy), score))

        if not move_scores:
            return None

        # 🎲 Exploration vs exploitation
        if random.random() < self.exploration_rate:
            return random.choice([move for move, _ in move_scores])

        total = sum(score for _, score in move_scores)
        probs = [score / total for _, score in move_scores]
        moves = [move for move, _ in move_scores]
        return moves[np.random.choice(len(moves), p=probs)]
