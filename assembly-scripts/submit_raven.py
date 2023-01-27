import time
import os

technologies = [{"name": "ont"},
                {"name": "pacbio"},
                {"name": "pacbio_hifi"}]

lengths = ["s0", "s1", "s2", "s3"]

genomes = [{"name": "pfalciparum", "length": "small", "threads": 8},
           {"name": "scerevisiae", "length": "small", "threads": 8},
           {"name": "athaliana", "length": "medium", "threads": 16},
           {"name": "celegans", "length": "medium", "threads": 16}]
           {"name": "dmelanogaster", "length": "medium", "threads": 16},
           {"name": "trubripes", "length": "medium-long", "threads": 20}]

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

            script_name = "raven_assemble_" \
                + genome["name"] \
                + "_" + technology["name"] \
                + "_" + length  + ".sbatch"

            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters/raven_" + genome["length"] + ".txt", "r")
            script.write(sbatch_parameters.read())

            srun_line = "srun raven -t " + str(genome["threads"]) \
                + " " + read_file \
                + " > " + output_dir + "/assembly.fasta"

            script.write("cd " + output_dir + "\n")
            script.write(srun_line)
            script.close()

            # Run script
            os.system("sbatch " + script_name)
            time.sleep(2)
