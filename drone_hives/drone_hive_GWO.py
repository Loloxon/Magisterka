import random

import numpy as np

from drone_GWO import DroneGWO


class DroneHiveGWO:
    def __init__(self, starting_positions: list, color="black", params_id=-1, id=-1, conf=None):
        self.divider = 3

        self.children = [DroneGWO(starting_position, color, params_id, id * len(starting_positions) + i)
                         for i, starting_position in enumerate(starting_positions)]
        # self.children = [DroneGWO((random.randint(1, conf.map_size-1), random.randint(1, conf.map_size)),
        #                           color, params_id, id * len(starting_positions) + i)
        #                  for i, starting_position in enumerate(starting_positions)]

        # self.already_visited: list[tuple] = [(starting_position, i) for i, starting_position in
        #                                      enumerate(starting_positions)]
        self.already_visited: list[tuple] = [
            (starting_position[0] // self.divider, starting_position[0] // self.divider) for starting_position in
            starting_positions]

        self.color = color
        self.params_id = params_id
        self.id = id

        self.max_signal = 0
        self.curr_signal = None

        assert conf is not None
        self.conf = conf

        self.alpha, self.beta, self.delta = ((self.conf.map_size/2, self.conf.map_size/2),
                                             (self.conf.map_size/2, self.conf.map_size/2),
                                             (self.conf.map_size/2, self.conf.map_size/2))
        self.alpha_score, self.beta_score, self.delta_score = 0, 0, 0

    def set_values(self, canvas, map, GUI, master):
        for child in self.children:
            child.set_values(canvas, map, GUI, master)

    def draw(self):
        for child in self.children:
            child.draw()

    def do_move(self,t, max_iter):

        for i, child in enumerate(self.children):
            score = child.curr_signal
            if score is None:
                pass
            elif score > self.alpha_score:
                self.alpha_score, self.beta_score, self.delta_score = score, self.alpha_score, self.beta_score
                self.alpha, self.beta, self.delta = (child.x, child.y), self.alpha, self.beta
            elif score > self.beta_score:
                self.beta_score, self.delta_score = score, self.beta_score
                self.beta = (child.x, child.y)
            elif score > self.delta_score:
                self.delta_score = score
                self.delta = (child.x, child.y)

        a = 2 - t * (2 / max_iter)  # Zmniejszanie współczynnika eksploracji
        # a = 2
        for i, child in enumerate(self.children):
            A1, A2, A3 = 2 * a * np.random.rand(2) - a, 2 * a * np.random.rand(2) - a, 2 * a * np.random.rand(
                2) - a
            C1, C2, C3 = 2 * np.random.rand(2), 2 * np.random.rand(2), 2 * np.random.rand(2)

            D_alpha, D_beta, D_delta = (np.abs(C1 * np.array(self.alpha) - np.array((child.x, child.y))),
                                        np.abs(C2 * np.array(self.beta) - np.array((child.x, child.y))),
                                        np.abs(C3 * np.array(self.delta) - np.array((child.x, child.y))))
            X1, X2, X3 = (np.array(self.alpha) - A1 * D_alpha,
                          np.array(self.beta) - A2 * D_beta,
                          np.array(self.delta) - A3 * D_delta)
            new_pos = (X1 + X2 + X3) / 3  # Nowa pozycja wilka
            # print(child.x, child.y, new_pos, self.move_toward((child.x, child.y), new_pos))
            # child.x, child.y = new_pos[0], new_pos[1]
            child.x, child.y = self.move_toward((child.x, child.y), new_pos)
            child.curr_signal = child.signal_received()
            child.max_signal = max(child.max_signal, child.curr_signal)
        # print()
        self.curr_signal = self.alpha_score
        self.max_signal = max(self.max_signal, self.curr_signal)

    def move_toward(self, current, target):
        x, y = current
        a, b = target

        # Determine the new position by moving at most 1 step in either direction
        new_x = x + (1 if a > x else -1 if a < x else 0)
        new_y = y + (1 if b > y else -1 if b < y else 0)

        return (new_x, new_y)

        # if t % 10 == 0:
        #     print(f"Iteracja {t}: Najlepsze rozwiązanie {alpha} z wynikiem {self.alpha_score}")

    # print("Optymalne rozwiązanie:", alpha, "Wartość funkcji:", alpha_score)
    # max_signal_tmp = 0
    # curr_signal_tmp = 0
    # for i, child in enumerate(self.children):
    #     counter = 0
    #     visited = True
    #     while counter < 4 and visited:
    #         visited = False
    #         if (child.get_position()[0]//self.divider, child.get_position()[1]//self.divider) in self.already_visited:
    #             visited = True
    #
    #         # for visited_place, id in self.already_visited:
    #         #     if self.overlap(child.target_position(), visited_place, id == i):
    #         #         visited = True
    #
    #         # print("Taboo!")
    #             child.d_x, child.d_y = next_direction(child.d_x, child.d_y)
    #             counter += 1
    #
    #     child.do_move()
    #     max_signal_tmp += child.max_signal
    #     curr_signal_tmp += child.curr_signal
    #
    #     # self.already_visited.append((child.get_position(), i))
    #     self.already_visited.append((child.get_position()[0]//self.divider, child.get_position()[1]//self.divider))
    #
    # self.max_signal = max_signal_tmp / len(self.children)
    # self.curr_signal = curr_signal_tmp / len(self.children)

    # # Definicja funkcji celu (np. testowa funkcja Rastrigina)
    # def objective_function(position):
    #     x, y = position
    #     return 20 + x**2 + y**2 - 10*(np.cos(2*np.pi*x) + np.cos(2*np.pi*y))

    # # Parametry GWO
    # num_wolves = 10
    # dim = 2
    # max_iter = 100
    # bounds = [-5, 5]  # Przedział przeszukiwania
    #
    # # Inicjalizacja populacji
    # wolves = np.random.uniform(bounds[0], bounds[1], (num_wolves, dim))
    # alpha, beta, delta = np.zeros(dim), np.zeros(dim), np.zeros(dim)
    # alpha_score, beta_score, delta_score = float("inf"), float("inf"), float("inf")

    # Algorytm GWO
    # for t in range(max_iter):
