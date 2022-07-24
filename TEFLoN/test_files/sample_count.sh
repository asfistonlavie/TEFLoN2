#install dependencies using the following:
#conda create --name teflon_env --yes -c bioconda bwa samtools=1.3 python=2.7
#conda activate teflon_env

###Define variables
WD="./sample_output/"
PPN="4"
PREFIX="TEST"
HIERARCHY="./sample_reference_hierarchy.txt"
ANNOTATION="./sample_reference_te_annotation.bed"
GENOME="./sample_reference_genome.fasta"
READS1="./sample_reads_1.fq"
READS2="./sample_reads_2.fq"
SAMPLES="./sample_names.txt"


##teflon count
python ./../teflon_count.py \
    -wd ${WD} \
    -d ${WD}reference/${PREFIX}.prep_TF/ \
    -s ${SAMPLES} \
    -i sample1 \
    -l2 order \
    -q 20 \
    -t $PPN
