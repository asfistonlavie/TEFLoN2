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
	parser.add_argument('-flt',dest='frequencyLoThresh',help='lower threshold used to define whether insertions are present, polymorphic, heterozygous, absent or no data. (default=0.05)',type=float,default=0.05)
	parser.add_argument('-flh',dest='frequencyHiThresh',help='hight threshold used to define whether insertions are present, polymorphic, heterozygous, absent or no data. (default=0.95)',type=float,default=0.95)
	parser.add_argument('-pop',dest="population",help='path population file',default=-1)
	parser.add_argument('-g',dest="group",help='',default=-1)
	parser.add_argument('-plt',dest='populationLoThresh',help='lower threshold used to define whether insertions are present, polymorphic or absent at population level. (default=0.05)',type=float,default=0.05)
	parser.add_argument('-plh',dest='populationHiThresh',help='hight threshold used to define whether insertions are present, polymorphic or absent at population level.(default=0.95)',type=float,default=0.95)
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
	frequencyHiThresh=args.frequencyHiThresh
	frequencyLoThresh=args.frequencyLoThresh
	populationLoThresh=args.populationLoThresh
	populationHiThresh=args.populationHiThresh

	# create the genotype directory
	countDir = os.path.join(cwd,"3-countPos")
	genoDir = os.path.join(cwd,"4-genotypes")
	samplesDir = os.path.join(genoDir,"samples")
	mkdir_if_not_exist(samplesDir)

	if args.ID != -1:
		if dataType not in "haploid, diploid, or pooled":
			return "Error datatype must be either haploid, diploid, or pooled"
			sys.exit()

		
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
		bamFILE=bam.replace(".bam",".subsmpl.bam")
		sample.append(bamFILE)
		sample.append(pre)
		statsFile = bamFILE.replace(".bam", ".stats.txt")
		with open(statsFile, 'r') as fIN:
			for l in fIN:
				if 'average length' in l:
					readLen=int(float(l.split()[-1]))
					sample.append(readLen)
				if 'insert size average' in l:
					insz=int(float(l.split()[-1]))
					sample.append(insz)
				if 'insert size standard deviation' in l:
					sd=int(float(l.split()[-1]))
					sample.append(sd)
		covFILE = bamFILE.replace(".bam", ".cov.txt")
		with open(covFILE, "r") as fIN:
			for l in fIN:
				if l.startswith("Av"):
					cov = float(l.split()[-1])
					sample.append(cov)
				if l.startswith("St"):
					cov_sd = float(l.split()[-1])
					sample.append(cov_sd)

		# average the stats for each sample
		averageLenghtIN = os.path.join(cwd,"1-mapping","averageLength.all.txt")
		with open(averageLenghtIN, "r") as fIN:
			for l in fIN:
				readLen = l.split()[-1]
		
		# define lower-bound coverage thresholds
		if loFilt == -1:
			l_thresh = 1
		else:
			l_thresh = loFilt
		print("Lower-bound coverage threshold filters corresponding to samples %s is %s" %(sample[1],l_thresh))
		print("NOTE: all sites with adjusted read counts > upper-bound coverage threshold will be marked -9")


		# define upper-bound coverage threshold
		if hiFilt == -1:
			h_thresh = int(sample[5]+ (2*sample[6]))
		else:
			h_thresh = hiFilt
		print("Upper-bound coverage threshold filters corresponding to samples %s is %s" %(sample[1],h_thresh))
		print("NOTE: all sites with adjusted read counts > upper-bound coverage threshold will be marked -9")



		pseudo2refFILE = os.path.join(prep_TF,prefix+".pseudo2ref.txt")
		print(pseudo2refFILE)
		with open(pseudo2refFILE,"r") as file :
			posMap = json.load(file)
			
		pt.pt_portal(countDir,samplesDir,sample, posMap, readLen, p2rC, l_thresh, h_thresh, dataType, frequencyLoThresh, frequencyHiThresh)

	# identify population file
	elif args.population != -1:
		populationsFILE = args.population
		nameGroup = args.group
		populationsDir = os.path.join(genoDir,"populations")
		mkdir_if_not_exist(populationsDir)
		if(nameGroup != -1) : 
			population = []
			with open(os.path.abspath(populationsFILE), 'r') as fIN:
				for line in fIN:
					if line.endswith("\n") :
						fields = line[:-1].split("\t")
					else : 
						fields = line.split("\t")
					group,sample = fields[1], fields[0]
					
					if group == nameGroup :
						population.append(sample)

			pf.pop_frequency(population,nameGroup,populationsDir,samplesDir,pt,populationLoThresh,populationHiThresh)
			pf2.pop_frequency(population,nameGroup,populationsDir,samplesDir,populationLoThresh,populationHiThresh)

		else :
			pf.pop_frequency_all(populationsFILE,populationsDir)
			pf2.pop_frequency_all(populationsFILE,populationsDir)

	#calcultate frequency for all samples
	else :

		pf.all_frequency(samplesFILE,samplesDir,pt,populationLoThresh,populationHiThresh)
		pf2.all_frequency(samplesFILE,samplesDir,populationLoThresh,populationHiThresh)


	print("TEFLON GENOTYPE FINISHED!")

if __name__ == "__main__":
	main()
