rule teflon_count : 
    input:
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/1-mapping/{samples_all}.sorted.subsmpl.bam",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/1-mapping/{samples_all}.sorted.subsmpl.bam.bai",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/1-mapping/{samples_all}.sorted.subsmpl.cov.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/1-mapping/{samples_all}.sorted.subsmpl.stats.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/3-countPos/{samples_all}.all_positions_sorted.collapsed.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/3-countPos/union.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/3-countPos/union_sorted.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/3-countPos/union_sorted.collapsed.txt"

    output:
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/3-countPos/{samples_all}.counts.txt"
    log:
        error = ".logs/teflon_count/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.err",
        output = ".logs/teflon_count/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.out"
    
    benchmark:
        ".benchmarks/teflon_count/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.benchmark.txt"
    
    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"],
        prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
        snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+"/sample_names.txt",
        sample = "{samples_all}",
        bwa = config["DEPENDANCES"]["BWA"],
        samtools = config["DEPENDANCES"]["SAMTOOLS"],
        levelh2 = config["PARAMS"]["DISCOVER"]["LEVEL_HIERARCHY2"],
        quality = config["PARAMS"]["COUNT"]["QUALITY"],
        python = config["DEPENDANCES"]["PYTHON3"]

    threads: config["PARAMS"]["COUNT"]["THREADS"]

    resources:
        mem_mb=get_mem_mb

    shell:
        "{params.python} TEFLoN/teflon_count.py "
        "-wd {params.wd} "
        "-d {params.prepTF} "
        "-s {params.snames} "
        "-i {params.sample} "
        "-eb {params.bwa} "
        "-es {params.samtools} "
        "-l2 {params.levelh2} "
        "-q {params.quality} "
        "-t {threads} 1> {log.output} 2> {log.error}"
