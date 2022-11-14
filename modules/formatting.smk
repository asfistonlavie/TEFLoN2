rule rename_reads:
	input:
		read = "data_input/samples/reads/{name}.fq",

	output:
		read_final = "data_input/samples/reads/{name}.fastq"

	shell:
		"mv {input.read} {output.read_final}"

rule deinterleave_fastq:
	input:
		fastq = "data_input/samples/reads/{samples_interleaved}.fastq",

	output:
		r1 = "data_input/samples/reads1/{samples_interleaved}_1.fastq",
		r2 = "data_input/samples/reads2/{samples_interleaved}_2.fastq"

	benchmark:
		".benchmarks/deinterleave_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_interleaved}.benchmark.txt"

	shell:
		"paste - - - - - - - - < {input.fastq} | "
		"tee >(cut -f 1-4 | tr '\t' '\n' > {output.r1}) | "
		"cut -f 5-8 | tr '\t' '\n' > {output.r2}"



