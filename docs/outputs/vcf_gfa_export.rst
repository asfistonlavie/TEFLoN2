==================
VCF and GFA export
==================

In addition to the historical text files (see :doc:`output_file_summary`), TEFLoN2 writes two
standard files in ``data_output_PREFIX/5-export/``:

.. code-block:: none

	data_output_PREFIX/5-export/
	├── PREFIX.TE_genotypes.vcf          multi-sample VCF 4.2, one record per TE insertion site
	├── PREFIX.TE_genotypes.vcf.gz       (optional, EXPORT > COMPRESS: 1) bgzip-compressed VCF
	├── PREFIX.TE_genotypes.vcf.gz.tbi   (optional) tabix index
	└── PREFIX.TE_genotypes.gfa          GFA 1.0 genotyping graph

They are produced by the ``teflon_export`` rule from the per-sample files of ``4-genotypes/samples/``
and use the **reference coordinates** (the pseudo-space coordinates of the intermediate files are converted back).
Coordinates are 1-based, like in the VCF specification.

The export can be disabled with ``PARAMS > EXPORT > USE: 0`` in the configuration file
(see :doc:`../executing/configure_parameter_file`).


VCF
===

Records
-------

One record per TE insertion site. The same site is represented in two ways, depending on whether the TE
is already annotated in the reference genome:

.. csv-table::
	:header: "TE", "ALT", "SVTYPE", "Allele 1 means"
	:widths: 25 20 15 40

	"Absent from the reference (de novo insertion)", "``<INS:ME:FAMILY>``", "INS", "the TE is **present** in the sample"
	"Annotated in the reference (reference TE)", "``<DEL:ME:FAMILY>``", "DEL", "the TE is **absent** from the sample"

For a reference TE the reference allele carries the TE, so the alternative allele is its absence. This is the usual
convention for mobile-element deletions, and it is the reason why ``INFO/TEAF`` (below) is always expressed as the frequency
of the *TE-present* allele, whatever the record type.

``POS`` is the 5' breakpoint (the start of the reference TE for ``DEL``), ``REF`` is the reference base read from the
genome FASTA at ``POS``, ``QUAL`` and ``FILTER`` are ``.``, and ``INFO/END`` is the 3' breakpoint (equal to ``POS`` for an insertion whose second breakpoint is unknown).

INFO fields
-----------

.. csv-table::
	:header: "Field", "Type", "Description"
	:widths: 15 10 75

	"SVTYPE", "String", "``INS``: TE absent from the reference; ``DEL``: TE annotated in the reference"
	"END", "Integer", "End position of the site"
	"SVLEN", "Integer", "Length of the reference interval spanned by the TE (negative, ``DEL`` only)"
	"TEID", "String", "TEFLoN2 identifier of the insertion (last column of the genotype files, e.g. ``te352``)"
	"TEFAM", "String", "TE family (hierarchy level 1)"
	"TEORDER", "String", "TE order / class (hierarchy level 2)"
	"STRAND", "String", "TE orientation (``.`` if unknown)"
	"REFTE", "Flag", "The insertion matches a TE annotated in the reference"
	"REFID", "String", "Identifier of the matching reference TE"
	"NS", "Integer", "Number of samples with data"
	"TEAF", "Float", "Frequency of the TE-present allele across the samples (present = 1, heterozygous or polymorphic = 0.5, absent = 0, no data ignored)"
	"TEAF_<population>", "Float", "Read-based frequency of the TE-present allele in each population (only when a population file is used)"

FORMAT fields
-------------

.. csv-table::
	:header: "Field", "Type", "Description"
	:widths: 10 10 80

	"GT", "String", "Genotype (allele 1 = TE present for ``INS``, TE absent for ``DEL``)"
	"AF", "Float", "Frequency of TE-present reads in the sample (``.`` if no data)"
	"PR", "Integer", "Number of reads supporting the presence of the TE"
	"AR", "Integer", "Number of reads supporting the absence of the TE"
	"AM", "Integer", "Number of ambiguous reads"

The genotype depends on ``DATA_TYPE`` (``PARAMS > GENOTYPE > DATA_TYPE``):

.. csv-table::
	:header: "Data type", "Present", "Absent", "Heterozygous", "Polymorphic", "No data"
	:widths: 15 15 15 20 20 15

	"haploid", "``1``", "``0``", "-", "-", "``.``"
	"diploid", "``1/1``", "``0/0``", "``0/1``", "-", "``./.``"
	"pooled", "``1``", "``0``", "-", "``.`` (see ``AF``)", "``.``"

For pooled samples the allele frequency of the pool is in ``FORMAT/AF``; a polymorphic call has no meaningful hard genotype,
so ``GT`` is missing.
For ``DEL`` records the allele numbers are swapped as explained above (a sample where the reference TE is present is ``0``).

Example
-------

.. code-block:: none

	##fileformat=VCFv4.2
	##ALT=<ID=INS:ME,Description="Insertion of a mobile element absent from the reference">
	##ALT=<ID=DEL:ME,Description="Mobile element annotated in the reference; ALT = absent from the sample">
	#CHROM  POS       ID     REF  ALT             QUAL  FILTER  INFO                                                                                                FORMAT           S1             S2
	2R      38145     te01   T    <INS:ME:gate>   .     .       SVTYPE=INS;END=38145;TEID=te01;TEFAM=gate;TEORDER=ltr;STRAND=.;NS=2;TEAF=1                         GT:AF:PR:AR:AM   1:1.0:1:0:0    1:1.0:3:0:0
	2R      21076732  te352  A    <DEL:ME:ine-1>  .     .       SVTYPE=DEL;END=21077084;SVLEN=-352;REFTE;REFID=FBti0061454;TEID=te352;TEFAM=ine-1;TEORDER=helitron  GT:AF:PR:AR:AM   1:1.0:0:5:0    0:0.0:4:0:0

(The example is shortened and aligned for readability; the real file is tab separated and also has a ``##contig`` line per sequence, ``##INFO`` / ``##FORMAT`` definitions and one ``##TEFLoN2_datatype`` line.)

Using the VCF
-------------

The file is read by the usual tools (``bcftools``, ``tabix``, ``pysam``, IGV, ...):

.. code-block:: console

	$ bcftools query -f '%CHROM\t%POS\t%INFO/TEFAM\t%INFO/TEAF\n' PREFIX.TE_genotypes.vcf
	$ bcftools view -i 'INFO/TEAF>=0.5 && INFO/SVTYPE="INS"' PREFIX.TE_genotypes.vcf
	$ bcftools view -s SAMPLE1,SAMPLE2 PREFIX.TE_genotypes.vcf

Because the TE alleles are symbolic, tools that expect sequence alleles (for example to predict consequences on the protein)
cannot interpret them. The positional impact on genes is given by the genome browser of the :doc:`html_report`.

Compression (``COMPRESS: 1``) needs ``bgzip`` and ``tabix`` (HTSlib).


GFA
===

The graph (GFA 1.0) summarises the TE insertions and the genotype of each sample as paths through the reference.

.. csv-table::
	:header: "Line", "Content"
	:widths: 10 90

	"``S``", "Backbone segments named ``<chrom>_<n>``: the reference intervals between two consecutive breakpoints. The sequence is ``*`` and the length is in ``LN``. One segment per de novo TE, named after its identifier (``te01``), with the tags ``TF`` (family), ``TO`` (order) and ``AF`` (frequency)."
	"``L``", "Link between consecutive backbone segments (the reference path). A de novo TE is inserted by two links between the flanking segments. A reference TE is skipped by a *bypass link* (tags ``TE``, ``TF``, ``TO``), the reference interval staying in the backbone."
	"``P``", "``REF_<chrom>``: the reference path. ``<sample>_<chrom>``: the path of a sample, which crosses the TEs it carries and skips the reference TEs that are absent from it."

Paths of the samples are written when ``PARAMS > EXPORT > GFA_PATHS`` is ``"samples"`` (default). The file can become large
for hundreds of samples; use ``"reference"`` to write only the reference path and keep the graph itself.

Rules used for the sample paths:

* present de novo TE: the path goes through the TE segment;
* absent reference TE: the path takes the bypass link;
* heterozygous, polymorphic and no-data calls follow the reference allele.

.. note::

	The TE segments have no nucleotide sequence (``*``): TEFLoN2 does not reconstruct the inserted sequence.
	Known limitations: two directly adjacent absent reference TEs, and a de novo TE exactly on the boundary of an absent
	reference TE, cannot both be represented as separate bypasses. Nested TEs are not resolved.

The file follows the GFA 1.0 specification and can be inspected with graph viewers that accept GFA 1.0
(such as Bandage) or loaded in pangenome toolkits that read ``S``, ``L`` and ``P`` lines.
This export has been checked for internal consistency only, not with every external tool.


Running the export on its own
=============================

Both files are produced by the Snakemake rule ``teflon_export``. To (re)generate them without running the rest of the pipeline:

.. code-block:: console

	$ snakemake --configfile config.yaml --cores 2 --allowed-rules teflon_export

The script can also be called directly:

.. code-block:: console

	$ python3 TEFLoN/teflon_export.py -wd data_output_PREFIX -s data_output_PREFIX/sample_names.txt \
	      -f data_input/reference/genome.fasta -dt diploid \
	      --vcf out.vcf --gfa out.gfa --gfa-paths samples \
	      --pop-freq data_output_PREFIX/4-genotypes/populations/all_frequency.population.genotypes.txt
