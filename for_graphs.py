import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt


def draw_plots(
    filenames, graph_names, names, extension="svg"
):
    graph_title, file_title = names
    output_file_name = graph_title

    all_means = []
    all_stds = []
    all_iterations = []
    all_algorithms = []
    all_colors = []
    all_styles = []

    # --- Load all files in new format ---
    for filename in filenames:
        # Load numeric data (skip header row)
        data = np.genfromtxt(filename, delimiter=";", skip_header=1)

        # Iterations = first column
        iterations = data[:-1, 0]

        # Values = mean and std across all other columns
        if data.shape[1] > 1:
            mean_vals = np.mean(data[:-1, 1:], axis=1, keepdims=True)
            std_vals = np.std(data[:-1, 1:], axis=1, keepdims=True)
        else:
            mean_vals = data[:-1, 0:1]
            std_vals = np.zeros_like(mean_vals)

        # --- Parse algorithm name + color from filename ---
        algorithm_tag = filename.split("_")[-1].replace(".csv", "")
        algorithms = [algorithm_tag]

        if algorithm_tag == "GWO":
            color = "red"
        elif algorithm_tag == "PSO":
            color = "blue"
        elif algorithm_tag == "PSA":
            color = "limegreen"
        else:
            color = "black"

        colors = {algorithm_tag: color}

        # --- Parse drone number for style ---
        drones_no = filename.split("_")[-2].replace(".csv", "")[-1]

        if drones_no == "2":
            style = {"linestyle": (0, (7, 7))}
        elif drones_no == "4":
            style = {"linestyle": "--"}
        elif drones_no == "8":
            style = {"linestyle": "-"}
        else:
            style = {"linestyle": "solid"}

        styles = {drones_no: style}

        all_iterations.append(iterations)
        all_means.append(mean_vals)
        all_stds.append(std_vals)
        all_algorithms.append(algorithms)
        all_colors.append(colors)
        all_styles.append(styles)

    # --- Trim all series to the same last index where not all means == 1.0 ---
    # max_idx = -1
    # for idx in range(len(all_iterations)):
    #     iterations = all_iterations[idx]
    #     means = all_means[idx]
    #     stds = all_stds[idx]
    #
    #     # Find the last index where not all means are 1.0
    #     mask = np.all(means != 1.0, axis=1)
    #     if np.any(mask):
    #         last_idx = np.max(np.where(mask)[0])  # last iteration to keep
    #     else:
    #         last_idx = -1  # all points are max, nothing to keep
    #     max_idx = max(max_idx, last_idx)
    # if max_idx != -1:
    #     max_idx = min(max_idx+200, len(all_iterations[0]) - 1)  # add some extra points for context
    #
    # for idx in range(len(all_iterations)):
    #     iterations = all_iterations[idx]
    #     means = all_means[idx]
    #     stds = all_stds[idx]
    #     # Trim all series to that index
    #     all_iterations[idx] = iterations[:max_idx + 1]
    #     all_means[idx] = means[:max_idx + 1, :]
    #     all_stds[idx] = stds[:max_idx + 1, :]

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(14, 5))

    for file_idx, (iterations, means, stds, algorithms, colors, styles, graph_name) in enumerate(
        zip(all_iterations, all_means, all_stds, all_algorithms, all_colors, all_styles, graph_names)
    ):
        style = styles[graph_name[0]]
        for i, algo in enumerate(algorithms):
            if algo == "DroneHiveGWO":
                algorithm_name = "GWO"
            elif algo == "DroneHivePSO":
                algorithm_name = "PSO"
            elif algo == "DroneHivePSA":
                algorithm_name = "PSA"
            else:
                algorithm_name = algo

            if graph_name == "2 drones":
                graph_name2 = "8 dronów"
            elif graph_name == "4 drones":
                graph_name2 = "16 dronów"
            elif graph_name == "8 drones":
                graph_name2 = "32 drony"
            else:
                graph_name2 = graph_name

            # plot mean line
            ax.plot(
                iterations,
                means[:, i],
                label=f"{algorithm_name} - {graph_name2}",
                color=colors[algo],
                linestyle=style["linestyle"],
                linewidth=1,
            )

            # Std shading
            ax.fill_between(
                iterations,
                means[:, i] - stds[:, i],
                means[:, i] + stds[:, i],
                color=colors[algo],
                alpha=0.1,
            )

            # Top and bottom boundary lines
            ax.plot(iterations, means[:, i] - stds[:, i],
                    color=colors[algo], linestyle=style["linestyle"], linewidth=0.6, alpha=0.4)
            ax.plot(iterations, means[:, i] + stds[:, i],
                    color=colors[algo], linestyle=style["linestyle"], linewidth=0.6, alpha=0.4)

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Value")
    ax.set_title(graph_title)
    ax.grid(True)
    plt.tight_layout()

    handles, labels = ax.get_legend_handles_labels()
    # labels = [labels[0],labels[3],labels[6],labels[1],labels[4],labels[7],labels[2],labels[5],labels[8]]
    # handles = [handles[0],handles[3],handles[6],handles[1],handles[4],handles[7],handles[2],handles[5],handles[8]]
    ax.legend(handles, labels)

    # --- Save ---
    path = "assets\\graphs_v3_new"
    output_file_name = output_file_name.replace('"', "'")
    plt.savefig(f"{path}\\{file_title}.{extension}", format=extension, dpi=300)
    plt.close(fig)
    print("Saved:", f"{output_file_name}.{extension} at {path}\\{file_title}.{extension}")



def last_row_latex_table_old(groups, k, map_name, variants):
    # --- Print LaTeX table ---
    print("\\begin{table}[h!]")
    print("\\centering")
    print(
        "\\begin{tabular}{ |p{4.2cm}||p{0.8cm}|p{0.8cm}|p{0.8cm}|p{0.8cm}|p{0.8cm}|p{0.8cm}|p{0.8cm}|p{0.8cm}|p{0.8cm}|  }")
    print("\\hline")
    print("\\multicolumn{10}{|c|}{Liczba iteracji potrzebna do znalezienia źródła sygnału} \\\\")
    print("\\hline")
    print("Algorytm & \\multicolumn{3}{|c|}{GWO} & \\multicolumn{3}{|c|}{PSA} & \\multicolumn{3}{|c|}{PSO} \\\\")
    print("\\hline")
    print(f"Liczba użytych dronów & 8 & 16 & 32 & 8 & 16 & 32 & 8 & 16 & 32 \\\\")
    print("\\hline")
    print("\\hline")

    for i, csv_files in enumerate(groups):
        rows = []
        labels = [f.split("/")[-1].replace(".csv", "") for f in csv_files]  # file names as labels

        for file in csv_files:
            data = np.genfromtxt(file, delimiter=";", skip_header=1)
            last_row = data[-1, 1:]  # skip first column (iteration)
            rows.append(last_row)

        rows = np.vstack(rows)  # shape: (num_files, num_values)
        #if any of values=-inf then set whole row to -inf when calculating mean and str
        mean_vals = np.array([np.mean(row[row != float('-inf')]) if np.any(row != float('-inf')) else float('-inf') for row in rows])
        std_vals = np.array([np.std(row[row != float('-inf')]) if np.any(row != float('-inf')) else float('-inf') for row in rows])


        for k in range(3):
            mean_vals_part = mean_vals[k*3:(k+1)*3]
            std_vals_part = std_vals[k*3:(k+1)*3]

            # mean ± std row
            stats_str = ""

            best_val = float('inf')
            for m, s in zip(mean_vals_part, std_vals_part):
                if not np.isneginf(m):
                    best_val = min(best_val, m)
            for m, s in zip(mean_vals_part, std_vals_part):
                if np.isneginf(m):
                    stats_str += "- & - & "
                else:
                    if m == best_val:
                        stats_str += "\\textbf{\\underline{" + str(int(m)) +"}} &"+ f" $\\pm$ {int(s)}& "
                    else:
                        stats_str += f"{int(m)} & $\\pm$ {int(s)} & "

            print(f"{variants[i]} & {stats_str[:-2]}\\\\")


    print("\\hline")
    print("\\end{tabular}")
    print("\\caption{Porównianie TTD dla scenariusza z użyciem wariantów " + map_name + ".}")
    print("\\label{table:" + str(k) + "}")
    print("\\end{table}")
    print()
    print()


def last_row_latex_table(groups, n, map_name, variants):
    # --- Print LaTeX table ---
    print("""
\\begin{table}[H]\\centering
\\ra{1.3}
\\begin{tabular}{@{}rrlcrlcrl@{}}\\toprule
& \\multicolumn{2}{c}{$GWO$} & \\phantom{abc}& \\multicolumn{2}{c}{$PSA$} & \\phantom{abc} & \\multicolumn{2}{c}{$PSO$}\\\\
\\cmidrule{2-3} \\cmidrule{5-6} \\cmidrule{8-9}
& $l.\\ iter.$ & $SD$ &&  $l.\\ iter.$ & $SD$ &&   $l.\\ iter.$ & $SD$\\\\
\\midrule""")

    for i, csv_files in enumerate(groups):
        rows = []
        labels = [f.split("/")[-1].replace(".csv", "") for f in csv_files]  # file names as labels

        for file in csv_files:
            data = np.genfromtxt(file, delimiter=";", skip_header=1)
            last_row = data[-1, 1:]  # skip first column (iteration)
            rows.append(last_row)

        rows = np.vstack(rows)  # shape: (num_files, num_values)
        #if any of values=-inf then set whole row to -inf when calculating mean and str
        mean_vals = np.array([np.mean(row[row != float('-inf')]) if np.any(row != float('-inf')) else float('-inf') for row in rows])
        std_vals = np.array([np.std(row[row != float('-inf')]) if np.any(row != float('-inf')) else float('-inf') for row in rows])

        print("$W_1$\\\\")
        for k in range(3):
            mean_vals_part = mean_vals[k*3:(k+1)*3]
            std_vals_part = std_vals[k*3:(k+1)*3]

            # mean ± std row
            stats_str = ""

            best_val = float('inf')
            for m, s in zip(mean_vals_part, std_vals_part):
                if not np.isneginf(m):
                    best_val = min(best_val, m)
            for m, s in zip(mean_vals_part, std_vals_part):
                if np.isneginf(m):
                    stats_str += "- & - && "
                else:
                    if m == best_val:
                        stats_str += "\\textbf{\\underline{" + str(int(m)) +"}} &"+ f" $\\pm$ {np.round(s, 1)}&& "
                    else:
                        stats_str += f"{int(m)} & $\\pm$ {int(s)} && "

            print(f"$d={8*2**k}$ & {stats_str[:-3]}\\\\")


    print("""\\bottomrule
\\end{tabular}
\\caption{Porównianie TTD dla scenariusza z użyciem wariantów """ + map_name + """.}
\\label{table:""" +str(n)+ """}
\\end{table}""")
    print()


maps = ["baseline", "hell", "góry", "krakow", "fuerta"]
variants = ["_std", "_zmd_out", "_zmd_out_moved"]
map_names = ["mapy bazowej", "mapy bez zakłóceń, wyłącznie z przeszkodami", "mapy względnie zbalansowanej", "alternatywnej mapy względnie zbalansowanej", "mapy z wieloma zakłóceniami i odbiciami"]

for k, map in enumerate(maps):
    # if map in ["baseline", "fuerta"]:
        filenames_for_table = []
        for variant in variants:
            folder_path = "assets/logs_v3/log_avg_current_sig_" + map + variant + "/"
            filenames = [folder_path + type + ".csv" for type in ["2_GWO", "2_PSO", "2_PSA",
                                                         "4_GWO", "4_PSO", "4_PSA", "8_GWO", "8_PSO", "8_PSA"]]
            filenames_for_table.append(filenames)
            #
            # draw_plots(filenames, ["2 drones", "2 drones", "2 drones",
            #                                                                 "4 drones", "4 drones", "4 drones",
            #                                                                 "8 drones", "8 drones", "8 drones"],
            #            ("Średnia Obecnych Sygnałów w zależności of liczby iteracji", f"ACS_{map}{variant}"))
            #
            # folder_path = "assets/logs_v3/log_max_count_______" + map + variant + "/"
            # filenames = [folder_path + type + ".csv" for type in ["2_GWO", "2_PSO", "2_PSA",
            #                                              "4_GWO", "4_PSO", "4_PSA", "8_GWO", "8_PSO", "8_PSA"]]
            # draw_plots(filenames, ["2 drones", "2 drones", "2 drones",
            #                                                     "4 drones", "4 drones", "4 drones",
            #                                                     "8 drones", "8 drones", "8 drones"],
            #            ("DRC w zależności od liczby iteracji", f"MC_{map}{variant}"))
            #
            # folder_path = "assets/logs_v3/log_avg_max_sig_____" + map + variant + "/"
            # filenames = [folder_path + type + ".csv" for type in ["2_GWO", "2_PSO", "2_PSA",
            #                                                         "4_GWO", "4_PSO", "4_PSA","8_GWO", "8_PSO", "8_PSA"]]
            # draw_plots(filenames, ["2 drones", "2 drones", "2 drones",
            #                                                                 "4 drones", "4 drones", "4 drones",
            #                                                                 "8 drones", "8 drones", "8 drones"],
            #            ("BSFS w zależności od liczby iteracji", f"AMS_{map}{variant}"))

        last_row_latex_table(filenames_for_table, k, map_names[k], ["Wariant standardowy", "Wariant przeskalowany", "Wariant przeskalowany i przesunięty"])


# draw_3_at_once_but_in_one_graph_cropped(filenames1, ["2 drones", "2 drones", "2 drones"], ("Average current signal", "log_avg_current_sig_baseline_std_GWO"))
# draw_3_at_once_but_in_one_graph_cropped(filenames2, ["2 drones", "2 drones", "2 drones"], ("Max signal", "log_avg_max_sig_____baseline_std_GWO"))
# draw_3_at_once_but_in_one_graph_cropped(filenames3, ["2 drones", "2 drones", "2 drones"], ("BSFS", "BSFS_____baseline_std_GWO"))
