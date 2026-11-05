# Interactive HTML report: quality of the input data + TEFLoN2 results (+ populations)
# Enabled with PARAMS > REPORT > USE (default: 1). See TEFLoN/teflon_report.py (needs numpy for the population part)

_report_cfg = config["PARAMS"].get("REPORT", {}) or {}
_rep_dir = config["PARAMS"]["GENERAL"]["WORKING_DIRECTORY"] + config["PARAMS"]["GENERAL"]["PREFIX"]
_report_html = _rep_dir + "/6-report/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".report.html"

_report_pop_input = []
if check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"]):
	_report_pop_input = [_rep_dir + "/4-genotypes/populations/all_frequency.population.genotypes.txt",
		_rep_dir + "/4-genotypes/populations/all_frequency.population.genotypes2.txt"]


rule teflon_report:
	input:
		expand(_rep_dir + "/1-mapping/{reads}.sorted.stats.txt", reads=samples_all),
		expand(_rep_dir + "/1-mapping/{reads}.sorted.cov.txt", reads=samples_all),
		expand(_rep_dir + "/4-genotypes/samples/{reads}.genotypes.txt", reads=samples_all),
		_rep_dir + "/4-genotypes/samples/all_samples.genotypes.txt",
		_report_pop_input

	output:
		_report_html

	log:
		error = ".logs/teflon_report/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".report.err",
		output = ".logs/teflon_report/" + config["PARAMS"]["GENERAL"]["PREFIX"] + ".report.out"

	params:
		python = config.get("DEPENDANCES", config.get("DEPENDENCIES", {})).get("PYTHON3", "python3"),
		wd = _rep_dir,
		snames = _rep_dir + "/sample_names.txt",
		minCov = str(_report_cfg.get("MIN_COVERAGE", 5)),
		minMapped = str(_report_cfg.get("MIN_MAPPED", 80)),
		minPP = str(_report_cfg.get("MIN_PROPERLY_PAIRED", 80)),
		fasta = config["DATA_INPUT"]["WORKING_DIRECTORY"] + "/reference/" + config["DATA_INPUT"]["GENOME"],
		geneAnnot = str(_report_cfg.get("GENE_ANNOTATION", "") or "").strip(),
		geneFlank = str(_report_cfg.get("GENE_FLANK", 2000))

	resources:
		mem_mb = get_mem_mb

	run:
		cmd = ("{params.python} TEFLoN/teflon_report.py -wd {params.wd} -s {params.snames} -o {output} "
			"--min-coverage {params.minCov} --min-mapped {params.minMapped} --min-properly-paired {params.minPP} "
			"-f {params.fasta} --flank {params.geneFlank} ")
		if params.geneAnnot != "" :
			cmd = cmd + "--annotation {params.geneAnnot} "
		if check_value(config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"]) :
			cmd = cmd + ("-pop " + config["PARAMS"]["GENOTYPE"]["POPULATION"]["FILE"] + " ")
		cmd = cmd + ("1> {log.output} 2> {log.error}")
		shell(cmd)


report_targets = []
if int(_report_cfg.get("USE", 1)) == 1 :
	report_targets = [_report_html]
