import time
import os

# Simulation models
models = [{"name": "ont_human2019", "technology": "ont", "identity": "91.3,98.8,2.9", "read_lengths": ["12100,17100", "25000,35000", "35000,49000", "75000,105000"], "other": ""},
          {"name": "pacbio_human2019", "technology": "pacbio", "identity": "89.4,94.7,2.7", "read_lengths": ["15700,14400", "25000,22500", "35000,31500", "75000,67500"], "other": ""}]
          {"name": "pacbio_hifi_human2022", "technology": "pacbio_hifi","identity": "99.7,100.0,0.3", "read_lengths": ["20700,2500", "25000,3000", "35000,4200", "75000,9000"], "other": "--glitches 100000,25,25 --junk_reads 0.01 --random_reads 0.01 --chimeras 0.04"}]

# Genomes
prefix = "/tudelft.net/staff-umbrella/abeellab/bcosma/reference-genomes/"
genomes = [{"name": "pfalciparum", "file_loc": prefix + "pfalciparum/pfalciparum.fna.gz", "length": "short"},
           {"name": "scerevisiae", "file_loc": prefix + "scerevisiae/scerevisiae.fna.gz", "length": "short"},
           {"name": "athaliana", "file_loc": prefix + "athaliana/athaliana.fna.gz", "length": "medium"},
           {"name": "celegans", "file_loc": prefix + "celegans/vc2010/UNSB01-no-N.fasta", "length": "medium"},
           {"name": "dmelanogaster", "file_loc": prefix + "dmelanogaster/dmelanogaster-no-N.fna.gz", "length": "medium"},
           {"name": "trubripes", "file_loc": prefix + "trubripes/trubripes-no-N.fna.gz", "length": "medium-large"}]

if __name__ == '__main__':
    for genome in genomes:
        print("\nGenome: " + genome["name"])
        print("---")
        for model in models:
            print("Model: " + model["name"])
            print("---")
        
            for i,read_length in enumerate(model["read_lengths"]):
                print("Read lengths: " + read_length)
                script_name = "simulate_" + genome["name"] + "_" + model["technology"] + "_s" + str(i) + ".sbatch"

                # If file exists, delete and create a new one
                if os.path.exists(script_name):
                    os.remove(script_name)

                # Create script file
                script = open(script_name, "a+")

                # Copy sbatch parameters to script file
                sbatch_parameters = open("sbatch_parameters_" + genome["length"] + ".txt", "r")
                script.write(sbatch_parameters.read())

                # Append the srun line
                read_file = "[path]" + genome["name"] + "_" + model["technology"] + "_s" + str(i) + ".fastq.gz"
                srun_line = "srun badread simulate --seed 10 --quantity 30x --error_model " + "[path]/Badread/badread/error_models/" + model["name"] + ".gz" \
                    + " --qscore_model " + "[path]/Badread/badread/qscore_models/" + model["name"] + ".gz" \
                    + " --reference " + genome["file_loc"] \
                    + " --length " + read_length \
                    + " --identity " + model["identity"] \
                    + " " + model["other"] \
                    + " | gzip > " + read_file

                script.write(srun_line)
                script.close()

                # Run script
                os.system("sbatch " + script_name)
                time.sleep(4)
