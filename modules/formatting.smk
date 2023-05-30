


rule compress_fastq:
	input:
		read = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/{reads}",
	output:
		read_final = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/{reads}.gz",

	threads: config["PARAMS"]["COMPRESS"]["THREADS"]

	priority: 3

	log:
		error = ".logs/compress_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.err",
		output = ".logs/compress_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.out"

	benchmark:
		".logs/compress_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.benchmark.txt"

	shell:
		"pigz --best --processes {threads} {input.read} 1> {log.output} 2> {log.error}"


rule rename_reads:
	input:
		read = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads/{name}.fq.gz",

	output:
		read_final = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads/{name}.fastq.gz"

	priority: 2

	log:
		error = ".logs/rename_reads/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{name}.err",
		output = ".logs/rename_reads/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{name}.out"

	benchmark:
		".logs/rename_reads/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{name}.benchmark.txt"

	shell:
		"mv {input.read} {output.read_final} 1> {log.output} 2> {log.error}"



rule deinterleave_fastq:
	input:
		fastq = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads/{samples_interleaved}.fastq.gz",

	output:
		r1 = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads1/{samples_interleaved}_1.fastq.gz",
		r2 = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/samples/reads2/{samples_interleaved}_2.fastq.gz"

	threads: config["PARAMS"]["COMPRESS"]["THREADS"]

	priority: 1

	benchmark:
		".benchmarks/deinterleave_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_interleaved}.benchmark.txt"

	shell:
		'pigz --best --processes {threads} -dc {input.fastq} | '
		'paste - - - - - - - -  | '
		'tee >(cut -f 1-4 | tr "\\t" "\\n" | pigz --best --processes {threads} > {output.r1}) | '
		'cut -f 5-8 | tr "\\t" "\\n" | pigz --best --processes {threads} > {output.r2}'