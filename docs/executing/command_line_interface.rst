======================
Command line interface
======================



After completing the configuration files and placing input data in the correct folders, you can executing simulation of TEFLoN2 :

.. code-block:: console

	$ snakemake --configfile config.yaml -s Snakefile -np -j $MAX_JOBS

If all went well, execute TEFLoN2 :

.. code-block:: console

	$ snakemake --configfile config.yaml -s Snakefile -p -j $MAX_JOBS


To make TEFLoN2 work, you may need to configure your cluster.

For more information on the launch, go to `SnakeMake documentation <https://snakemake.readthedocs.io/en/stable/>`_.


SingularityCE
-------------

If tou use TEFLoN2.simg container, completing the configuration files and placing input data in the correct folders, you can executing simulation of TEFLoN2 :

.. code-block:: console

	singularity exec TEFLoN2.simg snakemake --configfile config.yaml -s Snakefile -np -j $MAX_JOBS

If all went well, execute TEFLoN2 :

.. code-block:: console

	singularity exec TEFLoN2.simg snakemake --configfile config.yaml -s Snakefile -np -j $MAX_JOBS


Cluster
-------

A launch file (submit.sh) is provided, but it is not exhaustive and is specific to the cluster we have used. The workload manager used is `SLURM <https://slurm.schedmd.com/containers.html>`_.

.. code-block:: console

		#!/bin/bash

	#SBATCH --job-name=TEFLoN2_Snakemake # job name (-J)
	#SBATCH --cpus-per-task=1 # max nb of cores (-c)
	#SBATCH --mem= 2000 # max memory (-m)
	#SBATCH --output=/path/tmp/teflon2.%j.out
	#SBATCH --error=/path/tmp/teflon2.%j.err
	#SBATCH --partition=long
	#SBATCH --account=your_project
	#SBATCH --mail-type=ALL
	#SBATCH --mail-user=your.mail.gmail.com



	###Charge module
	module purge
	module load samtools/1.14
	module load repeatmasker/4.1.2.p1
	module load python/3.9
	module load bwa/
	module load snakemake

	######################################################################

	########################## On ifb-core ###############################
	## Uncomment the next line
	#module load snakemake
	######################################################################


	# Using external rules in the main Snakefile (minimal Snakefile)
	RULES=Snakefile
	ACCOUNT=your_project
	# Or with all rules included in one snakemake file:
	#RULES=Snakefile.smk

	# config file to be edited
	CONFIG=config.yaml

	# slurm directive by rule (can be edited if needed)
	CLUSTER_CONFIG=cluster.yaml
	# sbatch directive to pass to snakemake
	CLUSTER='sbatch --account=your_project --mem={cluster.mem} -c {cluster.cpus} -o {cluster.output} -e {cluster.error}'
	# Maximum number of jobs to be submitted at a time (see cluster limitation)
	MAX_JOBS=100

	# Full clean up:
	#rm -fr .snakemake logs *.out *.html *.log *.pdf
	# Clean up only the .snakemake
	#rm -fr .snakemake

	# Dry run (simulation)
	#snakemake --configfile $CONFIG -s $RULES -np -j $MAX_JOBS --cluster-config $CLUSTER_CONFIG --cluster "$CLUSTER" 

	# Full run (if everething is ok: uncomment it)
	snakemake --configfile $CONFIG -s $RULES -p -j $MAX_JOBS --cluster-config $CLUSTER_CONFIG --cluster "$CLUSTER"


	# If latency problem add to the run:
	# --latency-wait 60

	exit 0


To run submit.sh, run :

.. code-block:: console

	sbatch submit.sh

For more information on Slurm, go to `SLURM documentation <https://slurm.schedmd.com/containers.html>`_.


Log files
---------

After each stage of Snakemake, log and benchmark files are created.
To consult you can run:

.. code-block:: console

	cat .logs/[name_step]/[name_run].[name_sample].err
	cat .logs/[name_step]/[name_run].[name_sample].err
	cat .benchmarks/[name_step]/[name_run].[name_sample].benchmark.txt