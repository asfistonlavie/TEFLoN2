# TEFLoN2

**Detection, genotyping and frequency estimation of transposable element (TE) variants from short paired-read data, in single samples or in large population datasets.**

TEFLoN2 is a [Snakemake](https://snakemake.readthedocs.io) pipeline derived from [TEFLoN](https://doi.org/10.1093/gbe/evx073). It maps paired-end reads, finds the TE breakpoints of each sample, builds a catalog of TE polymorphisms, report the TE population diversity, genotypes every site in every sample and estimates the frequency of each TE variant in each population. Results are now exported as a standard VCF, a GFA graph and a self-contained interactive HTML report.

Full documentation: <https://teflon2.readthedocs.io/en/latest/>

[Overview](#overview) · [Installation](#installation) · [Quick start](#quick-start) · [Outputs](#outputs) · [Code of conduct](#code-of-conduct) · [Licence](#licence) · [Citation](#citation)

---

## Overview

TEFLoN2 runs the following steps in order. Each step writes its results in a numbered folder of `data_output_PREFIX/`.

| # | Step | What it does | Output folder |
|---|------|--------------|---------------|
| 0 | **Data preparation** | Builds the mapping reference: the reference genome without its TEs, plus the TE library sequences | `0-reference` |
| 1 | **Mapping** | Maps the paired-end reads of each sample (BWA, SAMtools); optional quality filtering with fastp | `1-mapping` |
| 2 | **Discover** | Finds the putative TE breakpoints of each sample | `2-preliminaryResults` |
| 3 | **Collapse** | Filters the breakpoints and builds the catalog of TE insertions | `3-countPos` |
| 3 | **Count** | Counts the reads supporting the presence or the absence of each insertion | `3-countPos` |
| 4 | **Genotype (sample)** | Genotypes each insertion in each sample (haploid, diploid or pooled) | `4-genotypes` |
| 4 | **Genotype (population)** | Estimates the frequency of each insertion per population (needs a population file) | `4-genotypes` |
| 5 | **Export** | Writes the VCF and the GFA | `5-export` |
| 6 | **Report** | Builds the interactive HTML report | `6-report` |

Two modes are available, depending on where the TE annotation comes from:

* **prep_annotation**: you provide an annotation of the TEs of the reference (BED) and a TE library;
* **prep_custom**: TEFLoN2 annotates the reference itself with RepeatMasker and your TE library (for example the Dfam library downloaded by `install/install.sh`).

### Inputs

* a reference genome (`.fasta`);
* short paired-end reads (`.fastq(.gz)`) and/or alignments (`.bam`);
* a TE annotation of the reference (`.bed`) and/or a TE library (`.fasta`);
* optionally, a population file and a gene annotation (GFF3/GTF) for the report.

---

## Installation

Requirements: Python 3, AWK, BWA ≥ 0.7.17, SAMtools ≥ 1.15, Snakemake ≥ 7.7.0. Optional: RepeatMasker ≥ 4.1.2, fastp, numpy (population statistics and PCA in the report), bgzip and tabix (compressed and indexed VCF). Tested on Linux (Ubuntu); a Singularity container with all tools is also provided.

```bash
git clone https://github.com/asfistonlavie/TEFLoN2.git
cd TEFLoN2
bash install/install.sh        # checks the tools and downloads the Dfam TE library
```

Details: <https://teflon2.readthedocs.io/en/latest/getting_started/installation.html>

---

## Quick start

```bash
python3 teflon2_configure.py                                       # answer a few questions: writes config.yaml
snakemake --configfile config.yaml -s Snakefile -np -j $MAX_JOBS   # dry run: lists what will be done
snakemake --configfile config.yaml -s Snakefile -p  -j $MAX_JOBS   # real run
```

A small test dataset is provided in `data_input_test/` (see the documentation page *Test TEFLoN2*). On a cluster, adapt `cluster.yaml` and `submitifb.sh`.

---

## Outputs

* **VCF 4.2** (`5-export`): one record per TE site with symbolic alleles `<INS:ME:family>` and `<DEL:ME:family>`, ready for bcftools, VCFtools or scikit-allel.
* **GFA 1.0** (`5-export`): the reference cut at the TE sites, usable as a graph representation of the polymorphisms.
* **HTML report** (`6-report`): a single file, with no server needed, that summarizes the input quality, the genotyping results and the population information, and includes a **genome browser** (zoomable view of the TE variants along the reference, with an optional gene annotation to see the positional impact of each variant).

Details: <https://teflon2.readthedocs.io/en/latest/outputs/output_file_summary.html>

---

## Code of conduct

We want TEFLoN2 to be a welcoming project for everyone, whatever their experience, gender, origin or background. By taking part (issues, discussions, pull requests), you agree to:

* be respectful and kind, and accept that people have different levels of expertise;
* give and receive constructive criticism gracefully, focusing on the code and the science, not on the person;
* not use harassing, discriminatory, insulting or sexualized language or behaviour;
* not publish private information of others without their consent.

Maintainers may edit or remove contributions that do not follow these rules and may restrict participation of people who repeatedly break them. To report a problem, contact the maintainer at **anna.fiston@gmail.com** (all reports are treated confidentially).

This code of conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.1.

### Contributing and support

Bugs and questions: please open an [issue](https://github.com/asfistonlavie/TEFLoN2/issues) with your TEFLoN2 version, your command line and the relevant log files from `.logs/`. Pull requests are welcome.

> TEFLoN2 is released under the GPL-3.0. See the [LICENSE](LICENSE) file.

--
## Citation

If you use TEFLoN2, please cite the TEFLoN2 article and the original TEFLoN article.

**TEFLoN2**

> Fiston-Lavier A.-S., Marco C., Chenal C, Fontaine M. Accurate genotyping and frequency estimation of transposable elements using short-reads in large population datasets: A case study of 200 Pan-Anopheles samples. 

Source code: <https://github.com/asfistonlavie/TEFLoN2>

**TEFLoN**

> Adrion J.R., Song M.J., Schrider D.R., Hahn M.W., Schaack S. (2017). Genome-wide estimates of transposable element insertion and deletion rates in *Drosophila melanogaster*. *Genome Biology and Evolution* 9(5): 1329-1340.

**Tools used by TEFLoN2**

* Snakemake: Mölder F. *et al.* (2021). Sustainable data analysis with Snakemake. *F1000Research* 10: 33.
* Dfam (if you use the downloaded library): Storer J., Hubley R., Rosen J., Wheeler T.J., Smit A.F. (2021). The Dfam community resource of transposable element families, sequence models, and genome annotations. *Mobile DNA* 12: 2. Please also give the Dfam release saved in `DFAM_VERSION.json`.
* RepeatMasker (if you use it): see <https://www.repeatmasker.org/>.
