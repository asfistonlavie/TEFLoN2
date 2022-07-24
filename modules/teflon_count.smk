rule teflon_count : 
    input:
        "data_output/1-mapping/{READ}.sorted.subsmpl.bam",
        "data_output/1-mapping/{READ}.sorted.subsmpl.bam.bai",
        "data_output/1-mapping/{READ}.sorted.subsmpl.cov.txt",
        "data_output/1-mapping/{READ}.sorted.subsmpl.stats.txt",
        "data_output/countPos/{READ}.all_positions_sorted.collapsed.txt",
        "data_output/countPos/union.txt",
        "data_output/countPos/union_sorted.txt",
        "data_output/countPos/union_sorted.collapsed.txt"

    output:
        "data_output/countPos/{READ}.counts.txt"

    params:
        wd = "data_output/",
        prepTF = "data_output/0-reference/"+config["PREFIX"]+".prep_TF/",
        snames = "data_output/sample_names.txt",
        sample = "{READ}",
        bwa = config["BWA"],
        samtools = config["SAMTOOLS"],
        levelh2 = config["LEVEL_HERARCHY2"],
        quality = config["QUALITY_COUNT"],
        python = config["PYTHON3"]

    threads: 20

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
        "-t {threads}"
