import os
import time

technologies = ["ont", "pacbio", "pacbio_hifi"]

lengths = ["s0", "s1", "s2", "s3"]

prefix = "[path]"
genomes = [{"name": "pfalciparum", "file_loc": prefix + "pfalciparum/pfalciparum.fna.gz"},
           {"name": "scerevisiae", "file_loc": prefix + "scerevisiae/scerevisiae.fna.gz"},
           {"name": "athaliana", "file_loc": prefix + "athaliana/athaliana.fna.gz"},
           {"name": "celegans", "file_loc": prefix + "celegans/vc2010/UNSB01-no-N.fasta"},
           {"name": "dmelanogaster", "file_loc": prefix + "dmelanogaster/dmelanogaster-no-N.fna.gz"},
           {"name": "trubripes", "file_loc": prefix + "trubripes/trubripes-no-N.fna.gz"}]

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
            
            out_dir = "[prefix]" \
                + genome["name"] + "_" \
                + assembler["name"] + "_" \
                + technology

            script_name = "quast_evaluate_" + genome["name"] + "_" + assembler["name"] + "_" + technology + ".sbatch"
            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters_quast.txt",  "r")
            script.write(sbatch_parameters.read())

            srun_line = "srun quast --threads 16 --output-dir " + out_dir \
                + " -r " + genome["file_loc"]
            
            assembly_loc = ""
            for length in lengths:
                assembly_loc = "[path]" \
                    + assembler["name"] + "/" \
                    + genome["name"] \
                    + "_" + technology \
                    + "_" + length + "/" \
                    + assembler["assembly"]

                assembly_completed = os.path.exists(assembly_loc)
                if not assembly_completed:
                    print("Did not find " + assembly_loc)
                else:
                    srun_line += " " + assembly_loc

            
            script.write(srun_line)
            script.close()

            # Run script
            os.system("sbatch " + script_name)
            time.sleep(4)
