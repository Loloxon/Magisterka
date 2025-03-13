class Conf:
    def __init__(self):
        self.map_name = "góry"

        self.image_size = 1000
        self.cells_number = 50
        self.map_size = 750

        self.visited_area_radius = 5

        self.cell_size = self.map_size // self.cells_number

        self.drones_starting_margin = self.map_size // 20
        self.drones_starting_per_side = 10
        self.drones_starting_per_point = 4

        self.iterations = 10000
        self.refresh_interval = 10
        self.save_to_file_interval = 5

        self.log_avg_max_sig = 'assets/logs/log_avg_max_sig.txt'
        self.log_max_count = 'assets/logs/log_max_count.txt'
        self.log_avg_current_sig = 'assets/logs/log_avg_current_sig.txt'

        self.drones_parameters = fill_drones_parameters()

        self.drone_hives_parameters = fill_drone_hives_parameters()

        self.max_signal = None


def fill_drones_parameters():
    drones_parameters = []

    drones_parameters.append(("DroneRandom", "purple"))
    # drones_parameters.append(("DroneAnnealing", "blue", 1, 0.4, 1))
    # drones_parameters.append(("DroneNoDescent", "orange", 0.75))

    # # descent_probabs = [0, 0.25, 0.5, 0.75, 0.85]
    # descent_probabs = [0.25, 0.5, 0.75]
    # # colors = ["blue", "green", "orange", "red", "yellow"]
    # colors = ["orange", "orange", "orange"]
    # # all_ignore_value_step_nums = [
    # #     [1, 2, 4],
    # #     [1, 2, 4],
    # #     [1, 2, 4],
    # #     [1, 2, 4],
    # #     [1, 2, 4]
    # # ]
    # all_ignore_value_step_nums = [
    #     [4],
    #     [4],
    #     [4]
    # ]
    #
    # for color, descent_probab, ignore_value_step_nums in zip(colors, descent_probabs, all_ignore_value_step_nums):
    #     for ignore_value_step_num in ignore_value_step_nums:
    #         drones_parameters.append(
    #             ("DroneNoDescent", "orange", descent_probab, ignore_value_step_num))
    #
    #
    #
    # start_temps = [1]
    # temp_muls = [0.9, 0.4]
    # # temp_muls = [0.9, 0.4, 0.2]
    #
    # epoch_sizes = [10, 1]
    # ignore_value_step_num = -1.1
    # for start_temp in start_temps:
    #     for temp_mul in temp_muls:
    #         for epoch in epoch_sizes:
    #             drones_parameters.append(
    #                 ("DroneAnnealing", "blue", start_temp, temp_mul, epoch, ignore_value_step_num))
    #
    # drones_parameters.append(("DroneAnnealing", "blue", 100, 0.4, 10, 4))
    # drones_parameters.append(("DroneAnnealing", "blue", 100, 0.4, 1, 4))

    return drones_parameters

def fill_drone_hives_parameters():
    drone_hives_parameters = []

    drone_hives_parameters.append(("DroneHiveRandomTaboo", "green"))
    # drone_hives_parameters.append(("DroneHiveTry1", "yellow"))

    return drone_hives_parameters
