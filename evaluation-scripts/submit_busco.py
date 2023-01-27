import os
import time

technologies = ["ont", "pacbio", "pacbio_hifi"]

lengths = ["s0", "s1", "s2", "s3"]

genomes = [{"name": "pfalciparum", "arg": "plasmodium_odb10"},
           {"name": "scerevisiae", "arg": "saccharomycetes_odb10"},
           {"name": "athaliana", "arg": "brassicales_odb10"},
           {"name": "celegans", "arg": "nematoda_odb10"},
           {"name": "dmelanogaster", "arg": "diptera_odb10"},
           {"name": "trubripes", "arg": "actinopterygii_odb10"}]

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

            script_name = "busco_evaluate_" + genome["name"] + "_" + assembler["name"] + "_" + technology + ".sbatch"
            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters_busco.txt",  "r")
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
                    srun_line += "\n srun busco -f -c 16 -m genome -i " + assembly_loc \
                        + " -o " + assembler["name"] + "_" + genome["name"] + "_" + technology + "_" + length \
                        + " -l " + genome["arg"]

            script.write(srun_line)
            script.close()

            print(srun_line)
            os.system("sbatch " + script_name)
            time.sleep(4)
