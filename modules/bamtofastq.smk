rule samtools_sort:
	input:
		bam = "data_input/samples/bam/{BAM}.bam"
	output:
		bam_sort = "data_input/samples/bam/{BAM}_sorted.bam"

	threads: 8

	shell:
		"samtools sort "
		"-n {input} "
		"-@ {threads} "
		"-o {output}"


rule samtools_fastq:
	input:
		bam = "data_input/samples/bam/{BAM}_sorted.bam"
	output:
		r1 = "data_input/samples/read1/{BAM}_r1.fastq",
		r2 = "data_input/samples/read2/{BAM}_r2.fastq"

	threads: 8

	shell:
		"samtools fastq "
		"-@ {threads} "
		"{input} "
		"-1 {output.r1} "
		"-2 {output.r2} "
		"-0 /dev/null -s /dev/null -n "
		"&& rm {input}"