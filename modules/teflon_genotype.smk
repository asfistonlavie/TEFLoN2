rule teflon_genotype :
	input:
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.counts.txt",samples_all=samples_all)

	output:
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.pseudoSpace.genotypes.txt",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/{samples_all}.genotypes.txt",samples_all=samples_all)

	log:
		error = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
		output = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"
	
	benchmark:
		".benchmarks/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"

	params:
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
		thresholdLower = config["PARAMS"]["GENOTYPE"]["THREASHOLD_LOWER"],
		thresholdHigher = config["PARAMS"]["GENOTYPE"]["THREASHOLD_HIGHER"],
		datatype = config["PARAMS"]["GENOTYPE"]["DATA_TYPE"],
		python = config["DEPENDANCES"]["PYTHON3"],
		population = config["PARAMS"]["GENOTYPE"]["POPULATION"]


	resources:
		mem_mb=get_mem_mb

	run:# delete everything so we can re-run things
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["THREASHOLD_LOWER"])) :
			cmd = cmd + ("-lt {params.thresholdLower} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["THREASHOLD_HIGHER"])) :
			cmd = cmd + ("-ht {params.thresholdHigher} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"])) :
			cmd = cmd + ("-pop {params.population} ")
		cmd = cmd + ("-dt {params.datatype} 1> {log.output} 2> {log.error}")
		shell(cmd)
