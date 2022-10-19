rule teflon_collapse :
    input :
        expand("data_output/1-mapping/{read}.sorted.cov.txt",read=READ),
        expand("data_output/1-mapping/{read}.sorted.stats.txt",read=READ),
        expand("data_output/countPos/{read}.all_positions_sorted.txt",read=READ),
        expand("data_output/countPos/{read}.all_positions.txt",read=READ)

    output:
        expand("data_output/1-mapping/{read}.sorted.subsmpl.bam",read=READ),
        expand("data_output/1-mapping/{read}.sorted.subsmpl.bam.bai",read=READ),
        expand("data_output/1-mapping/{read}.sorted.subsmpl.cov.txt",read=READ),
        expand("data_output/1-mapping/{read}.sorted.subsmpl.stats.txt",read=READ),
        expand("data_output/countPos/{read}.all_positions_sorted.collapsed.txt",read=READ),
        "data_output/countPos/union.txt",
        "data_output/countPos/union_sorted.txt",
        "data_output/countPos/union_sorted.collapsed.txt"

    params:
        wd = "data_output/",
        prepTF = "data_output/0-reference/"+config["PREFIX"]+".prep_TF/",
        snames = "data_output/sample_names.txt",
        samtools = config["SAMTOOLS"],
        thresholdSample = config["THREASHOLD_SAMPLE"],
        thresholdAll = config["THREASHOLD_ALL"],
        quality = config["QUALITY_COLLAPSE"],
        coverageOverride = config["COVERAGE_OVERRIDE"],
        python = config["PYTHON3"]

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
        if (len(config["COVERAGE_OVERRIDE"]) != 0) :
            cmd = cmd + ("-cov {params.coverageOverride} ")
        cmd = cmd + ("-t {threads}")
        shell(cmd)