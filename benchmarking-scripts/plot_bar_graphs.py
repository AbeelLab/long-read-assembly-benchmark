import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Map values from a range to the radar chart range
def normalize(values, to_range):
    normalized_values = []

    min_value = np.min(values)
    max_value = np.max(values)

    if  np.abs(min_value - max_value) < 1e-9:
        return [to_range[1]] * len(values)

    a = to_range[0]
    b = to_range[1]
    
    for i in range(len(values)):
        x = values[i]
        
        normalized_value = (b - a) * ((x - min_value) / (max_value - min_value)) + a
        normalized_values.append(normalized_value)

    return normalized_values

def plot_line_graph(scores, assemblers, name, colors):
    labels = assemblers

    default = scores[0:5]
    second = scores[5:10]
    third = scores[10:15]
    fourth = scores[15:20]

    width = 0.15

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(6,1.5))
    rects_default = ax.bar(x - width - 0.02, default, width, label='Iteration 1', color=colors, alpha=0.25)#edgecolor="white")
    rects_second = ax.bar(x, second, width, label='Iteration 2', color=colors, alpha=0.50)#hatch="////", edgecolor="white")
    rects_third = ax.bar(x + width + 0.02, third, width, label='Iteration 3', color=colors, alpha=0.75) #hatch="xxx", edgecolor="white")
    rects_fourth = ax.bar(x + 2 * width + 2 * 0.02, fourth, width, label='Iteration 4', color=colors)

    print(labels)
    ax.set_xticks(x, labels)
    ax.set_ylabel('Score')
    plt.ylim(3,10)
    #plt.grid(axis = 'y', linewidth = 0.5)

    plt.savefig(name + ".svg")

prefix = "[path]"

# ---> Concatenate datasets
colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"]
assemblers = ["canu", "flye", "miniasm", "raven", "redbean"]
metrics = ["coverage", "multiplicity", "validity", "ng50", "num_misassemblies", "complete_buscos"]
genomes = ["scerevisiae", "pfalciparum", "athaliana", "celegans", "dmelanogaster", "trubripes"]
technologies =  ["ont", "pacbio", "pacbio_hifi"]
lengths = ["s0", "s1", "s2", "s3"]

for genome in genomes:
    for technology in technologies:
        v = []
        for metric in metrics:
            h = pd.read_csv(prefix + metric + "_" + genome + "_" + technology + "_s0.csv", header=None).to_numpy()
            for length in ["s1", "s2", "s3"]:
                dataset = pd.read_csv(prefix + metric + "_" + genome + "_" + technology + "_" + length + ".csv", header=None).to_numpy()[0]

                h = np.append(h, dataset)
            v.append(list(h))
        
        v = np.array(v)
        np.savetxt(genome + "_" + technology + ".txt", v)

for genome in genomes:
    all_scores = []
    for technology in technologies:
        data = np.loadtxt(genome + "_" + technology + ".txt")
        # Low multiplicity is preferred
        data[1] = -data[1]

        # Validity values close to 1 are preffered
        data[2] = -np.abs(1 - data[2])

        # Low misassembly count in preffered
        data[4] = -data[4]

        if (genome == "athaliana" and technology == "ont") or (genome == "trubripes" and technology == "ont"):
            for j in range(6):
                data[j][15] = np.mean(data[j][:15])
        for j in range(6):
            data[j] = normalize(data[j], [1, 10])
        
        scores = data.mean(axis=0)
        all_scores.append(scores)
        
    all_scores = np.array(all_scores)
    all_scores = all_scores.mean(axis = 0)
    plot_line_graph(all_scores, assemblers, genome, colors)
