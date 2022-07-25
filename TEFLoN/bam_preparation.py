import argparse, sys, os
import multiprocessing as mp
import subprocess as sp
import shlex
import glob
import shutil
from os import listdir
from os.path import isfile



def check_dependency(exeSAM):
	try:
		cmd = "%s" %(exeSAM)
		sp.Popen(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.PIPE)
	except OSError:
		print("Cannot find %s" %(exeSAM))
		sys.exit(1)

def assign_task(samples, task_q, nProcs):
	c,i,nth_job=0,0,1
	while (i+1)*nProcs <= len(samples):
		i+=1
	nP1=nProcs-(len(samples)%nProcs)
	for j in range(nP1):
		task_q.put((samples[c:c+i], nth_job))
		nth_job += 1
		c=c+i
	for j in range(nProcs-nP1):
		task_q.put((samples[c:c+i+1], nth_job))
		nth_job += 1
		c=c+i+1

def create_proc1(nProcs, task_q, params):
	for _ in range(nProcs):
		p = mp.Process(target=worker1, args=(task_q, params))
		p.daemon = True
		p.start()


def worker1(task_q, params):
	while True:
		try:
			samples, nth_job = task_q.get()
			#unpack parameters
			cwd, suppFile, exeSAM, exeBED = params
			for sample in samples:
				bamtofastq(cwd, sample, exeSAM, exeBED, suppFile)
		finally:
			task_q.task_done()


def bamtofastq(cwd, sample, exeSAM, exeBED, suppFile):
	try:
		#variable declaration
		name = sample[:-4]
		bam=os.path.join(cwd,sample)
		bam_sorted=os.path.join(cwd,name + '_sorted.bam')

		#bam sorting
		print("Sort:",name)
		cmd="%s sort -n %s -o %s" %(exeSAM, bam, bam_sorted)
		print(cmd)
		p = sp.Popen(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.PIPE)
		perr = p.communicate()[1] # communicate returns a tuple (stdout, stderr)
		if p.returncode != 0:
			print("error sorting file")
			sys.exit(1)

		fastq1=os.path.join("../data_input/samples/read1/",name + "_1.fastq")
		fastq2=os.path.join("../data_input/samples/read2/",name + "_2.fastq")
		print("Convert sorted bam to fastq:",bam_sorted)
		cmd="%s bamtofastq -i %s -fq %s -fq2 %s" %(exeBED, bam_sorted, fastq1, fastq2)
		p = sp.Popen(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.PIPE)
		perr = p.communicate()[1] # communicate returns a tuple (stdout, stderr)
		if p.returncode != 0:
			print("error bedtools bamtofastq")
			sys.exit(1)

	except OSError:
		print("Cannot convert file bam to fastq")
		sys.exit(1)
	print("Convert finaly.")


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('-wd',dest='wd',help='full path to working directory',default=-1)
	parser.add_argument('-es',dest='exeSAM',help='full path to samtools executable', default="samtools")
	parser.add_argument('-ebed',dest='exeBED',help='full path to bedtools executable', default="bedtools")
	parser.add_argument('-sf',dest='suppFile',help='Keep intermediate files',default=-1)
	parser.add_argument('-t',dest='nProc',help='number of processors', type=int, default=1)
	args = parser.parse_args()

	#import options
	exeSAM=args.exeSAM
	exeBED=args.exeBED
	nProc=args.nProc
	suppFile=args.suppFile

	#check dependencies for funtion
	check_dependency(exeSAM)
	check_dependency(exeBED)



	# identify current working directory
	if args.wd == -1:
		cwd=os.path.abspath("../data_input/samples/bam")
	else:
		cwd=os.path.abspath(args.wd)

	samples = [f for f in listdir(cwd) if (isfile(os.path.join(cwd, f)) and f.split(".")[-1]=="bam")]
	
	# run multiprocess 1
	task_q = mp.JoinableQueue()
	params=[cwd, suppFile, exeSAM, exeBED]
	create_proc1(nProc, task_q, params)
	assign_task(samples, task_q, nProc)
	try:
		task_q.join()
	except KeyboardInterrupt:
		print("KeyboardInterrupt")
		sys.exit(0)
	else:
		print("\nfinished convert bam to fastq")

if __name__=="__main__":
	main()



#samtools sort -n ../bam/AN0007-C.bam -o ../bam/AN0007-C_sorted.bam
#bedtools bamtofastq -i ../bam/AN0007-C_sorted.bam -fq ../fastq/AN0007-C_sorted_r1.fastq -fq2 ../fastq/AN0007-C_sorted_r2.fastq
