rule teflon_collapse :
    input :
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{read}.sorted.cov.txt",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{read}.sorted.stats.txt",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{read}.all_positions_sorted.txt",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{read}.all_positions.txt",read=READ)

    output:
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{read}.sorted.subsmpl.bam",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{read}.sorted.subsmpl.bam.bai",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{read}.sorted.subsmpl.cov.txt",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{read}.sorted.subsmpl.stats.txt",read=READ),
        expand(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{read}.all_positions_sorted.collapsed.txt",read=READ),
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.collapsed.txt"

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
        cmd = cmd + ("-t {threads}")
        shell(cmd)