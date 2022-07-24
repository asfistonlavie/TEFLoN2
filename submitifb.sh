#!/bin/bash

#SBATCH --job-name=TEFLoN_Snakemake # job name (-J)
#SBATCH --cpus-per-task=1 # max nb of cores (-c)
#SBATCH --mem=2000 # max memory (-m)
#SBATCH --output=/shared/projects/tegambiae/Cameroon/05-test-snakemake/tmp/teflon.%j.out
#SBATCH --error=/shared/projects/tegambiae/Cameroon/05-test-snakemake/tmp/teflon.%j.err
#SBATCH --partition=long
#SBATCH --account=tegambiae
#SBATCH --mail-type=ALL
#SBATCH --mail-user=corentin.marco@etu.umontpellier.fr



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
ACCOUNT=tegambiae
# Or with all rules included in one snakemake file:
#RULES=Snakefile.smk

# config file to be edited
CONFIG=config.yaml

# slurm directive by rule (can be edited if needed)
CLUSTER_CONFIG=cluster.yaml
# sbatch directive to pass to snakemake
CLUSTER='sbatch --account=tegambiae --mem={cluster.mem} -c {cluster.cpus} -o {cluster.output} -e {cluster.error}'
# Maximum number of jobs to be submitted at a time (see cluster limitation)
MAX_JOBS=100

# Full clean up:
#rm -fr .snakemake logs *.out *.html *.log *.pdf
# Clean up only the .snakemake
#rm -fr .snakemake

# Dry run (simulation)
#snakemake --configfile $CONFIG -s $RULES -np -j $MAX_JOBS --cluster-config $CLUSTER_CONFIG --cluster "$CLUSTER" >snakemake_dryrun.out

# Full run (if everething is ok: uncomment it)
snakemake --configfile $CONFIG -s $RULES -p -j $MAX_JOBS --cluster-config $CLUSTER_CONFIG --cluster "$CLUSTER" >snakemake_dryrun.out


# If latency problem add to the run:
# --latency-wait 60

exit 0
