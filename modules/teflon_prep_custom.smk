#rule that executes teflon_prep_custom script that prepares the custom reference using RepeatMasker
rule teflon_prep_custom:
    input:
        genome = "data_input/reference/" + config["GENOME"],
        library = "data_input/library/" + config["LIBRARY"]


    output:
        directory("data_output/0-reference/" + config["PREFIX"] + ".prep_TF"),
        directory("data_output/0-reference/" + config["PREFIX"] + ".prep_RM"),
        "data_output/0-reference/"+config["PREFIX"]+".prep_MP/"+config["PREFIX"]+".mappingRef.fa"

    params:
        wd = "data_output/0-reference/",
        repeatMasker = config["REPEATMASKER"],
        prefix = config["PREFIX"],
        cutoff = config["CUTOFF"],
        minlength = config["MIN_LENGTH"],
        splitDist = config["SPLIT_DIST"],
        divergence = config["DIVERGENCE"],
        python = config["PYTHON3"]
      
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
