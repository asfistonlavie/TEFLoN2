#rule that runs teflonv0.4 scritp to detect TE breakpoints
rule teflon_discover:
    input:
        bai = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.bam.bai"

    output: 
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.cov.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.stats.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions_sorted.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions.txt"

    log:
        error = ".logs/teflon_discover/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.err",
        output = ".logs/teflon_discover/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.out"
    
    benchmark:
        ".benchmarks/teflon_discover/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".{samples_all}.benchmark.txt"  

    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
        prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
        snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
        sample = "{samples_all}",
        bwa = config["DEPENDANCES"]["BWA"],
        samtools = config["DEPENDANCES"]["SAMTOOLS"],
        levelh1 = config["PARAMS"]["DISCOVER"]["LEVEL_HIERARCHY1"],
        levelh2 = config["PARAMS"]["DISCOVER"]["LEVEL_HIERARCHY2"],
        quality = config["PARAMS"]["DISCOVER"]["QUALITY"],
        exclude = config["PARAMS"]["DISCOVER"]["EXCLUDE"],
        standardDeviation = config["PARAMS"]["DISCOVER"]["STANDARD_DEVIATION"],
        coverageOverride = config["PARAMS"]["DISCOVER"]["COVERAGE_OVERRIDE"],
        python = config["DEPENDANCES"]["PYTHON3"]

    threads: config["PARAMS"]["DISCOVER"]["THREADS"]

    resources:
        mem_mb=get_mem_mb

    run:
        cmd = ("{params.python} TEFLoN/teflon.v0.4.py "
        "-wd {params.wd} "
        "-d {params.prepTF} "
        "-s {params.snames} "
        "-i {params.sample} "
        "-eb {params.bwa} "
        "-es {params.samtools} "
        "-l1 {params.levelh1} "
        "-l2 {params.levelh2} "
        "-q {params.quality} ")
        if (check_value(config["PARAMS"]["DISCOVER"]["EXCLUDE"])) :
            cmd = cmd + ("-exclude {params.exclude} ")
        if (check_value(config["PARAMS"]["DISCOVER"]["STANDARD_DEVIATION"])):
            cmd = cmd + ("-sd {params.standardDeviation} ")
        if (check_value(config["PARAMS"]["DISCOVER"]["COVERAGE_OVERRIDE"])) :
            cmd = cmd + ("-cov {params.coverageOverride} ")
        cmd = cmd + ("-t {threads} 1> {log.output} 2> {log.error}")
        shell(cmd)
