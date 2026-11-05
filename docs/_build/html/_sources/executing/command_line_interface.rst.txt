======================
Command line interface
======================



After completing the configuration files and placing input data in the correct folders, you can executing simulation of TEFLoN2 :

.. code-block:: console

	$ snakemake --configfile config.yaml -s Snakefile -np -j $MAX_JOBS

If all went well, execute TEFLoN2 :

.. code-block:: console

	$ snakemake --configfile config.yaml -s Snakefile -p -j $MAX_JOBS


To make TEFLoN2 work, you may need to configure your cluster.

for more information on the launch, go to `SnakeMake documentation <https://snakemake.readthedocs.io/en/stable/>`_.
