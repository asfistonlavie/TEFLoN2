============
Installation
============


Before using TEFLoN2, you need to install its dependencies. TEFLoN2 uses Python 3, BWA (Burrows-Wheeler Alignment Tool), Samtools, RepeatMasker, and Snakemake. It has been successfully tested on Linux/Ubuntu platforms.

TEFLoN2
=======

TEFLoN2 can be installed from the `Github repository <https://github.com/asfistonlavie/TEFLoN2>`_ or directly via the terminal:   

.. code-block:: console

	$ sudo apt update
	$ sudo apt install git
	$ git clone https://github.com/asfistonlavie/TEFLoN2.git
	$ cd TEFLoN2



Dependencies
------------

.. _Python: https://www.python.org
.. _AWK: https://www.gnu.org/software/gawk/manual/gawk.html
.. _BWA: http://bio-bwa.sourceforge.net
.. _SAMtools: https://www.htslib.org
.. _RepeatMasker: https://www.repeatmasker.org/
.. _Snakemake: https://snakemake.readthedocs.io
.. _SingularityCE: https://sylabs.io/docs/

* Python_ ≥ 3
* AWK_ ≥ 5.1.0
* BWA_ ≥ 0.7.17
* SAMtools_ ≥ 1.15
* RepeatMasker_ ≥ 4.1.2 (optional)
* Snakemake_ ≥ 7.7.0


Using SingularityCE (optional)
------------------------------

To install SingularityCE ≥ 3.11.0, follow the instructions on the official website `SingularityCE site <https://docs.sylabs.io/guides/main/admin-guide/installation.html>`_.

A Singularity container is available with all the required tools precompiled. You can build the container using the provided Singularity file in the repository:

.. code-block:: console

	$ sudo singularity build TEFLoN2.simg Singularity_TEFLoN2_[Custom,Annotation]

If you do not have sudo privileges:

.. code-block:: console

	singularity build --fakeroot TEFLoN2.simg Singularity_TEFLoN2_[Custom,Annotation]

After, to use the TEFLoN2.simg container, you have to use :

.. code-block:: console

	singularity exec TEFLoN2.simg snakemake --configfile config.yaml -s Snakefile -p -j $MAX_JOBS


Manual installation
-------------------

For manual installation, we recommend following the installation guides provided by each tool.

Python 3
^^^^^^^^

Check your current Python version:

.. code-block:: console

	$ python --version

If your version is < 3, install Python 3 `<https://www.python.org/doc/>`_ from python.org or via terminal:


.. code-block:: console

	$ sudo apt update
	$ sudo apt install python3

If all went well you now have python 3 on your computer.


BWA (Burrows-Wheeler Aligner) 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check your BWA version:

.. code-block:: console

	$ bwa

If BWA is not installed or the version < 0.7.17:


.. code-block:: console

	$ sudo apt update
	sudo apt -y install bwa

Check the version again. If problems persist, refer to the `bwa site <https://bio-bwa.sourceforge.net/>`_.

SAMtools
^^^^^^^^

Check your SAMtools version:

.. code-block:: console

	$ samtools --version

If SAMtools is not installed or is outdated (< 1.15), follow instructions on the `samtools site <http://www.htslib.org/>`_.


RepeatMasker
^^^^^^^^^^^^

To install RepeatMasker_, follow installation instructions on `RepeatMasker site <http://www.repeatmasker.org/RepeatMasker/>`_.


Snakemake
^^^^^^^^^

Check your Snakemake version:

.. code-block:: console

	$ snakemake --version

If SnakeMake is not installed or is older than version < 7.7.0, install it following the instructions on `SnakeMake site <https://snakemake.readthedocs.io/en/stable/getting_started/installation.html>`_.
