import argparse, sys, os
import subprocess as sp
import shlex
import multiprocessing as mp

teflonBase = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(1, teflonBase)

from teflon_scripts import sort_positions as sortp
from teflon_scripts import collapse_union as cu
from teflon_scripts import mean_stats as ms
from teflon_scripts import subsample_alignments as sa


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-wd',dest='wd',help='full path to working directory',default=-1)
	parser.add_argument('-d',dest='DIR',help='full path to prep_TF directory')
	parser.add_argument('-s',dest='samples',help='tab delimited text file with full paths to indexed bamFILEs and sorted te positions')
	parser.add_argument('-es',dest='exeSAM',help='full path to samtools executable', default="samtools")
	parser.add_argument('-cov',dest='cov',help='subsample to coverage override', type=float, default=-1)
	parser.add_argument('-q',dest='qual',help='map quality threshold', type=int, default=20)
	parser.add_argument('-t',dest='nProc',help='number of processors', type=int, default=1)
	args = parser.parse_args()


	# identify current working directory
	if args.wd == -1:
		cwd=os.getcwd()
	else:
		cwd=os.path.abspath(args.wd)

	# import options
	exeSAM=args.exeSAM
	qual=args.qual
	nProc=args.nProc
	covOverride=args.cov

	# read the samples and stats
	samples=[]
	# each sample will be formatted [path to bamFILE, uniqueID, [stats]]
	with open(os.path.abspath(args.samples), 'r') as fIN:
		for line in fIN:
			statsOutFile = line.split()[0].replace(".bam", ".stats.txt")
			with open(statsOutFile, 'r') as fIN:
				for l in fIN:
					if "raw total sequences:" in l:
						total_n=int(l.split()[4])
					if 'average length' in l:
						readLen=int(float(l.split()[-1]))
					if 'insert size average' in l:
						insz=int(float(l.split()[-1]))
					if 'insert size standard deviation' in l:
						sd=int(float(l.split()[-1]))
			covFILE = line.split()[0].replace(".bam", ".cov.txt")
			with open(covFILE, "r") as fIN:
				for l in fIN:
					if l.startswith("Av"):
						cov = float(l.split()[-1])
					if l.startswith("St"):
						cov_sd = float(l.split()[-1])
			samples.append([line.split()[0], line.split()[1], [readLen, insz, sd, total_n,cov,cov_sd]])

	# generate subsampled alignments for use in teflon_count
	sa.subsample_alignments_portal(samples, exeSAM, nProc, qual, covOverride,os.path.abspath(args.DIR))

	subsamples = []
	# average the stats for each subsample
	with open(os.path.abspath(args.samples), 'r') as fIN:
		for line in fIN:
			subsampleFile = line.split()[0].replace(".bam", ".subsmpl.bam")
			statsOutFile = subsampleFile.replace(".bam", ".stats.txt")
			with open(statsOutFile, 'r') as fIN:
				for l in fIN:
					if "raw total sequences:" in l:
						total_n=int(l.split()[4])
					if 'average length' in l:
						readLen=int(float(l.split()[-1]))
					if 'insert size average' in l:
						insz=int(float(l.split()[-1]))
					if 'insert size standard deviation' in l:
						sd=int(float(l.split()[-1]))
			covFILE = subsampleFile.replace(".bam", ".cov.txt")
			with open(covFILE, "r") as fIN:
				for l in fIN:
					if l.startswith("Av"):
						cov = float(l.split()[-1])
					if l.startswith("St"):
						cov_sd = float(l.split()[-1])
			subsamples.append([subsampleFile, line.split()[1], [readLen, insz, sd, total_n,cov,cov_sd]])
	print(subsamples)
	averageLenghtOUT = os.path.join(cwd,"1-mapping","averageLength.all.txt")
	ms.mean_stats_portal(subsamples,averageLenghtOUT)
	
	print("\nSUBSAMPLE FINISHED!")


if __name__ == "__main__":
	main()