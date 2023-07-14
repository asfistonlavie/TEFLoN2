rule subsmple :
	input :
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.cov.txt",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.stats.txt",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions_sorted.txt",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions.txt",samples_all=samples_all)
	output:
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.bam",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.bam.bai",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.cov.txt",samples_all=samples_all),
		expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.stats.txt",samples_all=samples_all),
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/averageLength.all.txt"

	log:
		error = ".logs/subsample/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
		output = ".logs/subsample/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"

	benchmark:
		".benchmarks/subsample/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"

	params:
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
		samtools = config["DEPENDANCES"]["SAMTOOLS"],
		quality = config["PARAMS"]["COLLAPSE"]["QUALITY"],
		coverageOverride = config["PARAMS"]["COLLAPSE"]["COVERAGE_OVERRIDE"],
		python = config["DEPENDANCES"]["PYTHON3"]

	threads: config["PARAMS"]["COLLAPSE"]["THREADS"]


	resources:
		mem_mb=get_mem_mb


	run: 
		cmd = ("{params.python} TEFLoN/subsample.py "
		"-wd {params.wd} "
		"-d {params.prepTF} "
		"-s {params.snames} "
		"-es {params.samtools} "
		"-q {params.quality} ")
		if (check_value(config["PARAMS"]["COLLAPSE"]["COVERAGE_OVERRIDE"])) :
			cmd = cmd + ("-cov {params.coverageOverride} ")
		cmd = cmd + ("-t {threads} 1> {log.output} 2> {log.error}")
		shell(cmd)