# import numpy as np
# import random
# from collections import OrderedDict
# from drone_PSA import DronePSA
#
#
# class DroneHivePSA:
#     """
#     Population Simulated Annealing (PSA), step-limited (step_size=1).
#     - Central memory: archive of best positions (no PSO velocities / pulls).
#     - Proposal: local neighbor step; optionally biased toward archive (exploitation increases as T cools).
#     - Acceptance: Metropolis criterion with temperature schedule.
#     """
#
#     def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
#         self.children = [DronePSA(starting_position, color, params_id, id * len(starting_positions) + i)
#                          for i, starting_position in enumerate(starting_positions)]
#
#         self.color = color
#         self.params_id = params_id
#         self.id = id
#         assert conf is not None
#         self.conf = conf
#
#         # Central archive: list of (pos, score). Keep top-K unique positions.
#         self.archive = []              # [( (x, y), score ), ...]
#         self.archive_capacity = max(10, len(self.children) * 3)
#
#         # SA temperature (log cooling)
#         self.T0 = 100.0
#         self.T = self.T0
#
#         self.iteration = None
#         self.max_iter = None
#
#         # Metrics
#         self.max_signal = float('-inf')
#         self.curr_signal = None
#         self.max_signal_for_metric = []
#         self.max_count_for_metric = []
#         self.curr_signal_for_metric = []
#         self.first_iteration_hit_max = float('-inf')
#         self.visited_max_signal = 0
#         self.total_max_signal = conf.max_signal
#         self.can_end = False
#
#     # --- Framework hooks ---
#     def set_values(self, canvas, map, GUI, master):
#         for child in self.children:
#             child.set_values(canvas, map, GUI, master)
#
#     def draw(self):
#         for child in self.children:
#             if not self.conf.drones_hidden:
#                 child.draw()
#
#     # --- Core loop ---
#     def do_move(self, t, max_iter):
#         self.iteration = t
#         self.max_iter = max_iter
#
#         # Logarithmic cooling; T never hits zero to avoid division issues
#         # T(t) = T0 / log(t + c), with c >= e to keep denominator >= 1 initially
#         c = 2.718281828  # ~e
#         self.T = self.T0 / np.log(t + c)
#
#         # Update signals for all, refresh archive
#         for child in self.children:
#             child.update_signal()
#         self._update_archive()
#
#         visited_max_signal = 0
#
#         # Exploitation probability increases as temperature cools
#         # p_exploit ~ 1 - T/T0 (clamped to [0, 0.95])
#         p_exploit = float(np.clip(1.0 - (self.T / self.T0), 0.0, 0.95))
#
#         for child in self.children:
#             old_signal = child.curr_signal
#             cx, cy = child.x, child.y
#
#             # --- Propose a neighbor move (4-neighborhood), optionally biased toward archive ---
#             dx, dy = self._propose_step((cx, cy), p_exploit)
#
#             # Try to move; if blocked by map, skip this proposal (no move)
#             moved = child.move(dx, dy)
#             if moved:
#                 child.update_signal()
#                 new_signal = child.curr_signal
#
#                 # --- Metropolis acceptance ---
#                 delta = new_signal - old_signal
#                 if delta >= 0:
#                     accept = True
#                 else:
#                     # exp(delta / T) with protection against T ~ 0
#                     prob = np.exp(delta / max(self.T, 1e-12))
#                     accept = (np.random.rand() < prob)
#
#                 if not accept:
#                     # Revert move
#                     child.move(-dx, -dy)
#                     child.update_signal()  # restore curr_signal
#
#             # Track if this agent has already seen the global max
#             if child.max_signal == self.total_max_signal:
#                 visited_max_signal += 1
#
#         # Metrics
#         self.curr_signal = max(c.best_signal for c in self.children)
#         self.visited_max_signal = visited_max_signal
#         self.max_signal = max(self.max_signal, self.curr_signal)
#
#         self.max_signal_for_metric.append(np.round(self.max_signal / self.total_max_signal, 4))
#         self.max_count_for_metric.append(np.round(self.visited_max_signal / len(self.children), 4))
#         self.curr_signal_for_metric.append(np.round(np.mean([c.curr_signal for c in self.children]) / self.total_max_signal, 4))
#
#         if self.first_iteration_hit_max == float('-inf') and self.max_signal == self.total_max_signal:
#             self.first_iteration_hit_max = t
#         if self.curr_signal_for_metric[-1] == 1.0:
#             self.can_end = True
#
#     # --- Helpers ---
#     def _update_archive(self):
#         """
#         Insert/update current agent positions in central archive and keep only the top-K unique.
#         """
#         # Collect (pos, score)
#         candidates = list(self.archive)
#         for child in self.children:
#             candidates.append(((child.x, child.y), child.curr_signal))
#
#         # Keep best score per unique position
#         best_per_pos = {}
#         for pos, score in candidates:
#             if (pos not in best_per_pos) or (score > best_per_pos[pos]):
#                 best_per_pos[pos] = score
#
#         # Sort by score desc, keep top-K
#         sorted_items = sorted(best_per_pos.items(), key=lambda kv: kv[1], reverse=True)
#         self.archive = [(pos, score) for pos, score in sorted_items[: self.archive_capacity]]
#
#     def _propose_step(self, current_xy, p_exploit):
#         """
#         Propose a single-step move (dx, dy) in {-1, 0, +1} with |dx|+|dy|==1.
#         With probability p_exploit, bias step toward a random archive elite (if available).
#         Otherwise random 4-neighborhood step.
#         """
#         cx, cy = current_xy
#
#         # 4-neighborhood
#         neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
#
#         if self.archive and (np.random.rand() < p_exploit):
#             # Pick a random elite and step one cell toward it
#             elite_pos, _ = random.choice(self.archive)
#             ex, ey = elite_pos
#
#             dx = 0 if ex == cx else (1 if ex > cx else -1)
#             dy = 0 if ey == cy else (1 if ey > cy else -1)
#
#             # If both axes differ, randomly choose which axis to move along to keep step_size=1
#             if dx != 0 and dy != 0:
#                 if np.random.rand() < 0.5:
#                     dy = 0
#                 else:
#                     dx = 0
#
#             # If elite equals current (rare), fall back to random neighbor
#             if dx == 0 and dy == 0:
#                 dx, dy = random.choice(neighbors)
#         else:
#             dx, dy = random.choice(neighbors)
#
#         return dx, dy

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

        self.population_memory = [((child.x, child.y), 0) for child in self.children]

        self.T0 = 100
        self.T = self.T0
        self.iteration = None
        self.max_iter = None

        self.w_max = 1.25
        self.w_min = 0.25

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

        visited_max_signal = 0
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

            if child.max_signal == self.total_max_signal:
                visited_max_signal += 1

        self.curr_signal = max(c.best_signal for c in self.children)
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

    def update_memory(self):
        for i, child in enumerate(self.children):
            pos = (child.x, child.y)
            signal = child.curr_signal
            updated = False

            # for i, (mem_pos, mem_score, child_id) in enumerate(self.population_memory):
            #     if pos == mem_pos:
            #         if signal > mem_score:
            #             self.population_memory[i] = (pos, signal)
            #         updated = True
            #         break
            #
            # if not updated:
            #     self.population_memory.append((pos, signal))
            self.population_memory.append((pos, signal))

            # if signal > self.population_memory[i][1]:
            #     self.population_memory[i] = (pos, signal)

        #keep only 100 max values per child from memory
        self.population_memory = sorted(self.population_memory, key=lambda x: x[1], reverse=True)[:(len(self.children)*100)]
