Bootstrap: docker
From: ubuntu:22.04

%help
	Container for TEFLoN2
	https://github.com/asfistonlavie/TEFLoN2
	Includes
		BWA  0.7.17
		RepeatMasker 4.1.3
		Ptyhon 3.8
		Samtools 1.16.1
		Snakemake  7.14.0
		
%labels
	VERSION "TEFLoN2 v1.0"
	Maintener Corentin Marco
	Maintener Fiston-Lavier Anna-Sophie
	October,2023


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

	# Téléchargez et compilez Samtools 1.16.1
	wget https://github.com/samtools/samtools/releases/download/1.16.1/samtools-1.16.1.tar.bz2
	tar -vxjf samtools-1.16.1.tar.bz2
	cd samtools-1.16.1
	make
	make install

	# Téléchargez RMBlast et TRF, puis installez RepeatMasker 4.1.3
	wget https://www.repeatmasker.org/rmblast/rmblast-2.14.1+-x64-linux.tar.gz
	tar zxvf rmblast-2.14.1+-x64-linux.tar.gz
	wget https://github.com/Benson-Genomics-Lab/TRF/releases/download/v4.09.1/trf409.linux64
	chmod +x trf409.linux64
	cd /usr/local/bin
	wget https://www.repeatmasker.org/RepeatMasker/RepeatMasker-4.1.3-p1.tar.gz
	tar -zxvf RepeatMasker-4.1.3-p1.tar.gz
	cd /usr/local/bin/RepeatMasker
	perl ./configure --trf_prgm=/usr/bin/trf409.linux64 --rmblast_dir=/usr/bin/rmblast-2.11.0/bin

%environment
	export LC_ALL=C
	ENV DEBIAN_FRONTEND=noninteractive


%runscript
	exec "$@"
