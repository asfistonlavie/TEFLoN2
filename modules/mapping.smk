#Custom reference index
rule bwa_index:
    input:
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa"
    output:
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa.bwt"
    shell:
        "bwa index {input}"



#Mapping reads on the reference
rule bwa_mem:
    input:
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa.bwt",
        r1 = "data_input/samples/read1/{READ}_1.fastq",
        r2 = "data_input/samples/read2/{READ}_2.fastq"
    output:
        temp("data_output/1-mapping/"+"{READ}.sam")

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
        "> {output}"

#Sort and file.sam to file.bam (binary file)
rule samtools_view:
    input: 
        "data_output/1-mapping/{READ}.sam"

    output:
        bam = "data_output/1-mapping/{READ}.sorted.bam"

    threads: 8
    #https://link.springer.com/chapter/10.1007/978-3-319-58943-5_33

    resources:
        mem_mb=get_mem_mb

    shell:
        "samtools view "
        "-Sb {input} "
        "| samtools sort "
        "-@ {threads} - "
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
