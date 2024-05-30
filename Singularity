Bootstrap: docker
From: ubuntu:22.04

%post
    export DEBIAN_FRONTEND=noninteractive
    export LC_ALL=C

    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tzdata \
        autoconf \
        automake \
        bwa \
        cmake \
        gcc \
        build-essential \
        software-properties-common \
        tar \
        unzip \
        wget \
        zlib1g-dev \
        sudo \
        git-core \
        locales \
        python3-pip \
        ncbi-blast+ \
        bedtools \
        minimap2 \
        snakemake \
        assemblytics \
        r-base \
        perl \
        pandoc-citeproc \
        python3-h5py \
        libfontconfig1-dev \
        libxml2-dev \
        libcurl4-openssl-dev \
        libssl-dev \
        curl \
        gawk \
        fastp

    dpkg-divert --local --rename --add /sbin/initctl
    ln -s /bin/true /sbin/initctl

    # Téléchargez et compilez Samtools 1.16.1
    wget https://github.com/samtools/samtools/releases/download/1.16.1/samtools-1.16.1.tar.bz2
    tar -vxjf samtools-1.16.1.tar.bz2
    cd samtools-1.16.1
    ./configure --prefix=/usr/local
    make
    make install
    cd ..

    # Téléchargez RMBlast et TRF, puis installez RepeatMasker 4.1.3
    wget https://www.repeatmasker.org/rmblast/rmblast-2.14.1+-x64-linux.tar.gz
    tar zxvf rmblast-2.14.1+-x64-linux.tar.gz
    wget https://github.com/Benson-Genomics-Lab/TRF/releases/download/v4.09.1/trf409.linux64
    chmod +x trf409.linux64
    mv trf409.linux64 /usr/local/bin
    wget https://www.repeatmasker.org/RepeatMasker/RepeatMasker-4.1.3-p1.tar.gz
    tar -zxvf RepeatMasker-4.1.3-p1.tar.gz
    cd RepeatMasker
    perl ./configure --trf_prgm=/usr/local/bin/trf409.linux64 --rmblast_dir=/usr/local/rmblast

%environment
    export LC_ALL=C

%environment
    export LC_ALL=C
