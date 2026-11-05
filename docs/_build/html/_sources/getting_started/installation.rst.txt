============
Installation
============


Before you can use TEFLoN2 , you will need to install its dependencies.
TEFLoN2 uses Python 3, BWA (Burrows-Wheeler Alignment Tool), Samtools, RepeatMasker and SnakeMake.


TEFLoN2
=======

TEFLON2 is installed on `Github repository <https://github.com/asfistonlavie/TEFLoN2>`_ or your console:

.. code-block:: console

	$ sudo apt update
	$ sudo apt install git
	$ git clone https://github.com/asfistonlavie/TEFLoN2.git



Dependencies
------------

.. _Python: https://www.python.org
.. _BWA: http://bio-bwa.sourceforge.net
.. _SAMtools: https://www.htslib.org
.. _RepeatMasker: https://www.repeatmasker.org/
.. _Snakemake: https://snakemake.readthedocs.io
.. _SingularityCE: https://sylabs.io/docs/

* Python_ ≥ 3
* BWA_ ≥ 0.7.17
* SAMtools_ ≥ 1.15
* RepeatMasker_ ≥ 4.1.2
* Snakemake_ ≥ 7.7.0
* SingularityCE_ 3.11.0

Using SingularityCE
-------------------

For install SingularityCE_, follow installation instructions on `SingularityCE site <https://docs.sylabs.io/guides/main/admin-guide/installation.html>`_.

A Singularity container is available with all tools compiled in. The Singularity file provided in this repo and can be compiled as such:

.. code-block:: console

	$ sudo singularity build TEFLoN.simg Singularity

if you can't use sudo :

.. code-block:: console

	singularity build --fakeroot TEFLoN.simg Singularity


Manually
--------

For manual installation, it is best to go directly to the tool documentation.

Python 3
^^^^^^^^

To check the version of your python :

.. code-block:: console

	$ python --version

If python < 3, install python 3 on `their site <https://www.python.org/doc/>`_ or your console:

.. code-block:: console

	$ sudo apt update
	$ sudo apt install python3

If all went well you now have python 3 on your computer.


Burrows-Wheeler Alignment Tool (BWA)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your computer has bwa installed, check the version of your bwa :

.. code-block:: console

	$ bwa

If bwa is not installed or version <  0.7.17 :


.. code-block:: console

	$ sudo apt update
	sudo apt -y install bwa

Recheck bwa version and if there are any problems, go to the `bwa site <https://bio-bwa.sourceforge.net/>`_.

SAMtools
^^^^^^^^

If your computer has SAMtools installed, check the version of your SAMtools :

.. code-block:: console

	$ samtools --version

If samtools is not installed or SAMtools < 1.15, follow installation instructions on `samtools site <http://www.htslib.org/>`_.


RepeatMasker
^^^^^^^^^^^^

For install RepeatMasker_, follow installation instructions on `RepeatMasker site <http://www.repeatmasker.org/RepeatMasker/>`_.

SnakeMake
^^^^^^^^^


If your computer has SnakeMake installed, check the version of your SnakeMake :

.. code-block:: console

	$ snakemake --version

If SnakeMake is not installed or version < 7.7.0, follow installation instruction on `SnakeMake site <https://snakemake.readthedocs.io/en/stable/getting_started/installation.html>`_.