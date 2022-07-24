#rule that executes the teflon_prep_annotation script that prepares the custom reference
rule teflon_prep_annotation:
    input:
        annotation = "data_input/library/" + config["ANNOTATION"],
        hierarchy = "data_input/library/" + config["HIERARCHY"],
        genome = "data_input/reference/" + config["GENOME"]

    output:
        directory("data_output/0-reference/" + config["PREFIX"] + ".prep_MP"),
        directory("data_output/0-reference/" + config["PREFIX"] + ".prep_TF"),
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa"

    params:
        wd = "data_output/0-reference/",
        prefix = config["PREFIX"],
        canonicalTE = config["LIBRARY"],
        python = config["PYTHON3"]

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
