.. TEFLoN2 documentation master file, created by
   sphinx-quickstart on Wed Oct  5 11:10:24 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TEFLoN2's documentation!
============================================

TEFLoN2 is an improvement of `TEFLoN <https://github.com/jradrion/TEFLoN>`_. All improvements will allow it to be up to date, easier to use and more efficient.

Like TEFLoN, TEFLoN2 uses paired-end illumina sequence data to both discover transposable elements (TEs) and perform TE genotyping.

TEFLoN2 requires to prepare a specific mapping dataset (cf. figure 1.A). Then, one launches four individually automated scripts :
It (cf. figure 1.B) detects all TE insertions (de novo and references TEs), then filter out low quality data to create a catalog of TE insertion, genotype them and finally estime their allele frequency.

.. image:: images/TEFLoN2_architecture.png

TEFLoN2 can be run on high performance computers (bigmem), cluster or HPC cluste.

---------------
Getting started
---------------

.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 1

   getting_started/installation
   getting_started/teflon2_tutorial




.. toctree::
   :caption: Basic concepts
   :name: basic_concepts
   :hidden:
   :maxdepth: 1

   basic_concepts/steps_of_TEFLoN2
   basic_concepts/output_file_summary


.. toctree::
   :caption: Executing
   :name: executing
   :hidden:
   :maxdepth: 1

   executing/configure_parameter_file.rst
   executing/command_line_interface.rst

.. toctree::
   :caption: Project Info
   :name: project_info
   :hidden:
   :maxdepth: 1

   project_info/citations.rst