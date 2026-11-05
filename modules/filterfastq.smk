rule filterfastq:
	input:
		r1 = reads1_fastp,
		r2 = reads2_fastp

	output:
		out1 = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads1/{reads}_1.filter.fastq.gz",
		out2 = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads2/{reads}_2.filter.fastq.gz"

	log:
		error = ".logs/filterfastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.err",
		output = ".logs/filterfastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.out",
		html = ".logs/filterfastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.html",
		json = ".logs/filterfastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.json"

	
	benchmark:
		".benchmarks/filterfastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.benchmark.txt"

	params:
		fastp = config["DEPENDANCES"]["FASTP"]

	resources:
		mem_mb=get_mem_mb

	threads: config["PARAMS"]["FILTERFASTQ"]["THREADS"]
	
	resources:
		mem_mb=get_mem_mb

	shell:
		"{params.fastp} "
		"--in1 {input.r1} "
		"--in2 {input.r2} "
		"--out1 {output.out1} "
		"--out2 {output.out2} "
		"--html {log.html} "
		"--json {log.json} "
		"-w {threads} 1> {log.output} 2> {log.error}"
