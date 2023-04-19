rule teflon_genotype_individual :
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.counts.txt"

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/{samples_all}.pseudoSpace.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/{samples_all}.genotypes.txt"

	log:
		error = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.err",
		output = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.out"
	
	benchmark:
		".benchmarks/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.benchmark.txt"

	params:
		python = config["DEPENDANCES"]["PYTHON3"],
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
		sample = "{samples_all}",
		thresholdLower = config["PARAMS"]["GENOTYPE"]["THRESHOLD_LOWER"],
		thresholdHigher = config["PARAMS"]["GENOTYPE"]["THRESHOLD_HIGHER"],
		datatype = config["PARAMS"]["GENOTYPE"]["DATA_TYPE"],
		frequencyLoThresh = config["PARAMS"]["GENOTYPE"]["SAMPLE"]["POOLED_OR_DIPLOID"]["THRESHOLD_ABSENCE"],
		frequencyHiThresh = config["PARAMS"]["GENOTYPE"]["SAMPLE"]["POOLED_OR_DIPLOID"]["THRESHOLD_PRESENCE"],
		frequencyPresence = config["PARAMS"]["GENOTYPE"]["SAMPLE"]["HAPLOID"]["THRESHOLD_PRESENCE"],
		population_file = config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"],
		populationLoThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"],
		populationHiThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"]

	resources:
		mem_mb=get_mem_mb

	run:# delete everything so we can re-run things
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} "
		"-i {params.sample} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["THRESHOLD_LOWER"])) :
			cmd = cmd + ("-lt {params.thresholdLower} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["THRESHOLD_HIGHER"])) :
			cmd = cmd + ("-ht {params.thresholdHigher} ")
		if (config["PARAMS"]["GENOTYPE"]["DATA_TYPE"] == "haploid") :
			if (check_value(config["PARAMS"]["GENOTYPE"]["SAMPLE"]["HAPLOID"]["THRESHOLD_PRESENCE"])) :
				cmd = cmd + ("-flt {params.frequencyPresence} ")
		else:
			if (check_value(config["PARAMS"]["GENOTYPE"]["SAMPLE"]["POOLED_OR_DIPLOID"]["THRESHOLD_ABSENCE"])) :
				cmd = cmd + ("-flt {params.frequencyLoThresh} ")
			if (check_value(config["PARAMS"]["GENOTYPE"]["SAMPLE"]["POOLED_OR_DIPLOID"]["THRESHOLD_PRESENCE"])) :
				cmd = cmd + ("-flt {params.frequencyHiThresh} ")
		cmd = cmd + ("-dt {params.datatype} 1> {log.output} 2> {log.error}")
		shell(cmd)


rule teflon_genotype_all :
	input:
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/{reads}.pseudoSpace.genotypes.txt",reads=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/{reads}.genotypes.txt",reads=samples_all)

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/"+"all_samples.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/"+"all_samples.genotypes2.txt"
	log:
		error = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".all_samples.err",
		output = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".all_samples.out"
	
	benchmark:
		".benchmarks/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".all_samples.benchmark.txt"

	params:
		python = config["DEPENDANCES"]["PYTHON3"],
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
		populationLoThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"],
		populationHiThresh = config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"]

	resources:
		mem_mb=get_mem_mb

	run:# delete everything so we can re-run things
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"])) :
			cmd = cmd + ("-plt {params.populationLoThresh} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"])) :
			cmd = cmd + ("-plt {params.populationHiThresh} ")
		cmd = cmd + ("-dt {params.datatype} 1> {log.output} 2> {log.error}")
		shell(cmd)



rule teflon_genotype_population :
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/"+"all_samples.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/samples/"+"all_samples.genotypes2.txt"

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/{group}.genotypes.txt",
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/4-genotypes/populations/{group}.genotypes2.txt"

	log:
		error = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{group}.err",
		output = ".logs/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{group}.out"
	
	benchmark:
		".benchmarks/teflon_genotype/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{group}.benchmark.txt"

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

	run:# delete everything so we can re-run things
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"])) :
			cmd = cmd + ("-pop {params.population_file} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_ABSENCE"])) :
			cmd = cmd + ("-plt {params.populationLoThresh} ")
		if (check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["THRESHOLD_PRESENCE"])) :
			cmd = cmd + ("-plt {params.populationHiThresh} ")
		cmd = cmd + ("-dt {params.datatype} 1> {log.output} 2> {log.error}")
		shell(cmd)

