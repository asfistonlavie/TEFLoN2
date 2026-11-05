rule converted_TE_catalog:
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.collapsed.txt"

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/2-preliminaryResults/converted_TE_catalog.union_sorted.collapsed.txt"
	
	log:
		error = ".logs/converted_TE_catalog/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
		output = ".logs/converted_TE_catalog/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"

	benchmark:
		".benchmarks/converted_TE_catalog/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"
	
	params:
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		python = config["DEPENDANCES"]["PYTHON3"]

	resources:
		mem_mb=get_mem_mb

	shell:
		"{params.python} TEFLoN/position_conversion.py "
		"-wd {params.wd}  "
		"-d {params.prepTF} "
		"1> {log.output} 2> {log.error}"

rule summary_catalog:
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/2-preliminaryResults/converted_TE_catalog.union_sorted.collapsed.txt"

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/2-preliminaryResults/TE_catalog.summary"

	params:
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
		folder = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/2-preliminaryResults/",
		awk = config["DEPENDANCES"]["AWK"]


	log:
		error = ".logs/summary_catalog/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
		output = ".logs/summary_catalog/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"

	benchmark:
		".benchmarks/summary_catalog/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"
	
	resources:
		mem_mb=get_mem_mb

	shell:
		"{params.awk} -f TEFLoN/summary_TE_catalog.awk  "
		"{input} && mv TE_catalog.summary {params.folder} "
		"1> {log.output} 2> {log.error}"