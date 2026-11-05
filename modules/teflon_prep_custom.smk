#rule that executes teflon_prep_custom script that prepares the custom reference using RepeatMasker
rule teflon_prep_custom:
    input:
        genome = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/reference/" + config["DATA_INPUT"]["GENOME"]

    output:
        directory(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_TF"),
        directory(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_RM"),
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa"

    log:
        error = ".logs/teflon_prep_custom/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
        output = ".logs/teflon_prep_custom/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"

    benchmark:
        ".benchmarks/teflon_prep_custom/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"

    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/",
        library = config["DATA_INPUT"]["WORKING_DIRECTORY"]+"/library/" + config["DATA_INPUT"]["LIBRARY"],
        repeatMasker = config["DEPENDANCES"]["REPEATMASKER"],
        prefix = config["PARAMS"]["GENERAL"]["PREFIX"],
        species = config["PARAMS"]["PREP_CUSTOM"]["SPECIES"],        
        cutoff = config["PARAMS"]["PREP_CUSTOM"]["CUTOFF"],
        frag = config["PARAMS"]["PREP_CUSTOM"]["FRAG"],
        engine = config["PARAMS"]["PREP_CUSTOM"]["ENGINE"],
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
        "-p {params.prefix} ")
        if (check_value(config["DATA_INPUT"]["LIBRARY"])) :
            cmd = cmd + ("-l {params.library} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["SPECIES"])) :
            cmd = cmd + ("-species {params.species} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["CUTOFF"])) :
            cmd = cmd + ("-c {params.cutoff} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["FRAG"])) :
            cmd = cmd + ("-frag {params.frag} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["ENGINE"])) :
            cmd = cmd + ("-engine {params.engine} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["MIN_LENGTH"])) :
            cmd = cmd + ("-m {params.minlength} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["SPLIT_DIST"])) :
            cmd = cmd + ("-s {params.splitDist} ")
        if (check_value(config["PARAMS"]["PREP_CUSTOM"]["DIVERGENCE"])) :
            cmd = cmd + ("-d {params.divergence} ")
        cmd = cmd + ("-t {threads} 1> {log.output} 2> {log.error}")
        shell(cmd)
