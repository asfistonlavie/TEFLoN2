================
Steps of TEFLoN2
================

.. _RepeatMasker: https://www.repeatmasker.org/

Inputs
------

Required input data to TEFLoN2 are :

* Reference genome (.fasta)
* Short paired-end reads (.fastq(.gz)) or/and binary alignment map (.bam)
* Annotation of TE insertions in the reference (.bed6) or/and TE library (.fasta)

.. code-block:: none

	data_input/
	├── library
	│	├── sample_reference_hierarchy.txt
	│	├── REFERENCE_TE_ANNOTATION.bed
	│	└── TE_LIBRARY.fasta
	├── reference
	│	└── REFERENCE_GENOME.fasta [required]
	└── samples
	    ├── bam
	    │	└── SAMPLE_NAME.bam
	    ├── reads
	    │	└── SAMPLE_NAME.[fastq fq](.gz)
	    ├── reads1
	    │	└── SAMPLE_NAME[. _][1 r1 R1].[fastq fq](.gz)
	    └── reads2
	        └── SAMPLE_NAME[. _][2 r2 R2].[fastq fq](.gz)


TEFLoN2 requires to prepare a specific mapping dataset. 
It detects all TE insertions (de novo and references TEs), then
filter out low quality data to create a catalog of TE insertion, genotype them and finally estime their allele frequency.


Data preparation
----------------

Depending on the input you have TEFLoN2 uses teflon_preparation_annotation or teflon_preparation_custom.


Preparation annotation - With TEs annotation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you use annotation of the TE insertions known to be present in the reference, TEFLoN2 will use teflon_prep_annotation.

You should organize your files as follows:

.. code-block:: none

	data_input/
	├── library
	│	├── sample_reference_hierarchy.txt [required]
	│	├── REFERENCE_TE_ANNOTATION.bed [required]
	│	└── TE_LIBRARY.fasta [optional]
	├── reference
	│	└── REFERENCE_GENOME.fasta [required]
	└── samples
	    ├── bam
	    │	└── SAMPLE_NAME.bam
	    ├── reads
	    │	└── SAMPLE_NAME.[fastq fq](.gz)
	    ├── reads1
	    │	└── SAMPLE_NAME[. _][1 r1 R1].[fastq fq](.gz)
	    └── reads2
	        └── SAMPLE_NAME[. _][2 r2 R2].[fastq fq](.gz)

In this step, TEFLoN2 uses the TE annotations to extract the sequences from the reference and then generated a TE library with these TE sequences. It removes them from the reference and keeps the information of their positions in the reference. 

Here is the structure of the output files obtained after the execution of Preparation annotation step.

.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	└── 0-reference
		├── PREFIX.prep_MP
		│	├── PREFIX.annotatedTE.fa
		│	├── PREFIX.mappingRef.fa
		│	├── PREFIX.mappingRef.fa.amb
		│	├── PREFIX.mappingRef.fa.ann
		│	├── PREFIX.mappingRef.fa.bwt
		│	├── PREFIX.mappingRef.fa.pac
		│	├── PREFIX.mappingRef.fa.sa
		│	└── PREFIX.pseudo.fa
		└── PREFIX.prep_TF
		    ├── PREFIX.genomeSize.txt
		    ├── PREFIX.hier
		    ├── PREFIX.pseudo2ref.txt
		    ├── PREFIX.ref2pseudo.txt
		    └── PREFIX.te.pseudo.bed

The most useful output is PREFIX.mappingRef.fa composed of the reference sequence without TE and TE sequences.

Preparation custom - Without TEs annotation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you do not use TE annotation of the reference, you will have to use a TE library.

You should organize your files as follows:

.. code-block:: none

	data_input/
	├── library
	│	└── TE_LIBRARY.fasta [required]
	├── reference
	│	└── REFERENCE_GENOME.fasta [required]
	└── samples
	    ├── bam
	    │	└── SAMPLE_NAME.bam
	    ├── reads
	    │	└── SAMPLE_NAME.[fastq fq](.gz)
	    ├── reads1
	    │	└── SAMPLE_NAME[. _][1 r1 R1].[fastq fq](.gz)
	    └── reads2
	        └── SAMPLE_NAME[. _][2 r2 R2].[fastq fq](.gz)


In this step, TEFLoN2 uses RepeatMasker which, together with the TE consensus library, masks the TE sequences of the reference and then removes them.

Here is the structure of the output files obtained after the execution of Preparation custom step.

.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	└── 0-reference
		├── PREFIX.prep_MP
		│	├── PREFIX.annotatedTE.fa
		│	├── PREFIX.mappingRef.fa
		│	├── PREFIX.mappingRef.fa.amb
		│	├── PREFIX.mappingRef.fa.ann
		│	├── PREFIX.mappingRef.fa.bwt
		│	├── PREFIX.mappingRef.fa.pac
		│	├── PREFIX.mappingRef.fa.sa
		│	└── PREFIX.pseudo.fa
		├── PREFIX.prep_TF
		│   ├── PREFIX.genomeSize.txt
		│   ├── PREFIX.hier
		│   ├── PREFIX.pseudo2ref.txt
		│   ├── PREFIX.ref2pseudo.txt
		│   └── PREFIX.te.pseudo.bed
		└── PREFIX.prep_RM
		    ├── GENOME.fasta
		    ├── GENOME.fasta.align
		    ├── GENOME.fasta.cat.gz
		    ├── GENOME.fasta.masked
		    ├── GENOME.fasta.out
		    ├── GENOME.fasta.tbl
		    └── PREFIX.bed


The most useful output is PREFIX.mappingRef.fa composed of the reference sequence without TE and TE sequences.

Mapping
^^^^^^^

Mapping step maps the short paired-end reads (.fastq) on PREFIX.mappingRef.fa.


Here is the structure of the output files obtained after the execution of Mapping step.

.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	├── 1-mapping
	│	├── SAMPLE_NAME.sorted.bam
	│	└── SAMPLE_NAME.sorted.bam.bai
	└── sample_names.txt


We obtain a `binary alignment map <https://support.illumina.com/help/BS_App_RNASeq_Alignment_OLH_1000000006112/Content/Source/Informatics/BAM-Format.htm>`_ (BAM) for each sample.

Discover
--------

Discover step detects potential putative TE breakpoints in each sample. 

To do this, it uses information from the alignment files (BAM): `flags and CIGAR <https://en.wikipedia.org/wiki/SAM_(file_format)>`_ of each read.

3 situations are possible:

#. Both readings of the pair map with the reference. There is no putative TE breakpoints.
#. The two reads do not map. No information can be deduced.
#. One of the two reads maps to the reference and the other to a consensus sequence of TEs. A putative TE breakpoints is at this loci, which may or may not be present in the reference.


Here is the structure of the output files obtained after the execution of Discover step.

.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	├── 1-mapping
	│	├── SAMPLE_NAME.sorted.cov.txt
	│	├── SAMPLE_NAME.sorted.stats.txt
	└── 3-countPos
		├── SAMPLE_NAME.all_positions_sorted.txt
		└── SAMPLE_NAME.all_positions.txt

We obtain all positions of putative TE breakpoints (SAMPLE_NAME.all_positions_sorted.txt) in each sample.

Collapse
--------

Collapse step filters putatve TE breakpoints at the individual and then at the population level.
The user must define two thresholds: 

#. An individual threshold that defines for each individual the number of reads that must support the insertion to retain it.
#. A population threshold which defines the number of reads that must support the insertion in all individuals, to retain it. 

It creates subsamples of the same depth of each sample. These subsamples will be used in Count step.


Here is the structure of the output files obtained after the execution of Collapse step.


.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	├── 1-mapping
	│	├── averageLength.all.txt
	│	├── SAMPLE_NAME.sorted.subsmpl.bam
	│	├── SAMPLE_NAME.sorted.subsmpl.bam.bai
	│	├── SAMPLE_NAME.sorted.subsmpl.cov.txt
	│	└── SAMPLE_NAME.sorted.subsmpl.stats.txt
	└── 3-countPos
		├── SAMPLE_NAME.all_positions_sorted.collapsed.txt
		├── union_sorted.collapsed.txt
		├── union_sorted.txt
		└── union.txt


The most useful output is union_sorted.collapsed.txt composed of all TE breakpoints of all sample also known as the catalog of putative TE breakpoints. 


Count
-----

Count step examine reads flanking the TE breakpoints and genotype them according to their support of presence/absence of TE for each sample.


Here is the structure of the output files obtained after the execution of Count step.

.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	├── 1-mapping
	└── 3-countPos
		└── SAMPLE_NAME.counts.txt


Genotype (sample)
-----------------

Genotype (sample) step gather all the information and estimate the allelic frequency of each TE breakpoints for each sample.

Here is the structure of the output files obtained after the execution of Genotype step.

.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	├── 1-mapping
	├── 3-countPos
	└── 4-genotypes
		└── samples
			├── pseudoSpace
			│	└── SAMPLE_NAME.pseudoSpace.genotypes.txt
			├── SAMPLE_NAME.genotypes.txt
			├── all_samples.genotypes.txt
			└── all_samples.genotypes2.txt



Genotype (population)
---------------------

If you use population file, Genotype (population) step gather all the information and estimate the population frequency of each TE insertion for each population.


.. code-block:: none
	
	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	├── 1-mapping
	├── 3-countPos
	└── 4-genotypes
		├── samples
		|	└── pseudoSpace
		└── populations
	 	    ├── NAME_POP.population.genotypes2.txt
		    ├──	NAME_POP.population.genotypes.txt
		    ├── all_frequency.population.genotypes2.txt
		    └── all_frequency.population.genotypes.txt
