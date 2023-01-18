#rule that executes the teflon_prep_annotation script that prepares the custom reference
rule teflon_prep_annotation:
    input:
        annotation = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/library/" + config["DATA_INPUT"]["ANNOTATION"],
        hierarchy = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/library/" + config["DATA_INPUT"]["HIERARCHY"],
        genome = config["PARAMS"]["DATA_INPUT"]["WORKING_DIRECTORY"]+"/reference/" + config["DATA_INPUT"]["GENOME"]

    output:
        directory(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_TF"),
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa"
    
    log:
        error = ".logs/teflon_prep_annotation/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".err",
        output = ".logs/teflon_prep_annotation/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".out"
        
    benchmark:
        ".benchmarks/teflon_prep_annotation/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".benchmark.txt"
    
    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/",
        prefix = config["PARAMS"]["GENERAL"]["PREFIX"],
        canonicalTE = config["DATA_INPUT"]["LIBRARY"],
        python = config["DEPENDANCES"]["PYTHON3"]

    resources:
        mem_mb=get_mem_mb

    run:
        cmd = ("{params.python} TEFLoN/teflon_prep_annotation.py "
        "-wd {params.wd} "
        "-a {input.annotation} "
        "-t {input.hierarchy} "
        "-g {input.genome} "
        "-p {params.prefix} ")
        if (check_value(config["DATA_INPUT"]["LIBRARY"])) :
            cmd = cmd + ("-f {params.canonicalTE} ")
        cmd = cmd + ("1> {log.output} 2> {log.error}")
        shell(cmd)
