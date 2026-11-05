=========================
Interactive configuration
=========================

Instead of editing ``config.yaml`` by hand (see :doc:`configure_parameter_file`), you can let the script
``teflon2_configure.py`` ask the questions and write the file for you. It only needs Python 3 (standard library).

.. code-block:: console

	$ python3 teflon2_configure.py

The script:

* keeps the comments of the template and does not touch the keys it does not need;
* saves the previous file as ``config.yaml.bak-<date>-<time>`` before writing;
* checks the paths you give (genome, library, population file, annotation) and the sample list found in ``data_input/samples``;
* ends by printing the Snakemake commands to run (dry run first).

First run or new run
====================

The script detects the situation by itself.

First run
	There is no ``config.yaml``, or it still contains the placeholders of the template, and no ``data_output_*`` folder.
	A full guided set-up is proposed: the tools (``python3``, ``bwa``, ``samtools``, RepeatMasker), the input data folder and
	the reference genome, how the TE annotation is provided (existing annotation, or prepared from a TE library), the run name
	(``PREFIX``), memory and threads, the discover / collapse / count settings, the genotyping thresholds and data type,
	the population file, the outputs (VCF / GFA, HTML report, gene annotation of the report) and the step at which to stop.

	If no TE library is found in ``data_input/library``, the script offers to download the latest Dfam library
	(see :doc:`../getting_started/installation`).

Existing run
	A filled ``config.yaml`` and/or previous results exist. The script lists the previous runs, the steps that are finished for each,
	and asks what you want to do:

	.. csv-table::
		:header: "Choice", "What it does"
		:widths: 30 70

		"Start a **new** run", "New run name (``PREFIX``), all the settings are reviewed. The results of the other runs are not touched."
		"**Update** the current run", "Add samples or change settings. Snakemake does not redo the steps that are finished and whose inputs did not change."
		"**Re-genotype** the current run", "New genotyping thresholds. The mapping, discover and count results are kept; the genotyping results and the outputs that depend on them (``4-genotypes``, ``5-export``, ``6-report``) are deleted after you confirm."
		"Only change the **outputs**", "Switch the VCF / GFA export and the HTML report on or off, or change their options."

Without questions
=================

For scripts and pipelines, two options avoid the prompts:

.. code-block:: console

	$ python3 teflon2_configure.py --yes                         # accept the detected / default values
	$ python3 teflon2_configure.py --yes \
	      --set PARAMS.GENERAL.PREFIX=run2 \
	      --set PARAMS.GENOTYPE.DATA_TYPE=pooled \
	      --set PARAMS.REPORT.GENE_ANNOTATION=annotation/genes.gff3

``--set A.B.C=value`` can be repeated; ``A.B.C`` is the path of the key in ``config.yaml``.
Use ``-c other.yaml`` to read and write another file than ``config.yaml``.

.. code-block:: none

	usage: teflon2_configure.py [-h] [-c CONFIG] [--yes] [--set A.B.C=value]

If an older ``config.yaml`` does not contain the ``EXPORT`` or ``REPORT`` blocks (or some of their keys), the script adds them.

After the configuration
=======================

.. code-block:: console

	$ snakemake --configfile config.yaml -s Snakefile -np -j $MAX_JOBS     # dry run
	$ snakemake --configfile config.yaml -s Snakefile -p -j $MAX_JOBS      # run
