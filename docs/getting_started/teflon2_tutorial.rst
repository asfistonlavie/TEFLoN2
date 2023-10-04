================
TEFLoN2 Tutorial
================

After installing TEFLoN2 and its dependencies, you can test whether teflon2 works properly.


With RepeatMasker
-----------------
If you are using RepeatMasker (Preparation custom):

.. code-block:: console

	snakemake --configfile tests/tmp_config_prep_custom.yaml -s Snakefile -np -j  $MAX_JOBS


And then:

.. code-block:: console

    snakemake --configfile tests/tmp_config_prep_custom.yaml -s Snakefile -p -j  $MAX_JOBS


Warning: this may take some time

Without RepeatMasker
--------------------


If you are not using RepeatMasker (Preparation annotation):

.. code-block:: console

	snakemake --configfile tests/tmp_config_prep_annotation.yaml -s Snakefile -np -j  $MAX_JOBS



And then:

.. code-block:: console

	snakemake --configfile tests/tmp_config_prep_annotation.yaml -s Snakefile -p -j  $MAX_JOBS