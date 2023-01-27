import os
import time

technologies = ["ont", "pacbio", "pacbio_hifi"]

lengths = ["s0", "s1", "s2", "s3"]

prefix = "[path]"
genomes = [{"name": "pfalciparum", "file_loc": prefix + "pfalciparum/pfalciparum.fna", "length": "small"},
           {"name": "scerevisiae", "file_loc": prefix + "scerevisiae/scerevisiae.fna", "length": "small"},
           {"name": "athaliana", "file_loc": prefix + "athaliana/athaliana.fna", "length": "medium"},
           {"name": "celegans", "file_loc": prefix + "celegans/vc2010/UNSB01-no-N.fasta", "length": "medium"},
           {"name": "dmelanogaster", "file_loc": prefix + "dmelanogaster/dmelanogaster-no-N.fna", "length": "medium"},
           {"name": "trubripes", "file_loc": prefix + "trubripes/trubripes-no-N.fna", "length": "medium-long"}]

assemblers = [{"name": "canu", "assembly": "assembly.contigs.fasta"},
              {"name": "raven", "assembly": "assembly.fasta"},
              {"name": "wtdbg", "assembly": "assembly.fasta"},
              {"name": "miniasm", "assembly": "assembly.fasta"},
              {"name": "flye", "assembly": "assembly.fasta"}]

for genome in genomes:
    print("\nEvaluating " + genome["name"])
    print("-----")
    
    for assembler in assemblers:
        print(assembler)
        
        for technology in technologies:
            print(technology)

            script_name = "compass_evaluate_" + genome["name"] + "_" + assembler["name"] + "_" + technology + ".sbatch"
            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters_compass_" + genome["length"] + ".txt",  "r")
            script.write(sbatch_parameters.read())

            srun_line = ""

            for length in lengths:
                assembly_loc = "[path]" \
                    + assembler["name"] + "/" \
                    + genome["name"] \
                    + "_" + technology \
                    + "_" + length + "/" \
                    + assembler["assembly"]

                out_dir = "[path]" \
                    + genome["name"] + "_" \
                    + assembler["name"] + "_" \
                    + technology + "_" \
                    + length

                assembly_completed = os.path.exists(assembly_loc)

                if not assembly_completed:
                    print("Did not find " + assembly_loc)
                else:
                    srun_line += "\n mkdir -p " + out_dir + " && cd " + out_dir
                    srun_line += "\n srun perl compass-master/compass.pl " \
                        + genome["file_loc"] \
                        + " " + assembly_loc \
                        + " > 0stats.txt"

            script.write(srun_line)
            script.close()

            print(srun_line)
            os.system("sbatch " + script_name)
            time.sleep(4)

