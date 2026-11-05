===========
HTML report
===========

At the end of a run, TEFLoN2 writes a single, self-contained HTML file:

.. code-block:: none

	data_output_PREFIX/6-report/PREFIX.report.html

It has no external dependency (the graphics are drawn in the file itself): open it in any modern browser, copy it to a laptop,
or attach it to an e-mail. It summarises (1) the quality of the input data and (2) the TEFLoN2 results, taking the population
information into account when a population file is used.

The report is built by the ``teflon_report`` rule and can be disabled with ``PARAMS > REPORT > USE: 0``
(see :doc:`../executing/configure_parameter_file`).

Tabs
====

Overview
	Number of samples, populations and TE insertions, split into reference TEs and de novo insertions, and the list of the
	warnings raised while building the report.

Input quality
	One line per sample, from the ``samtools stats`` and coverage files of ``1-mapping``: mean coverage (before and after
	subsampling), percentage of mapped, properly paired and duplicated reads, insert size and read length. Samples that fall under a threshold are
	flagged. The default thresholds are:

	.. csv-table::
		:header: "Flag", "Default", "Parameter"
		:widths: 40 15 45

		"Mean coverage below", "5x", "``MIN_COVERAGE``"
		"Mapped reads below", "80 %", "``MIN_MAPPED``"
		"Properly paired reads below", "80 %", "``MIN_PROPERLY_PAIRED``"
		"Duplicates above", "30 %", "(fixed)"

	The table can be sorted and filtered.

TE landscape
	Number of insertions per TE order, per TE family and per sequence, split into reference TEs and de novo insertions.

Genome browser
	The insertions along the reference genome, with zoom, filters and, optionally, genes (see below).

Samples
	Composition of the calls of each sample (present, absent, heterozygous or polymorphic, no data), TE load (fully present
	insertions, reference and de novo), TE load against the mean coverage, and present insertions by TE order.

Populations (only with a population file)
	Insertions private to a population, fixed in all samples of a population, or shared; heatmap of the frequencies per
	population, sharing patterns between populations, site frequency spectrum, and the agreement between the two frequency
	estimates of TEFLoN2 (reads and samples, ``genotypes.txt`` against ``genotypes2.txt``).

PCA
	Principal component analysis of the samples from the TE genotypes, coloured by population.

.. note::

	The *Populations* and *PCA* tabs need the Python package ``numpy``. Without it the other tabs are still built and a message is shown.


Genome browser
==============

The *Genome browser* tab shows all the TE variants of one sequence at a time.

Navigation
----------

* **Zoom**: mouse wheel (centred on the cursor), double-click, or the ``+`` / ``−`` buttons.
* **Pan**: drag the view, or use the ``◀`` / ``▶`` buttons.
* **Region**: type ``2R:100,000-250,000`` (or a sequence name alone) in the region box and press Enter.
* **Overview**: the bar at the top shows the density of variants along the whole sequence and the current window; click it to jump.
* **Reset**: goes back to the whole sequence.

Tracks
------

TE variants
	Reference TEs are drawn as boxes spanning their interval, de novo insertions as triangles. Overlapping variants are stacked
	on several rows. When too many variants are in view to be drawn one by one, the track becomes a density histogram
	(blue: reference TEs, red: de novo insertions); click a bar to zoom in.

Frequency
	One lollipop per variant: the frequency of the TE-present allele, either over all samples or in one population
	(*frequency of* selector).

Genes
	Only when an annotation is provided (see below): exons (thin boxes), coding sequences (tall boxes), introns and the strand.
	Genes that contain at least one TE of the current selection are outlined in orange.

Filters and colours
-------------------

Variants can be filtered by type (reference TE or de novo insertion), TE order, family (text), frequency range and, with an annotation,
impact class. They can be coloured by TE order, TE family, type, frequency or impact.

Clicking a variant opens a panel with its position, type, family, order, the frequency in each population and the call of every sample,
grouped by population. Clicking a gene lists the TEs in or near it. The tables below the browser list the variants of the current
window (*Variants in view*) and, with an annotation, the genes that carry insertions.

.. note::

	Per-sample calls are embedded in the report only when the number of sites multiplied by the number of samples does not exceed
	three million; above that, the per-sample details are left out to keep the file small.

Impact on genes
---------------

Provide a gene annotation (GFF3 or GTF, optionally gzip-compressed) to see the genes and to classify every TE according to its position:

.. csv-table::
	:header: "Class", "Meaning"
	:widths: 25 75

	"CDS", "the site overlaps a coding sequence of a gene"
	"UTR / non-coding exon", "overlaps an exon but no coding sequence"
	"intron", "inside the gene body, outside the exons"
	"upstream", "within ``GENE_FLANK`` bp before the gene (strand-aware)"
	"downstream", "within ``GENE_FLANK`` bp after the gene (strand-aware)"
	"intergenic", "none of the above"

When a TE is related to several genes, the most severe class is kept (the order above), ties being broken by the distance.
A reference TE spans an interval and is classified with the whole interval, a de novo insertion is a point.

.. warning::

	This is a **positional annotation, not a functional prediction**. The reading frame, the orientation of the TE and the
	splice sites are not evaluated. Use it to prioritise candidates, not to conclude on the effect of an insertion.

Chromosome names in the annotation and in the genome are matched exactly, or ignoring a ``chr`` prefix. Only the sequences that carry TE
sites are shown in the browser. Annotation and genome are both assumed to use 1-based coordinates.

Configuration
-------------

In ``config.yaml``, under ``PARAMS > REPORT``:

.. code-block:: yaml

	PARAMS:
	  REPORT:
	    USE: 1
	    MIN_COVERAGE: 5
	    MIN_MAPPED: 80
	    MIN_PROPERLY_PAIRED: 80
	    GENE_ANNOTATION: "annotation/genes.gff3"   # optional: GFF3 or GTF (.gz allowed); "" = no genes
	    GENE_FLANK: 2000                           # bp, for upstream / downstream

The chromosome lengths are read from the reference genome (``DATA_INPUT > GENOME``); without it they are estimated from the data and a message is shown.
Both options can also be set with the interactive script (:doc:`../executing/interactive_configuration`).


Running the report on its own
=============================

.. code-block:: console

	$ snakemake --configfile config.yaml --cores 2 --allowed-rules teflon_report

or directly:

.. code-block:: console

	$ python3 TEFLoN/teflon_report.py -wd data_output_PREFIX -pop population.txt \
	      -f data_input/reference/genome.fasta --annotation genes.gff3 --flank 2000 \
	      -o data_output_PREFIX/6-report/PREFIX.report.html

``--no-browser`` leaves the Genome browser tab out.
