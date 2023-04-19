import argparse, sys, os, gzip
import gc
import json

teflonBase = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.insert(1, teflonBase)

from teflon_scripts import mean_stats as ms
from teflon_scripts import genotyper_poolType as pt
from teflon_scripts import pseudo2refConvert as p2rC
from teflon_scripts import pop_frequency as pf
from teflon_scripts import pop_frequency2 as pf2

def mkdir_if_not_exist(*dirs):
	for dir in dirs:
		if not os.path.exists(dir):
			os.makedirs(dir,exist_ok=True)
			print("creating directory: %s" %(dir))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-wd',dest='wd',help='full path to working directory', default=-1)
	parser.add_argument('-d',dest='DIR',help='full path to prep_TF directory')
	parser.add_argument('-s',dest='samples',help='tab delimited text file with full paths to indexed bamFILEs and sorted te positions')
	parser.add_argument('-i',dest='ID',help='unique id of this sample',default=-1)
	parser.add_argument('-lt',dest='loThresh',help='sites genotyped as -9 if adjusted read counts less than than this threshold (default=1)', type=int, default=-1)
	parser.add_argument('-ht',dest='hiThresh',help='sites genotyped as -9 if adjusted read counts greater than this threshold (default=mean_coverage + 2*STDEV)', type=int, default=-1)
	parser.add_argument('-dt',dest='dataType',help='haploid, diploid, or pooled')
	parser.add_argument('-flt',dest='frequencyLoThresh',help='Lower threshold used to define whether insertions are present, polymorphic or absent. For haploid data,default = 0.5. For diloid or pooled data default=0.25)',type=float,default=-1)
	parser.add_argument('-flh',dest='frequencyHiThresh',help='Hight threshold used to define whether insertions are present, polymorphic or absent. For haploid data, there is no. For diloid or pooled data default=0.75)',type=float,default=0.75)
	parser.add_argument('-pop',dest="population",help='',default=-1)
	parser.add_argument('-plt',dest='populationLoThresh',help='Lower threshold used to define whether insertions are present, polymorphic or absent at population level. (default=0.25)',type=float,default=0.25)
	parser.add_argument('-plh',dest='populationHiThresh',help='Hight threshold used to define whether insertions are present, polymorphic or absent at population level.(default=0.75)',type=float,default=0.75)
	args = parser.parse_args()

	# identify current working directory
	if args.wd == -1:
		cwd=os.getcwd()
	else:
		cwd=os.path.abspath(args.wd)

	# import options
	loFilt=args.loThresh
	hiFilt=args.hiThresh
	prep_TF=os.path.abspath(args.DIR)
	prefix=os.path.abspath(args.DIR).split("/")[-1].replace(".prep_TF","")
	dataType=args.dataType
	samplesFILE=args.samples
	if dataType not in "haploid, diploid, or pooled":
		return "Error datatype must be either haploid, diploid, or pooled"
		sys.exit()

	

	frequencyLoThresh=args.frequencyLoThresh
	if frequencyLoThresh == -1:
		if dataType == "haploid":
			frequencyLoThresh = 0.5
		if dataType == "diploid" or dataType == "pooled" :
			frequencyLoThresh = 0.25

	frequencyHiThresh=args.frequencyHiThresh
	populationLoThresh=args.populationLoThresh
	populationHiThresh=args.populationHiThresh

	if args.ID != -1:
		bam,pre="",""
		with open(os.path.abspath(args.samples), "r") as fIN:
			for line in fIN:
				if line.split()[1] == args.ID:
					pre = line.split()[1]
					bam = line.split()[0]
		if pre=="" or bam=="":
			print("Warning: prefix in samples file different from path in options")
			sys.exit()
		
		# read samples and stats
		sample=[]
		bamFILE=bam.split()[0].replace(".bam",".subsmpl.bam")
		statsFile = bamFILE.replace(".bam", ".stats.txt")
		with open(statsFile, 'r') as fIN:
					for l in fIN:
						if 'average length' in l:
							readLen=int(float(l.split()[-1]))
						if 'insert size average' in l:
							insz=int(float(l.split()[-1]))
						if 'insert size standard deviation' in l:
							sd=int(float(l.split()[-1]))
		covFILE = bamFILE.replace(".bam", ".cov.txt")
		with open(covFILE, "r") as fIN:
					for l in fIN:
						if l.startswith("Av"):
							cov = float(l.split()[-1])
						if l.startswith("St"):
							cov_sd = float(l.split()[-1])
		sample.append(bamFILE, pre, [readLen, insz, sd, cov, cov_sd])



		# average the stats for each sample
		stats=ms.mean_stats_portal(sample)

		# create the genotype directory
		countDir = os.path.join(cwd,"3-countPos")
		genoDir = os.path.join(cwd,"4-genotypes")
		samplesDir = os.path.join(genoDir,"samples")
		mkdir_if_not_exist(samplesDir)

		# define lower-bound coverage thresholds
		if loFilt == -1:
			l_thresh = 1
		else:
			l_thresh = loFilt
		print("Lower-bound coverage threshold filters corresponding to samples %s is %s" %(sample[1],l_thresh))
		print("NOTE: all sites with adjusted read counts > upper-bound coverage threshold will be marked -9")


		# define upper-bound coverage threshold
		if hiFilt == -1:
			h_thresh = int(sample[2][3]+ (2*sample[2][4]))
		else:
			h_thresh = hiFilt
		print("Upper-bound coverage threshold filters corresponding to samples %s is %s" %(sample[1],h_thresh))
		print("NOTE: all sites with adjusted read counts > upper-bound coverage threshold will be marked -9")



		pseudo2refFILE = os.path.join(prep_TF,prefix+".pseudo2ref.txt")
		print(pseudo2refFILE)
		with open(pseudo2refFILE,"r") as file :
			posMap = json.load(file)


		pt.pt_portal(countDir,samplesDir,sample, posMap, stats, p2rC, l_thresh, h_thresh, dataType, frequencyLoThresh, frequencyHiThresh)

	# identify population file

	elif args.population != -1:
		populationsFILE = args.population
		populationsDir = os.path.join(genoDir,"populations")
		mkdir_if_not_exist(populationsDir)
		pf.pop_frequency(populationsFILE,populationsDir,samplesDir,pt,populationLoThresh,populationHiThresh)
		pf2.pop_frequency(populationsFILE,populationsDir,samplesDir,populationLoThresh,populationHiThresh)

	#calcultate frequency for all samples
	else :
		pf.all_frequency(samplesFILE,samplesDir,pt,populationLoThresh,populationHiThresh)
		pf2.all_frequency(samplesFILE,samplesDir,populationLoThresh,populationHiThresh)


	print("TEFLON GENOTYPE FINISHED!")

if __name__ == "__main__":
	main()
