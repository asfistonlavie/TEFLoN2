rule teflon_genotype :
	input:
		expand("data_output/countPos/{read}.counts.txt",read=READ)

	output:
		expand("data_output/countPos/{read}.pseudoSpace.genotypes.txt",read=READ),
		expand("data_output/genotypes/{read}.genotypes.txt",read=READ)

	params:
		wd = "data_output/",
		prepTF = "data_output/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		snames = "data_output/sample_names.txt",
		thresholdLower = config["PARAMS"]["GENOTYPE"]["THREASHOLD_LOWER"],
		thresholdHigher = config["PARAMS"]["GENOTYPE"]["THREASHOLD_HIGHER"],
		datatype = config["PARAMS"]["GENOTYPE"]["DATA_TYPE"],
		python = config["DEPENDANCES"]["PYTHON3"]

	resources:
		mem_mb=get_mem_mb

	run:# delete everything so we can re-run things
		cmd = ("{params.python} TEFLoN/teflon_genotype.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"-s {params.snames} ")
		if (not "{params.thresholdLower}") :
			cmd = cmd + ("-lt {params.thresholdLower} ")
		if (not "{params.thresholdHigher}") :
			cmd = cmd + ("-ht {params.thresholdHigher} ")
		cmd = cmd + ("-dt {params.datatype}")
		shell(cmd)
