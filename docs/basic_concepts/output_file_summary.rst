====================
Output files summary
====================

Here is the structure of the output files obtained after running the pipeline.


.. code-block:: none

	WORK_DIRECTORY/data_output_PREFIX/
	├── 0-reference
	│	├── PREFIX.prep_MP
	│	│	├── PREFIX.annotatedTE.fa
	│	│	├── PREFIX.mappingRef.fa
	│	│	├── PREFIX.mappingRef.fa.amb
	│	│	├── PREFIX.mappingRef.fa.ann
	│	│	├── PREFIX.mappingRef.fa.bwt
	│	│	├── PREFIX.mappingRef.fa.pac
	│	│	├── PREFIX.mappingRef.fa.sa
	│	│	└── PREFIX.pseudo.fa
	│	├── PREFIX.prep_TF
	│	│   ├── PREFIX.genomeSize.txt
	│	│   ├── PREFIX.hier
	│	│   ├── PREFIX.pseudo2ref.txt
	│	│   ├── PREFIX.ref2pseudo.txt
	│	│   └── PREFIX.te.pseudo.bed
	│	└── PREFIX.prep_RM             ----------
	│	    ├── GENOME.fasta                    |
	│	    ├── GENOME.fasta.align              |
	│	    ├── GENOME.fasta.cat.gz             |--- Specific to prepration custom 
	│	    ├── GENOME.fasta.masked             |
	│	    ├── GENOME.fasta.out                |
	│	    ├── GENOME.fasta.tbl                |
	│	    └── PREFIX.bed             ----------
	├── 1-mapping
	│	├── averageLength.all.txt
	│	├── SAMPLE_NAME.sorted.bam
	│	├── SAMPLE_NAME.sorted.bam.bai
	│	├── SAMPLE_NAME.sorted.cov.txt
	│	├── SAMPLE_NAME.sorted.stats.txt
	│	├── SAMPLE_NAME.sorted.subsmpl.bam
	│	├── SAMPLE_NAME.sorted.subsmpl.bam.bai
	│	├── SAMPLE_NAME.sorted.subsmpl.cov.txt
	│	└── SAMPLE_NAME.sorted.subsmpl.stats.txt
	├── 3-countPos
	│	├── SAMPLE_NAME.all_positions_sorted.collapsed.txt
	│	├── SAMPLE_NAME.all_positions_sorted.txt
	│	├── SAMPLE_NAME.all_positions.txt
	│	├── SAMPLE_NAME.counts.txt
	│	├── SAMPLE_NAME.pseudoSpace.genotypes.txt
	│	├── union_sorted.collapsed.txt
	│	├── union_sorted.txt
	│	└── union.txt
	├── 4-genotypes
	│	├── samples
	│	│	├── pseudoSpace
	|	|	│	└── SAMPLE_NAME.pseudoSpace.genotypes.txt
	|	|	├── SAMPLE_NAME.genotypes.txt
	|	|	├── all_samples.genotypes.txt
	|	|	└── all_samples.genotypes2.txt
	|	└── populations                                  ----------
	| 	    ├── NAME_POP.population.genotypes2.txt                |
	|	    ├──	NAME_POP.population.genotypes.txt                 |--- If you use population file
	│	    ├── all_frequency.population.genotypes2.txt           |
	│	    └── all_frequency.population.genotypes.txt   ----------
	└── sample_names.txt



Most useful output
------------------

The most useful output files are : WORK_DIRECTORY/data_output_PREFIX/4-genotypes//samples/SAMPLE_NAME.genotypes.txt


.. csv-table:: SAMPLE_NAME.genotypes.txt
	:header: chr, 5' breakpoint, 3' breakpoint, Level 1,Level 2, Stand, Reference TE ID, 5' soft-clipped reads, 3' soft-clipped reads, Presence reads, Abscence reads, Ambiguous reads, Genotype, Interpretation ,Identifier TE
	:widths: 15 10 30 30 30 30 30 30 30 30 30 30 30 30 30

	2R,38145,\-,gate,ltr,\-,\-,\+,\-,1,0,0,1.0,present,te01
	2R,38145,\-,rt1b,non-ltr,.,\-,\+,\-,1,0,0,1.0,present,te02
	2R,21076732,21077084,ine-1,helitron,\-,FBti0061454,\+,\-,0,5,0,1.0,absent,te352




#. chromosome
#. 5' breakpoint estimate ("-" if estimate not available)
#. 3' breakpoint estimate ("-" if estimate not available)
#. search level id (Usually TE family)
#. cluster level id (Usually TE order or class)
#. strand ("." if strand could not be detected)
#. reference TE ID ("-" if novel insertion)
#. 5' breakpoint is supported by soft-clipped reads (if TRUE "+" else "-")
#. 3' breakpoint is supported by soft-clipped reads (if TRUE "+" else "-")
#. read count for "presence reads"
#. read count for "absence reads"
#. read count for "ambiguous reads"
#. genotype for every TE (allele frequency for pooled data, present/absent/no_data for haploid, present/absent/heterozygous/no_data for diploid)
#. frequency interpretation (for pooled data, present/absent/no_data for haploid, present/absent/heterozygous/no_data for diploid)
#. numbered identifier for each TE in the population



If you use population file, output file are :  WORK_DIRECTORY/data_output_PREFIX/4-genotypes//populations/SAMPLE_POP.genotypes.txt

.. csv-table:: SAMPLE_POP.genotypes.txt
	:header: chr, 5' breakpoint, 3' breakpoint, Level 1,Level 2, Stand, Reference TE ID, 5' soft-clipped reads, 3' soft-clipped reads, Presence reads, Abscence reads, Ambiguous reads, No data sample , Genotype, Interpretation ,Identifier TE
	:widths: 15 10 30 30 30 30 30 30 30 30 30 30 30 30 30 30

	2R,38145,\-,gate,ltr,\-,\-,\+,\-,3,0,0,0,1.0,present,te01
	2R,38145,\-,rt1b,non-ltr,.,\-,\+,\-,4,4,0,0,1.0,polymorphic,te02
	2R,21076732,21077084,ine-1,helitron,\-,FBti0061454,\+,\-,0,7,0,1,1.0,absent,te352




#. chromosome
#. 5' breakpoint estimate ("-" if estimate not available)
#. 3' breakpoint estimate ("-" if estimate not available)
#. search level id (Usually TE family)
#. cluster level id (Usually TE order or class)
#. strand ("." if strand could not be detected)
#. reference TE ID ("-" if novel insertion)
#. 5' breakpoint is supported by soft-clipped reads (if TRUE "+" else "-")
#. 3' breakpoint is supported by soft-clipped reads (if TRUE "+" else "-")
#. read count for "presence reads"
#. read count for "absence reads"
#. read count for "ambiguous reads"
#. sample considered as no data
#. genotype for every TE
#. frequency interpretation (present/absent/polymorphic/no_data)
#. numbered identifier for each TE in the population


If you use population file, output file are :  WORK_DIRECTORY/data_output_PREFIX/4-genotypes//populations/SAMPLE_POP.genotypes2.txt

.. csv-table:: SAMPLE_POP.genotypes2.txt
	:header: chr, 5' breakpoint, 3' breakpoint, Level 1,Level 2, Stand, Reference TE ID, 5' soft-clipped reads, 3' soft-clipped reads, Presence reads, Abscence reads, Ambiguous reads, No data sample , Genotype, Interpretation ,Identifier TE
	:widths: 15 10 30 30 30 30 30 30 30 30 30 30 30 30 30 30

	2R,38145,\-,gate,ltr,\-,\-,\+,\-,4,0,0,0,1.0,present,te01
	2R,38145,\-,rt1b,non-ltr,.,\-,\+,\-,2,2,0,0,1.0,polymorphic,te02
	2R,21076732,21077084,ine-1,helitron,\-,FBti0061454,\+,\-,0,3,0,1,1.0,absent,te352




#. chromosome
#. 5' breakpoint estimate ("-" if estimate not available)
#. 3' breakpoint estimate ("-" if estimate not available)
#. search level id (Usually TE family)
#. cluster level id (Usually TE order or class)
#. strand ("." if strand could not be detected)
#. reference TE ID ("-" if novel insertion)
#. 5' breakpoint is supported by soft-clipped reads (if TRUE "+" else "-")
#. 3' breakpoint is supported by soft-clipped reads (if TRUE "+" else "-")
#. sample count considered as present
#. sample count considered as heterozygous
#. sample count considered as absent
#. sample considered as no data
#. genotype for every TE
#. frequency interpretation (present/absent/polymorphic/no_data)
#. numbered identifier for each TE in the population