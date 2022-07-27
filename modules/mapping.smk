#Custom reference index
rule bwa_index:
    input:
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa"
    output:
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa.bwt"
    shell:
        "bwa index {input}"



#Mapping reads on the reference
#Sort and file.sam to file.bam (binary file)
rule mapping:
    input:
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa.bwt",
        r1 = "data_input/samples/read1/{READ}_r1.fastq",
        r2 = "data_input/samples/read2/{READ}_r2.fastq"

    output:
        bam = "data_output/1-mapping/{READ}.sorted.bam"

    resources:
        mem_mb=get_mem_mb

    params:
        ref = "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa"

    threads: 10
    #https://dearxxj.github.io/post/2/
    
    resources:
        mem_mb=get_mem_mb

    shell:
        "bwa mem "
        "-t {threads} "
        "-Y {params.ref} "
        "{input.r1} "
        "{input.r2} "
        "| samtools sort "
        "-@ {threads} "
        "-o {output.bam}"



#Bam files index
rule samtools_index:
    input:
        "data_output/1-mapping/{READ}.sorted.bam"

    output:
        bai = "data_output/1-mapping/{READ}.sorted.bam.bai"

    params:
        sample = "{READ}"
    
    shell:
        "samtools index "
        "{input} "
        "&& echo -e './{input}\t{params.sample}' "
        ">> data_output/sample_names.txt"
