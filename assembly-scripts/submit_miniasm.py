import time
import os

technologies = [{"name": "ont", "arg": "ava-ont"},
                {"name": "pacbio", "arg": "ava-pb"},
                {"name": "pacbio_hifi", "arg": "ava-pb"}]

lengths = ["s0", "s1", "s2", "s3"]


genomes = [{"name": "pfalciparum", "length": "small", "threads": 8},
           {"name": "scerevisiae", "length": "small", "threads": 8},
           {"name": "athaliana", "length": "medium", "threads": 16},
           {"name": "celegans", "length": "medium", "threads": 16},
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

            script_name = "miniasm_assemble_" \
                + genome["name"] \
                + "_" + technology["name"] \
                + "_" + length  + ".sbatch"

            # If file exists, delete and create a new one
            if os.path.exists(script_name):
                os.remove(script_name)

            # Create script file
            script = open(script_name, "a+")

            # Copy sbatch parameters to script file
            sbatch_parameters = open("sbatch_parameters/miniasm_" + genome["length"] + ".txt", "r")
            script.write(sbatch_parameters.read())

            # srun minimap2 -x ava-pb -t 20 $reads $reads | gzip -1 > miniasm-mapped-pacbio-potato-reads.paf.gz
            # srun miniasm -f $reads miniasm-mapped-pacbio-potato-reads.paf.gz > miniasm-potato-pacbio-unitigs.gfa
            # srun minipolish -t 20 $reads miniasm-potato-pacbio-unitigs.gfa > miniasm-polished-pacbio-potato-assembly.gfa

            srun_line = "srun minimap2 -x " + technology["arg"] + " -t " + str(genome["threads"]) + " " + read_file + " " + read_file \
                + " | gzip -1 > overlap.paf.gz \n" \
                + "srun miniasm -f " + read_file + " overlap.paf.gz > unitigs.gfa \n" \
                + "srun minipolish -t " + str(genome["threads"]) + " " + read_file + " unitigs.gfa > assembly.gfa \n"

            script.write("cd " + path_to_assembly + " && mkdir -p " + genome["name"] + "_" + technology["name"] + "_" + length +  " && cd " + output_dir + "\n")
            script.write(srun_line)

            to_fasta = "awk '/^S/{print \">\"$2\"\n\"$3}' assembly.gfa | fold > assembly.fasta".encode("unicode_escape").decode("utf-8")
            script.write(to_fasta)
            
            script.close()

            # Run script
            os.system("sbatch " + script_name)
            time.sleep(2)
