rule rename_reads:
	input:
		read = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads/{name}.fq",

	output:
		read_final = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads/{name}.fastq"

	log:
		error = ".logs/rename_reads/"+config["PARAMS"]["GENERAL"]["PREFIX"]+"{name}.err",
		output = ".logs/rename_reads/"+config["PARAMS"]["GENERAL"]["PREFIX"]+"{name}.out"

	benchmark:
		".logs/rename_reads/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{name}.benchmark.txt"

	shell:
		"mv {input.read} {output.read_final} 1> {log.output} 2> {log.error}"


rule deinterleave_fastq:
	input:
		fastq = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads/{samples_interleaved}.fastq",

	output:
		r1 = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads1/{samples_interleaved}_1.fastq",
		r2 = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads2/{samples_interleaved}_2.fastq"

	benchmark:
		".benchmarks/deinterleave_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_interleaved}.benchmark.txt"

	shell:
		"paste - - - - - - - - < {input.fastq} | "
		"tee >(cut -f 1-4 | tr '\t' '\n' > {output.r1}) | "
		"cut -f 5-8 | tr '\t' '\n' > {output.r2}"



