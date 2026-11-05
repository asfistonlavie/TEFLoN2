=====================
Config parameter file
=====================

Configuration files are used to tell TEFLoN2 what to use.
 TEFLoN2 has two configuration files: 

 * Workflow configuration
 * Cluster configuration
 
Configuration of TEFLoN2
------------------------

TEFLoN2 uses Snakemake to perform its analyses. You have then first to provide your parameters in a .yaml file (see an example in the config.yaml file). Parameters are :

.. code-block:: yaml


    #all path can be relatif or absolute

    DEPENDANCES:
        PYTHON3:    "/path/to/python3" #[required] path to python 3 executable 
        BWA:    "path/to/bwa" #[required] path to bwa executable 
        SAMTOOLS:   "path/to/samtools" #[required] path to samtools executable 
        REPEATMASKER:   "path/to/repeatmasker" #[requiered if prep_custom] path to repeatmasker executable

    DATA_INPUT:
        WORKING_DIRECTORY:  "data_input" # [required] path to arbresecne of your data input. Default folder is data_input
        GENOME: "name_reference_file.fasta" #[required] name of reference file in data_input/reference
        ANNOTATION: "name_annotation_file.bed" #[required if prep_annotation] name of annotation file in data_input/library
        LIBRARY:    "name_TE_library.fasta" #[required if prep_custom][optional if prep_annotation] name of TE library file for your organism in data_input/library
        HIERARCHY:  "name_TE_hirarchiy.txt" #[requiered if prep_annotation] name of TE hirarchy file in data_input/library

    PARAMS:
        GENERAL:
            WORKING_DIRECTORY:  "" #[optional] path to working directory. Default: in the current directory
            PREFIX: "name_run" #[required] name of run
            MEMORY: 30000  #[required] Memory in mb to be used by the rules. If a rule does not work increase this number 
            MEMORY_SUPP:    20000 #[required]  If you use the --retries option of snakemake, if a rule fails to use memory, add to the memory this extra.
        COMPRESS:
            THREADS:    10  #[required] maximum number of threads the rule can use 
        SAMTOOLS:
            THREADS:    10 #[required] maximum number of threads the rule can use  
        PREP_CUSTOM:
            SPECIES: "" #Specify the species or clade of the input sequence. The species name must be a valid NCBI Taxonomy Database species name and be containedin the RepeatMasker repeat database. Some examples are: human,mouse,rattus,"ciona savignyi",arabidopsis,mammal, carnivore, rodentia, rat, cow, pig, cat, dog, chicken, fugu,danio, "ciona intestinalis" drosophila, anopheles, worm, diatoaea,artiodactyl, arabidopsis, rice, wheat, and maize
            CUTOFF: "" #[optional] SW cutoff score for RepeatMasker, default=250 
            FRAG: "" #[optional]  Maximum sequence length masked without fragmenting for RepepatMasker (default 60000)
            ENGINE: "" #[optional][crossmatch|wublast|abblast|ncbi|rmblast|hmmer] Use an alternate search engine to the default for RepeatMasker.
            MIN_LENGTH: "" #[optional] minimum length for RepeatMasker-predicted TE to be reported in the final annotation, default=200 
            SPLIT_DIST: "" #[optional] minimum length for RepeatMasker-predicted TE to be reported in the final annotation, default=200 
            DIVERGENCE: "" #[optional] only those repeats < x percent diverged from the consensus seq will be included in final annotation, default=20 
            THREADS:    16 #[required] maximum number of threads the rule can use  
        DISCOVER:
            LEVEL_HIERARCHY1:   "family" #[required] level of the hierarchy file to guide initial TE search. #NOTE: It is recommended that you use the lowest level in the hierarchy file (i.e. "family" for data without a user-curated hierarchy)
            LEVEL_HIERARCHY2:   "class" #[required] level of the hierarchy to group similar TEs.    #NOTE: This must be either the same level of the hierarchy used in -l1 or a higher level (clustering at higher levels will reduce the number of TE instances found, but improve accuracy for discriminating TE identity)
            QUALITY:    "20" #[required] map quality threshold #NOTE: Mapped reads with map qualities lower than this number will be discarded
            EXCLUDE:    "" #[optional] newline separated file containing the name of any TE families to exclude from analysis #NOTE: Use same names as in column one of the hierarchy file
            STANDARD_DEVIATION: "" #[optional] insert size standard deviation #NOTE: Used to manually override the insert size StdDev identified by samtools stat (check this number in the generated stats.txt file to ensure it seems more or less correct based on knowledge of sequencing library!)
            COVERAGE_OVERRIDE:  "" #[optional] coverage override #Note: Used to manually override the coverage estimate if you get the error: "Warning: coverage could not be estimated"
            THREADS:    16 #[required] maximum number of threads the rule can use  
        COLLAPSE:
            THRESHOLD_SAMPLE:   "1" #[required] TEs must be supported by >= n reads in at least one sample
            THRESHOLD_ALL:  "1" #[required] TEs must be supported by >= n reads summed across all samples
            COVERAGE_OVERRIDE:  "" #[optional] coverage override #Note: Used to manually override the coverage estimate if you get the error: "Warning: coverage could not be estimated"
            QUALITY:    "20" #[required] map quality threshold
            THREADS:    16 #[required] maximum number of threads the rule can use  
        COUNT:
            QUALITY:    "20" #[required] map quality threshold
            THREADS:    20 #[required] maximum number of threads the rule can use  
        GENOTYPE:
            THRESHOLD_LOWER:    "1" #[optinal] sites genotyped as -9 if adjusted read counts lower than this threshold, default=1
            THRESHOLD_HIGHER:  "100" #[optinal] sites genotyped as -9 if adjusted read counts higher than this threshold, default=mean_coverage + 2*STDEV
            DATAs an example, a cluster configuration file is provided, but it is not exhaustive and is specific to the cluster we have used A_TYPE: "pooled" #[required] must be either haploid, diploid, or pooled
            SAMPLE:
                THRESHOLD_ABSENCE:  "" #[optinal] Frequency threshold
                THRESHOLD_PRESENCE:   "" #[optinal] Frequency threshold
            POPULATION:
                FILE:  "" #[optional]  path to population file
                THRESHOLD_ABSENCE: "" #[optinal] Frequency threshold
                THRESHOLD_PRESENCE: "" #[optinal] Frequency threshold

The main parameters are:

* GENOME:  Fasta file containing the reference genome of the species of interest.
* LIBRARY: A Multifasta file containing the canonical sequence of transposable elements
* ANNOTATION: BED file containing the TE annotation in reference genome.
* LEVEL_HIERARCHY1/2, THEASHOLD_SAMPLE/ALL: Required thresholds to operate TEFLoN2
* QUALITY: Map quality threshold for each steap
* TOOLS: Path to the tools 
* THREADS: Number of threads to execute a step
* THRESHOLD : Threshold for data analysis
* DATA_TYPE: Type of data for different interpretations

Config Cluster
--------------

As an example, a cluster configuration file is provided, but it is not exhaustive and is specific to the cluster we have used
