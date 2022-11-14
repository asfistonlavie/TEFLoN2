rule teflon_collapse :
    input :
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.cov.txt",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.stats.txt",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions_sorted.txt",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions.txt",samples_all=samples_all)

    output:
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.bam",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.bam.bai",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.cov.txt",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{samples_all}.sorted.subsmpl.stats.txt",samples_all=samples_all),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{samples_all}.all_positions_sorted.collapsed.txt",samples_all=samples_all),
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.collapsed.txt"
    
    log:
        error = ".logs/teflon_collapse/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
        output = ".logs/teflon_collapse/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"

    benchmark:
        ".benchmarks/teflon_collapse/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"
    
    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
        prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
        snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
        samtools = config["DEPENDANCES"]["SAMTOOLS"],
        thresholdSample = config["PARAMS"]["COLLAPSE"]["THREASHOLD_SAMPLE"],
        thresholdAll = config["PARAMS"]["COLLAPSE"]["THREASHOLD_ALL"],
        quality = config["PARAMS"]["COLLAPSE"]["QUALITY"],
        coverageOverride = config["PARAMS"]["COLLAPSE"]["COVERAGE_OVERRIDE"],
        python = config["DEPENDANCES"]["PYTHON3"]

    threads: 16


    resources:
        mem_mb=get_mem_mb


    run: 
        cmd = ("{params.python} TEFLoN/teflon_collapse.py "
        "-wd {params.wd} "
        "-d {params.prepTF} "
        "-s {params.snames} "
        "-es {params.samtools} "
        "-n1 {params.thresholdSample} "
        "-n2 {params.thresholdAll} "
        "-q {params.quality} ")
        if (not "{params.coverageOverride}") :
            cmd = cmd + ("-cov {params.coverageOverride} ")
        cmd = cmd + ("-t {threads} 1> {log.output} 2> {log.error}")
        shell(cmd)