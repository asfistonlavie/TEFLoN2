Bootstrap: docker
From: ubuntu:22.04

%help
    Container for TEFLoN2
    https://github.com/asfistonlavie/TEFLoN2
    Includes
        BWA  0.7.17
        RepeatMasker 4.1.3
        Python 3.8
        Samtools 1.16.1
        Snakemake  7.14.0

%labels
    VERSION "TEFLoN2 v1.0"
    Maintainer Corentin Marco
    Maintainer Fiston-Lavier Anna-Sophie
    October, 2023

%post
    export DEBIAN_FRONTEND=noninteractive
    export LC_ALL=C

    apt-get update
    apt-get install -y \
        tzdata \
        autoconf \
        automake \
        bwa \
        cmake \
        gcc \
        build-essential \
        tar \
        unzip \
        wget \
        zlib1g-dev \
        sudo \
        locales \
        python3-pip \
        ncbi-blast+ \
        bedtools \
        minimap2 \
        perl \
        pandoc-citeproc \
        python3-h5py \
        libfontconfig1-dev \
        libxml2-dev \
        libcurl4-openssl-dev \
        libssl-dev \
        libbz2-dev \
        liblzma-dev \
        curl \
        gawk \
        python3 \
        libncurses5-dev \
        pigz \
        perl \
        tcl \
        gzip 

    # Mettre à jour pip
    pip3 install --upgrade pip

    # Installer Snakemake et pulp
    pip3 install \
        snakemake \
        pulp==2.3.1 \
        six

    # Télécharger et installer fastp
    wget http://opengene.org/fastp/fastp -O /usr/local/bin/fastp
    chmod +x /usr/local/bin/fastp


    # Téléchargez et compilez Samtools 1.16.1
    wget https://github.com/samtools/samtools/releases/download/1.16.1/samtools-1.16.1.tar.bz2
    tar -vxjf samtools-1.16.1.tar.bz2
    cd samtools-1.16.1
    ./configure --prefix=/usr/local
    make
    make install
    cd ..

    #RepeatMasker 4.1.6
    #Dependances

    ## Download RMBlast
    cd /usr/bin
    wget https://www.repeatmasker.org/rmblast/rmblast-2.14.1+-x64-linux.tar.gz
    tar zxvf rmblast-2.14.1+-x64-linux.tar.gz

    ## Download TRF
	cd /usr/bin/
    git clone https://github.com/Benson-Genomics-Lab/TRF.git
    cd TRF
    mkdir build
    cd build
    ../configure
    make
    chmod +x /usr/bin/TRF


    ##Download and install RepeatMasker
    cd /usr/local/bin
    wget https://www.repeatmasker.org/RepeatMasker/RepeatMasker-4.1.6.tar.gz
    tar -zxvf RepeatMasker-4.1.6.tar.gz
    rm RepeatMasker-4.1.6.tar.gz

    wget https://www.dfam.org/releases/Dfam_3.8/families/FamDB/dfam38_full.0.h5.gz
    gunzip dfam38_full.0.h5.gz
    mv dfam38_full.0.h5.gz /usr/local/RepeatMasker/Libraries/famdb

    cp RepBaseRepeatMaskerEdition-20181026.tar.gz /usr/local/RepeatMasker/
    cd /usr/local/RepeatMasker
    gunzip RepBaseRepeatMaskerEdition-20181026.tar.gz
    tar xvf RepBaseRepeatMaskerEdition-20181026.tar
    rm RepBaseRepeatMaskerEdition-20181026.tar


    cd /usr/local/RepeatMasker
    perl ./configure

%environment
    export LC_ALL=C
