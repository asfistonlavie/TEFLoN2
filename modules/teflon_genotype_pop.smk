rule teflon_genotype_population :
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/"+"all_samples.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/"+"all_samples.genotypes2.txt"

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/{group}.population.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/{group}.population.genotypes2.txt"

	log:
		error = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{group}.population.err",
		output = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{group}.population.out"
	
	benchmark:
		".benchmarks/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{group}.population.benchmark.txt"

	params:
		python = config["DEPENDANCES"]["PYTHON3"],
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		group = "{group}",
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
		population_file = config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"],
		populationLoThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"],
		populationHiThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"]

	resources:
		mem_mb=get_mem_mb

	run:
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} "
		"-g {params.group} "
		"-pop {params.population_file} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"])) :
			cmd = cmd + ("-plt {params.populationLoThresh} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"])) :
			cmd = cmd + ("-plt {params.populationHiThresh} ")
		cmd = cmd + ("1> {log.output} 2> {log.error}")
		shell(cmd)



rule teflon_genotype_all_populations :
	input:
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/{pop}.population.genotypes.txt",pop=group),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/{pop}.population.genotypes2.txt",pop=group)

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/all_frequency.population.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/all_frequency.population.genotypes2.txt"

	log:
		error = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".all_frequency.population.err",
		output = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".all_frequency.population.out"
	
	benchmark:
		".benchmarks/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".all_frequency.population.benchmark.txt"

	params:
		python = config["DEPENDANCES"]["PYTHON3"],
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
		population_file = config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"],
		populationLoThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"],
		populationHiThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"]

	resources:
		mem_mb=get_mem_mb

	run:
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} "
		"-pop {params.population_file} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"])) :
			cmd = cmd + ("-plt {params.populationLoThresh} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"])) :
			cmd = cmd + ("-plt {params.populationHiThresh} ")
		cmd = cmd + ("1> {log.output} 2> {log.error}")
		shell(cmd)
