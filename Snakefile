#import dependences python
import subprocess
import os
import sys

#function
def get_mem_mb(wildcards, attempt):
	return config["PARAMS"]["GENERAL"]["MEMORY"] +  (config["PARAMS"]["GENERAL"]["MEMORY_SUPP"] * (attempt - 1))

def reads1 (wcs):
	name = wcs.reads
	wd = config["DATA_INPUT"]["WORKING_DIRECTORY"] + "/samples/reads1/"
	for file_ext in [".fastq", ".fq"] :
		for file_r1 in ["_1","_r1",".1",".r1"] :
			if os.path.exists(wd + name + file_r1 +file_ext) :
				read1 = wd + name + file_r1 + file_ext
				return read1
	read1 = wd + name + "_1.fastq"
	return read1

def reads2 (wcs):
	name = wcs.reads
	wd = config["DATA_INPUT"]["WORKING_DIRECTORY"] + "/samples/reads2/"
	for file_ext in [".fastq", ".fq"] :
		for file_r2 in ["_2","_r2",".2",".r2"] :
			if os.path.exists(wd + name + file_r2 +file_ext) :
				read2 = wd + name + file_r2 + file_ext
				return read2
	read2 = wd + name + "_2.fastq"
	return read2



def samples_list() :
	base = config["DATA_INPUT"]["WORKING_DIRECTORY"] + "/samples/"
	folders = ["bam/","reads/","reads1/","reads2/"]
	wd = []
	samples = {"id":[]}
	for i in folders :
		wd = base + i
		list_samples = os.listdir(wd)
		for element in list_samples:
			if ".fastq" in element or ".fq" in element or "bam" in element:
				if ".gz" in element :
					samples["id"].append(element.rsplit(".",2)[0].replace(".1","").replace(".r1","").replace("_1","").replace("_r1","").replace(".2","").replace(".r2","").replace("_2","").replace("_r2",""))
				else :
					samples["id"].append(element.rsplit(".",1)[0].replace(".1","").replace(".r1","").replace("_1","").replace("_r1","").replace(".2","").replace(".r2","").replace("_2","").replace("_r2",""))
	return samples



# check if varaible is None or empty
def check_value (var):
	if var is None :
		return False
	elif type(var) is int:
		return True
	elif type(var) is str :
		if len(var.strip()) == 0 :
			return False
		else :
			return True



if config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"].strip() == "" :
	config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"] = "data_output_"
else :
	config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"] = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/data_output_"

localrules:
	all

#rule all defines the output of the pipeline
##global variable

wd = config["DATA_INPUT"]["WORKING_DIRECTORY"]
dict_samples = samples_list()
samples_all = set(dict_samples["id"])

include: "modules/formatting.smk"
include: "modules/bamtofastq.smk"

#Choice of the script to call according to the input data file
if check_value(config["DATA_INPUT"]["GENOME"]):
	if check_value(config["DATA_INPUT"]["ANNOTATION"]):
		include: "modules/teflon_prep_annotation.smk"
	elif check_value(config["DATA_INPUT"]["LIBRARY"]):
		include: "modules/teflon_prep_custom.smk"
else : 
	sys.exit("Invalid inputs")

#Calling snakemake modules
include: "modules/mapping.smk"
include: "modules/teflon_discover.smk"
include: "modules/teflon_collapse.smk"
include: "modules/teflon_count.smk"
include: "modules/teflon_genotype.smk"


rule all:
	input:
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{reads}.pseudoSpace.genotypes.txt",reads=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/{reads}.genotypes.txt",reads=samples_all),