#rule that executes teflon_prep_custom script that prepares the custom reference using RepeatMasker
rule teflon_prep_custom:
    input:
        genome = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/reference/" + config["DATA_INPUT"]["GENOME"],
        library = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/library/" + config["DATA_INPUT"]["LIBRARY"]


    output:
        directory(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_TF"),
        directory(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_RM"),
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa"

    log:
        error = ".logs/teflon_prep_custom/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
        output = ".logs/teflon_prep_custom/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".output"

    benchmark:
        ".benchmarks/teflon_prep_custom/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"

    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/",
        repeatMasker = config["DEPENDANCES"]["REPEATMASKER"],
        prefix = config["PARAMS"]["GENERAL"]["PREFIX"],
        cutoff = config["PARAMS"]["PREP_CUSTOM"]["CUTOFF"],
        minlength = config["PARAMS"]["PREP_CUSTOM"]["MIN_LENGTH"],
        splitDist = config["PARAMS"]["PREP_CUSTOM"]["SPLIT_DIST"],
        divergence = config["PARAMS"]["PREP_CUSTOM"]["DIVERGENCE"],
        python = config["DEPENDANCES"]["PYTHON3"]
      
    threads: config["PARAMS"]["PREP_CUSTOM"]["THREADS"]

    resources:
        mem_mb=get_mem_mb
                         
    run:
        cmd = ("{params.python} TEFLoN/teflon_prep_custom.py "
        "-wd {params.wd} "
        "-e {params.repeatMasker} "
        "-g {input.genome} "
        "-l {input.library} "
        "-p {params.prefix} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["CUTOFF"])) :
            cmd = cmd + ("-c {params.cutoff} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["MIN_LENGTH"])) :
            cmd = cmd + ("-m {params.minlength} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["SPLIT_DIST"])) :
            cmd = cmd + ("-s {params.splitDist} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["DIVERGENCE"])) :
            cmd = cmd + ("-d {params.divergence} ")
        cmd = cmd + ("-t {threads} 1> {log.output} 2> {log.error}")
        shell(cmd)
