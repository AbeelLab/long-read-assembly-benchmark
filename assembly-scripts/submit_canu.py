import time
import os

technologies = [{"name": "ont", "arg": "-nanopore"},
                {"name": "pacbio", "arg": "-pacbio"},
                {"name": "pacbio_hifi", "arg": "-pacbio-hifi"}]

lengths = ["s0", "s1", "s2", "s3"]

genomes = [{"name": "pfalciparum", "length": "small", "threads": 8, "size": 23},
           {"name": "scerevisiae", "length": "small", "threads": 8, "size": 12},
           {"name": "athaliana", "length": "medium", "threads": 16, "size": 135},
           {"name": "celegans", "length": "medium", "threads": 16, "size": 100},
           {"name": "dmelanogaster", "length": "medium", "threads": 16, "size": 144},
           {"name": "trubripes", "length": "medium-long", "threads": 20, "size": 384}]

path_to_simulated_reads = "[path]"
path_to_assembly = "[path]"

for genome in genomes:
    print("\nAssembling " + genome["name"])
    print("---")
    
    for technology in technologies:
        print("Reads: " + technology["name"])

        for length in lengths:
            print("Length: " + length)

            read_file = path_to_simulated_reads + genome["name"] \
                + "_" + technology["name"] \
                + "_" + length \
                + ".fastq.gz"

            output_dir = path_to_assembly + genome["name"] \
                + "_" + technology["name"] \
                + "_" + length

            script_name = "canu_assemble_" \
                + genome["name"] \
                + "_" + technology["name"] \
                + "_" + length  + ".sbatch"

            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters/canu_" + genome["length"] + ".txt", "r")
            script.write(sbatch_parameters.read())

            canu_command = "canu-2.2/bin/canu"

            script.write("\n cd " + output_dir + " && rm -r * \n ")

            srun_line = "srun " + canu_command + " useGrid=false -p assembly " \
                + "genomeSize=" + str(genome["size"]) + "m " \
                + technology["arg"] + " " + read_file \
                + " MaxThreads=" + str(genome["threads"]) \
                + " -d " + output_dir

            script.write(srun_line)
            script.close()

            # Run script
            os.system("sbatch " + script_name)
            time.sleep(2)
