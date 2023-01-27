import time
import os

technologies = [{"name": "ont", "arg": "ont", "minimap_arg": "map-ont"},
                {"name": "pacbio", "arg": "sq", "minimap_arg": "map-pb"},
                {"name": "pacbio_hifi", "arg": "ccs", "minimap_arg": "map-hifi"}]

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

            script_name = "wtdbg_assemble_" \
                + genome["name"] \
                + "_" + technology["name"] \
                + "_" + length  + ".sbatch"

            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters/wtdbg_" + genome["length"] + ".txt", "r")
            script.write(sbatch_parameters.read())

            srun_line = "srun wtdbg2 -x " + technology["arg"] + " -g " + str(genome["size"]) + "m -i " + read_file + " -t " + str(genome["threads"]) + " -fo dbg \n" \
                + "srun wtpoa-cns -t " + str(genome["threads"]) + " -i dbg.ctg.lay.gz -fo dbg.raw.fa \n" \
                + "srun minimap2 -t " + str(genome["threads"]) + " -x " + technology["minimap_arg"] + " dbg.raw.fa "  + read_file + " | gzip > alignment1.paf.gz \n" \
                + "srun racon -t " + str(genome["threads"]) + " " + read_file + " alignment1.paf.gz dbg.raw.fa > polished1.fasta \n" \
                + "srun minimap2 -t " + str(genome["threads"]) + " -x " + technology["minimap_arg"] + " polished1.fasta "  + read_file +  " | gzip > alignment2.paf.gz \n" \
                + "srun racon -t " + str(genome["threads"]) + " " +  read_file + " alignment2.paf.gz polished1.fasta > assembly.fasta \n"

            script.write("cd " + path_to_assembly + " && mkdir -p " + genome["name"] + "_" + technology["name"] + "_" + length +  " && cd " + output_dir + "\n")
            script.write(srun_line)
            
            script.close()

            # Run script
            os.system("sbatch " + script_name)
            time.sleep(2)
