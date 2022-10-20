rule teflon_count : 
    input:
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{READ}.sorted.subsmpl.bam",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{READ}.sorted.subsmpl.bam.bai",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{READ}.sorted.subsmpl.cov.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/1-mapping/{READ}.sorted.subsmpl.stats.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{READ}.all_positions_sorted.collapsed.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.txt",
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/union_sorted.collapsed.txt"

    output:
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/3-countPos/{READ}.counts.txt"

    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"],
        prepTF = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_TF/",
        snames = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/sample_names.txt",
        sample = "{READ}",
        bwa = config["DEPENDANCES"]["BWA"],
        samtools = config["DEPENDANCES"]["SAMTOOLS"],
        levelh2 = config["PARAMS"]["DISCOVER"]["LEVEL_HIERARCHY2"],
        quality = config["PARAMS"]["COUNT"]["QUALITY"],
        python = config["DEPENDANCES"]["PYTHON3"]

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
