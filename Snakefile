#config file
configfile: "config.yaml"

#import dependences python
import subprocess
import os
import sys


#function
def get_mem_mb(wildcards, attempt):
    return 30000 +  20000* (attempt - 1)

##global variable
READ = glob_wildcards("data_input/samples/read1/{sample}_r1.fastq").sample + glob_wildcards("data_input/samples/bam/{sample}.bam").sample
localrules:
    all

#rule all defines the output of the pipeline
rule all:
    input:
        expand("data_output/countPos/{read}.pseudoSpace.genotypes.txt",read=READ),
        expand("data_output/genotypes/{read}.genotypes.txt",read=READ),

include: "modules/bamtofastq.smk"

#Choice of the script to call according to the input data file
if "GENOME" in config["DATA"]:
    if "ANNOTATION" in config["DATA"]:
        include: "modules/teflon_prep_annotation.smk"
    elif "LIBRARY" in config["DATA"] :
        include: "modules/teflon_prep_custom.smk"
else : 
    sys.exit("Invalid inputs")

#Calling snakemake modules
include: "modules/mapping.smk"
include: "modules/teflon_discover.smk"
include: "modules/teflon_collapse.smk"
include: "modules/teflon_count.smk"
include: "modules/teflon_genotype.smk"