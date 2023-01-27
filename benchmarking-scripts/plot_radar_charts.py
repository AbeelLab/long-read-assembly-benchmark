import kaleido
import plotly.express as px
import pandas as pd
import numpy as np

import plotly.io as pio

import warnings
warnings.filterwarnings("ignore")


# Map values from a range to the radar chart range
# Per technology, per metric
def normalize(values, to_range, minimum, maximum):
    normalized_values = []

    min_value = minimum
    max_value = maximum

    if  np.abs(min_value - max_value) < 1e-9:
        return [to_range[1]] * len(values)

    a = to_range[0]
    b = to_range[1]
    
    for i in range(len(values)):
        x = values[i]
        
        normalized_value = (b - a) * ((x - min_value) / (max_value - min_value)) + a
        normalized_values.append(normalized_value)

    return normalized_values



def plot_radar_chart(assembler_name, dataset_name, dataset, color):
    data = dataset[[assembler]].to_numpy().T[0]
    
    to_plot = pd.DataFrame(dict(
        r=data,
        theta=['Sequence identity',
               'Repeat collapse',
               'Rate of valid sequences',
               'Contiguity',
               'Misassembly count',
               'Gene identification']))

    fig = px.line_polar(to_plot, r='r', theta='theta', color_discrete_sequence=[color], range_r=[0, 10], line_close=True)

    fig.update_traces(fill='toself')

    fig.write_image("legend.svg")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar = dict(radialaxis = dict(range=[0, 10], showticklabels=False, ticks=''), angularaxis = dict(showticklabels=False, ticks='')))
    # Save as .svg
    fig.write_image(assembler + "_" + dataset_name + ".svg")

assemblers = ["canu", "flye", "miniasm", "raven", "wtdbg2"]
colors = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854"]

genomes = ["scerevisiae", "pfalciparum", "athaliana", "celegans", "dmelanogaster", "trubripes"]
technologies = ["ont", "pacbio", "pacbio_hifi"]

# Metrics and corresponding evaluation categories 
metrics = [("coverage", "Sequence identity"),
           ("multiplicity", "Repeat collapse"),
           ("validity", "Rate of valid sequences"),
           ("ng50", "Contiguity"),
           ("num_misassemblies", "Misassembly count"),
           ("complete_buscos", "Gene identification")]

prefix = "[path]"
datasets = []
dataset_names = []

for genome in genomes:
    for technology in technologies:
        datasets.append(pd.read_csv(prefix + genome + "_" + technology + "_s0.csv", header=None, names=assemblers))
        dataset_names.append(genome + "_" + technology)

# Normalize data
ranges = []
validity_range = [0, 0]

for i in range(6):
    ranges.append([float("inf"), float("-inf")])

i = 0
for i, dataset in enumerate(datasets):
    data = dataset.to_numpy()

    # Low multiplicity is preferred
    data[1] = -data[1]

    # Validity values close to 1 are preffered
    temp = data[2].copy()
    print(temp)
    data[2] = -np.abs(1 - data[2])

    # Modify NG50 by division with N50
    f = open("[path]" + dataset_names[i].split("_")[0] + '/n50.txt', 'r')
    n50 = float(f.read())
    data[3] = data[3] / n50

    # Low misassembly count in preffered
    data[4] = -data[4]
    
    for j in range(6):
        for k in range(len(assemblers)):
            if ranges[j][0] > data[j][k]:
                ranges[j][0] = min(ranges[j][0], data[j][k])
                if j == 2:
                    validity_range[0] = temp[k]
            if ranges[j][0] < data[j][k]:    
                ranges[j][1] = max(ranges[j][1], data[j][k])
                if j == 2:
                    validity_range[1] = temp[k]

    i = i + 1
    
for dataset in datasets:
    data = dataset.to_numpy()
    
    for j in range(6):
        data[j] = normalize(data[j], [1, 10], ranges[j][0], ranges[j][1])

i = 0
for assembler in assemblers:
    j = 0

    for dataset in datasets:
        dataset = dataset.head(6)
        print(dataset_names[j])
        average_scores = dataset.mean(axis=0).to_numpy()
        print("Best assembler:", assemblers[np.argmax(average_scores)])
        print("Best score: ", np.max(average_scores))
        
        plot_radar_chart(assembler, dataset_names[j], dataset, colors[i])
        j = j + 1

    i = i + 1
