# Export of the genotypes as VCF (+ optional bgzip/tabix) and GFA (genotyping graph)
# Enabled with PARAMS > EXPORT > USE (default: 1). See TEFLoN/teflon_export.py

_export_cfg = config["PARAMS"].get("EXPORT", {}) or {}
_run_dir = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"] + config["PARAMS"]["GENERAL"]["PREFIX"]
_export_prefix = _run_dir + "/5-export/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".TE_genotypes"

_export_pop_input = []
if check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"]):
	_export_pop_input = [_run_dir + "/4-genotypes/populations/all_frequency.population.genotypes.txt"]


rule teflon_export:
	input:
		expand(_run_dir + "/4-genotypes/samples/{reads}.genotypes.txt", reads=samples_all),
		_run_dir + "/4-genotypes/samples/all_samples.genotypes.txt",
		_export_pop_input

	output:
		vcf = _export_prefix + ".vcf",
		gfa = _export_prefix + ".gfa"

	log:
		error = ".logs/teflon_export/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".export.err",
		output = ".logs/teflon_export/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".export.out"

	benchmark:
		".benchmarks/teflon_export/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".export.benchmark.txt"

	params:
		python = config.get("DEPENDANCES", config.get("DEPENDENCIES", {})).get("PYTHON3", "python3"),
		wd = _run_dir,
		snames = _run_dir + "/sample_names.txt",
		fasta = config["DATA_INPUT"]["WORKING_DIRECTORY"] + "/reference/" + config["DATA_INPUT"]["GENOME"],
		datatype = config["PARAMS"]["GENOTYPE"]["DATA_TYPE"],
		gfapaths = str(_export_cfg.get("GFA_PATHS", "samples")) or "samples"

	resources:
		mem_mb = get_mem_mb

	run:
		cmd = ("{params.python} TEFLoN/teflon_export.py "
			"-wd {params.wd} -s {params.snames} -f {params.fasta} "
			"-dt {params.datatype} --vcf {output.vcf} --gfa {output.gfa} "
			"--gfa-paths {params.gfapaths} ")
		if len(_export_pop_input) > 0 :
			cmd = cmd + ("--pop-freq " + _export_pop_input[0] + " ")
		cmd = cmd + ("1> {log.output} 2> {log.error}")
		shell(cmd)


rule teflon_export_compress:
	# bgzip + tabix index so that the VCF can be used directly by bcftools, GATK, vg, ...
	input:
		_export_prefix + ".vcf"
	output:
		_export_prefix + ".vcf.gz",
		_export_prefix + ".vcf.gz.tbi"
	log:
		".logs/teflon_export/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".compress.log"
	shell:
		"bgzip -c {input} > {output[0]} && tabix -f -p vcf {output[0]} 2> {log}"


export_targets = []
if int(_export_cfg.get("USE", 1)) == 1 :
	export_targets = [_export_prefix + ".vcf", _export_prefix + ".gfa"]
	if int(_export_cfg.get("COMPRESS", 0)) == 1 :
		export_targets = export_targets + [_export_prefix + ".vcf.gz", _export_prefix + ".vcf.gz.tbi"]
