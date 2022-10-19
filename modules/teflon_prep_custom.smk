#rule that executes teflon_prep_custom script that prepares the custom reference using RepeatMasker
rule teflon_prep_custom:
    input:
        genome = "data_input/reference/" + config["GENOME"],
        library = "data_input/library/" + config["LIBRARY"]


    output:
        directory("data_output/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_TF"),
        directory("data_output/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_RM"),
        "data_output/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa"

    params:
        wd = "data_output/0-reference/",
        repeatMasker = config["DEPENDANCES"]["REPEATMASKER"],
        prefix = config["PARAMS"]["GENERAL"]["PREFIX"],
        cutoff = config["PARAMS"]["PREP_CUSTOM"]["CUTOFF"],
        minlength = config["PARAMS"]["PREP_CUSTOM"]["MIN_LENGTH"],
        splitDist = config["PARAMS"]["PREP_CUSTOM"]["SPLIT_DIST"],
        divergence = config["PARAMS"]["PREP_CUSTOM"]["DIVERGENCE"],
        python = config["DEPENDANCES"]["PYTHON3"]
      
    threads: 16

    resources:
        mem_mb=get_mem_mb
                         
    run:
        cmd = ("{params.python} TEFLoN/teflon_prep_custom.py "
        "-wd {params.wd} "
        "-e {params.repeatMasker} "
        "-g {input.genome} "
        "-l {input.library} "
        "-p {params.prefix} ")
        if (not "{params.cutoff}") :
            cmd = cmd + ("-c {params.cutoff} ")
        if (not "{params.minlength}") :
            cmd = cmd + ("-m {params.minlength} ")
        if (not "{params.splitDist}") :
            cmd = cmd + ("-s {params.splitDist} ")
        if (not "{params.divergence}") :
            cmd = cmd + ("-d {params.divergence} ")
        cmd = cmd + ("-t {threads}")
        shell(cmd)
