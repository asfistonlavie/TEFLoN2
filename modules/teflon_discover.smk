#rule that runs teflonv0.4 scritp to detect TE breakpoints
rule teflon_discover:
    input:
        bai = "data_output/1-mapping/{READ}.sorted.bam.bai"

    output: 
        "data_output/1-mapping/{READ}.sorted.cov.txt",
        "data_output/1-mapping/{READ}.sorted.stats.txt",
        "data_output/countPos/{READ}.all_positions_sorted.txt",
        "data_output/countPos/{READ}.all_positions.txt"
        
    params:
        wd = "data_output/",
        prepTF = "data_output/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
        snames = "data_output/sample_names.txt",
        sample = "{READ}",
        bwa = config["DEPENDANCES"]["BWA"],
        samtools = config["DEPENDANCES"]["SAMTOOLS"],
        levelh1 = config["PARAMS"]["DISCOVER"]["LEVEL_HIERARCHY1"],
        levelh2 = config["PARAMS"]["DISCOVER"]["LEVEL_HIERARCHY2"],
        quality = config["PARAMS"]["DISCOVER"]["QUALITY"],
        exclude = config["PARAMS"]["DISCOVER"]["EXCLUDE"],
        standardDeviation = config["PARAMS"]["DISCOVER"]["STANDARD_DEVIATION"],
        coverageOverride = config["PARAMS"]["DISCOVER"]["COVERAGE_OVERRIDE"],
        python = config["DEPENDANCES"]["PYTHON3"]

    threads: 16

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
        if (not "{params.exclude}") :
            cmd = cmd + ("-exclude {params.exclude} ")
        if (not "{params.standardDeviation}") :
            cmd = cmd + ("-sd {params.standardDeviation} ")
        if (not "{params.coverageOverride}") :
            cmd = cmd + ("-cov {params.coverageOverride} ")
        cmd = cmd + ("-t {threads}")
        shell(cmd)
