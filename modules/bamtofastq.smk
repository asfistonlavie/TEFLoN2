rule samtools_sort:
	input:
		bam = "data_input/samples/bam/{BAM}.bam"

	output:
		bam_sort = "data_input/samples/bam/{BAM}_sorted.bam"

	log:
		error = ".logs/samtools_sort/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{BAM}.err"

	benchmark:
		".benchmarks/samtools_sort/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{BAM}.benchmark.txt"

	params:
		samtools = config["DEPENDANCES"]["SAMTOOLS"]

	threads: config["PARAMS"]["SAMTOOLS"]["THREADS"]

	shell:
		"{params.samtools} sort "
		"-n {input} "
		"-@ {threads} "
		"-o {output} 2> {log.error}"


rule samtools_fastq:
	input:
		bam = "data_input/samples/bam/{BAM}_sorted.bam"
		
	output:
		r1 = "data_input/samples/reads1/{BAM}_1.fastq",
		r2 = "data_input/samples/reads2/{BAM}_2.fastq"

	log:
		error = ".logs/samtools_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{BAM}.err"

	benchmark:
		".benchmarks/samtools_fastq/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{BAM}.benchmark.txt"

	params:
		samtools = config["DEPENDANCES"]["SAMTOOLS"]

	threads: config["PARAMS"]["SAMTOOLS"]["THREADS"]

	shell:
		"{params.samtools} fastq "
		"-@ {threads} "
		"{input} "
		"-1 {output.r1} "
		"-2 {output.r2} "
		"-0 /dev/null -s /dev/null -n 2> {log.error} "
		"&& rm {input}"