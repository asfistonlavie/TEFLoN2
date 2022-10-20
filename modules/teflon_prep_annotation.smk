#rule that executes the teflon_prep_annotation script that prepares the custom reference
rule teflon_prep_annotation:
    input:
        annotation = "data_input/library/" + config["DATA"]["ANNOTATION"],
        hierarchy = "data_input/library/" + config["DATA"]["HIERARCHY"],
        genome = "data_input/reference/" + config["DATA"]["GENOME"]

    output:
        directory(config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".prep_TF"),
        config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".prep_MP/"+config["PARAMS"]["GENERAL"]["PREFIX"]+".mappingRef.fa"

    params:
        wd = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"]+config["PARAMS"]["GENERAL"]["PREFIX"]+"/0-reference/",
        prefix = config["PARAMS"]["GENERAL"]["PREFIX"],
        canonicalTE = config["DATA"]["LIBRARY"],
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
        if (not "{params.canonicalTE}") :
            cmd = (cmd + "-f {params.canonicalTE} ")
        cmd = (cmd + "-g {input.genome} "
        "-p {params.prefix}")
        shell(cmd)
