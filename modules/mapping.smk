#Custom reference index
rule bwa_index:
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa"

	output:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa.bwt"

	log:
		error = ".logs/bwa_index/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err"

	benchmark:
		".benchmarks/bwa_index/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"

	params:
		bwa = config["DEPENDANCES"]["BWA"]

	shell:
		"{params.bwa} index {input} 2> {log.error}"




#Mapping reads on the reference
#Sort and file.sam to file.bam (binary file)
rule mapping:
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa.bwt",
		r1 = reads1,
		r2 = reads2

	output:
		bam = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{reads}.sorted.bam"

	log:
		error = ".logs/mapping/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.err"
	
	benchmark:
		".benchmarks/mapping/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.benchmark.txt"

	resources:
		mem_mb=get_mem_mb

	params:
		ref = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa",
		bwa = config["DEPENDANCES"]["BWA"]

	threads: config["PARAMS"]["SAMTOOLS"]["THREADS"]
	#https://dearxxj.github.io/post/2/
	
	resources:
		mem_mb=get_mem_mb

	shell:
		"{params.bwa} mem "
		"-t {threads} "
		"-Y {params.ref} "
		"{input.r1} "
		"{input.r2} 2> {log.error} "
		"| samtools sort "
		"-@ {threads} "
		"-o {output.bam} 2>> {log.error} && type({input.r1}) > {log.error}"





#Bam files index
rule samtools_index:
	input:
		config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{reads}.sorted.bam"

	output:
		bai = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{reads}.sorted.bam.bai"

	benchmark:
		".benchmarks/samtools_index/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{reads}.benchmark.txt"

	params:
		wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
		sample = "{reads}",
		samtools = config["DEPENDANCES"]["SAMTOOLS"]

	shell:
		"{params.samtools} index "
		"{input} "
		"&& echo -e '{input}\t{params.sample}' "
		">> {params.wd}/sample_names.txt"