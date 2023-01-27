import os
import numpy as np
import pandas as pd
import re

from utils import convert_runtime, parse_memory, convert_memory

def main(length):
    genomes = [{"name": "pfalciparum", "arg": "plasmodium_odb10"},
               {"name": "scerevisiae", "arg": "saccharomycetes_odb10"},
               {"name": "athaliana", "arg": "brassicales_odb10"},
               {"name": "celegans", "arg": "nematoda_odb10"},
               {"name": "dmelanogaster", "arg": "diptera_odb10"},
               {"name": "trubripes", "arg": "actinopterygii_odb10"}]
    assemblers = ["canu", "flye", "miniasm", "raven", "wtdbg"]
    technologies = ["ont", "pacbio", "pacbio_hifi"]

    prefix = "[path]"

    metrics = ["complete_buscos"]

    # BUSCO
    print("\nBUSCO\n---")

    for genome in genomes:
        for technology in technologies:
            if technology == "pacbio_hifi" and length == "real":
                continue
            
            filename = "complete_buscos_" + genome["name"] + "_" + technology + "_" + length + ".csv"
            if os.path.exists(filename):
                os.remove(filename)
            busco_file = open(filename, "a+")

            complete_buscos = np.full(len(assemblers), -1.0)
            for i, assembler in enumerate(assemblers):
                directory = prefix + "busco_evaluations/" + genome["name"] + "_" + assembler + "_" + technology + "_" + length + "/"
                inner = assembler + "_" + genome["name"] + "_" + technology + "_" + length
                summary_file = directory + inner + "/" + "short_summary.specific." + genome["arg"] + "." + inner + ".txt"

                if os.path.exists(summary_file):
                    to_parse = open(summary_file, "r")

                    for line in to_parse:
                        if line.strip().startswith("C:"):
                            val = float(line.strip()[2:6].replace("%", ""))

                            complete_buscos[i] = val
                else:
                    print("--- Did not find: " + summary_file)
                    complete_buscos[i] = 0

            np.savetxt(filename, [complete_buscos], delimiter=",", fmt="%1.1f")


    # QUAST
    print("\nQUAST\n---")

    quast_metrics = [{"name": "NG50", "file_name": "ng50", "format": "%i"},
                     {"name": "# misassemblies", "file_name": "num_misassemblies", "format": "%i"}]

    for metric in quast_metrics:
        metrics.append(metric["file_name"])
        for genome in genomes:
            for technology in technologies:
                if technology == "pacbio_hifi" and length == "real":
                    continue
                # Open file to write metric values
                filename = metric["file_name"] + "_" + genome["name"] + "_" + technology + "_" + length + ".csv"
                if os.path.exists(filename):
                    os.remove(filename)
                metric_file = open(filename, "a+")

                metric_values = np.full(len(assemblers), -1.0)
                for i, assembler in enumerate(assemblers):
                    directory = prefix + "quast_evaluations/" + genome["name"] + "_" + assembler + "_" + technology + "/"
                    if os.path.exists(directory + "transposed_report.tsv"):
                        df = pd.read_csv(directory + "transposed_report.tsv", sep="\t", header=0)

                        y = df[metric["name"]].to_numpy()
                        if length != "real" and len(y) > int(length[1]):
                            val = y[int(length[1])] # select corresponding row
                        elif length != "real":
                            val = -1
                        elif length == "real":
                            val = y[0]

                        if not val == "-":
                            metric_values[i] = float(val)
                        else:
                            metric_values[i] = 0
                            print("--Did not find: " + directory)

                np.savetxt(filename, [metric_values], delimiter=",", fmt=metric["format"])


    # COMPASS
    print("\nCOMPASS\n---")
    compass_metrics = [{"name": "Coverage (by summing \"island\" lengths)", "file_name": "coverage", "format": "%1.3f"},
                       {"name": "Multiplicity", "file_name": "multiplicity", "format": "%1.3f"},
                       {"name": "Validity", "file_name": "validity", "format": "%1.3f"}]

    for metric in compass_metrics:
        metrics.append(metric["file_name"])
        for genome in genomes:
            for technology in technologies:
                if technology == "pacbio_hifi" and length == "real":
                    continue
                # Open file to write metric values
                filename = metric["file_name"] + "_" + genome["name"] + "_" + technology + "_" + length +  ".csv"
                if os.path.exists(filename):
                    os.remove(filename)
                metric_file = open(filename, "a+")

                metric_values = np.full(len(assemblers), -1.0)
                for i, assembler in enumerate(assemblers):
                    directory = prefix + "compass_evaluations/" + genome["name"] + "_" + assembler + "_" + technology + "_" + length + "/"

                    if os.path.exists(directory + "0stats.txt"):
                        to_parse = open(directory + "0stats.txt", "r")

                        for line in to_parse:
                            if line.strip().startswith(metric["name"]):
                                numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
                                rx = re.compile(numeric_const_pattern, re.VERBOSE)
                                if len(rx.findall(line.strip())) > 0:
                                    if metric["name"] == "Coverage (by summing \"island\" lengths)" and assembler == "flye" and genome["name"] == "trubripes": print("!!! ", val)
                                    val = float(rx.findall(line.strip())[0])
                                    metric_values[i] = val
                                else:
                                    print("Something went wrong: " + directory)
                                    metric_values[i] = 0

                    else:
                        print("--- Did not find: " + directory + "0stats.txt")
                        metric_values[i] = 0

                print(metric_values)
                np.savetxt(filename, [metric_values], delimiter=",", fmt="%1.3f")

    # Merge results
    for genome in genomes:
        for technology in technologies:
            if length == "real" and technology == "pacbio_hifi":
                continue
            
            filename = genome["name"] + "_" + technology + "_" + length + ".csv"
            if os.path.exists(filename):
                os.remove(filename)
            for metric in metrics:
                f = metric["name"] + "_" + genome["name"] + "_" + technology + "_" + length + ".csv"
                x = np.loadtxt(f, delimiter=",")

                with open(filename, "a+") as new_file:
                    np.savetxt(new_file, [x], delimiter=",", fmt=metric["format"])
                    new_file.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--length',  nargs='?', default=None, help='Either s0, s1, s2 or s3')
    args = parser.parse_args()
    main(args.length)
