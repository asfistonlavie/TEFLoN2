rule teflon_genotype :
    input:
        expand("data_output/countPos/{read}.counts.txt",read=READ)

    output:
        expand("data_output/countPos/{read}.pseudoSpace.genotypes.txt",read=READ),
        expand("data_output/genotypes/{read}.genotypes.txt",read=READ)

    params:
        wd = "data_output/",
        prepTF = "data_output/0-reference/"+config["PREFIX"]+".prep_TF/",
        snames = "data_output/sample_names.txt",
        thresholdLower = config["THREASHOLD_LOWER"],
        thresholdHigher = config["THREASHOLD_HIGHER"],
        datatype = config["DATA_TYPE"],
        python = config["PYTHON3"]

    resources:
        mem_mb=get_mem_mb

    run:# delete everything so we can re-run things
        cmd = ("{params.python} TEFLoN/teflon_genotype.py "
        "-wd {params.wd}  "
        "-d {params.prepTF} "
        "-s {params.snames} ")
        if (len(config["THREASHOLD_LOWER"]) != 0) :
            cmd = cmd + ("-lt {params.thresholdLower} ")
        if (len(config["THREASHOLD_HIGHER"]) != 0) :
            cmd = cmd + ("-ht {params.thresholdHigher} ")
        cmd = cmd + ("-dt {params.datatype}")
        shell(cmd)
