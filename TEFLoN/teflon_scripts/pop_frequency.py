import os,sys

def pop_frequency(popFILE,popDir,genoDir,pt):
	populations={}
	header = "chr\t5'breakpoint\t3'breackpoint\tlevel1\tlevel2\tstand\treference_TE_ID\t5'soft-clipped_reads\t3'soft-clipped_read\tvalues\t"
	with open(os.path.abspath(popFILE), 'r') as fIN:
		for line in fIN:
			fields = line.split()
			group,sample = fields[1], fields[0]
			if (group in populations):
				populations[group].append(sample)
			else:
				populations[group] = [sample]
				header = header + group + "_popFrequency\t" 

	frequency = {}
	statsGroup = {}
	for group in populations :
		for sample in populations[group]:
			sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
			with open(sampleGeno,"r") as fIN:
				for line in fIN:
					fields = line[:-1].rsplit("\t",5)
					id, presents, absents, ambiguous,values = fields[5], int(fields[1]), int(fields[2]), int(fields[3]), fields[0]
					if(id in statsGroup):
						statsGroup[id]["presents"] += presents
						statsGroup[id]["absents"] += absents
						statsGroup[id]["ambiguous"] += ambiguous
					else:
						statsGroup[id] = {"presents":presents,"absents":absents,"ambiguous":ambiguous,"values":values}
		groupFILE = os.path.join(popDir,group + ".population.genotypes.txt")
		with open(groupFILE,"w") as fOUT:
			for id in statsGroup:
				line = str(statsGroup[id]["values"]) + "\t" + str(statsGroup[id]["presents"]) + "\t" + str(statsGroup[id]["absents"]) + "\t" + str(statsGroup[id]["ambiguous"])
				if(id not in frequency):
					frequency[id] = {}
				frequency[id][group] = (pt.fq(line.split()))
				line = line + "\t" + str(frequency[id][group]) + "\t" + id + "\n"
				fOUT.write(line)

	allFrequencyPopFILE = os.path.join(popDir,"all_frequency.population.genotypes.txt")
	with open(allFrequencyPopFILE, "w") as fOUT:
		fOUT.write(header[:-1] + "\n")
		for element in frequency:
			line = statsGroup[element]["values"] +  "\t" + element
			for group in frequency[element] :
				line = line +"\t" + str(frequency[element][group])
			fOUT.write(line + "\n")


def all_frequency(samplesFILE,genoDir,pt):
	with open(os.path.abspath(samplesFILE), 'r') as fIN:
		frequency = {}
		statsAll = {}
		for line in fIN:
			sample = line.split()[1]
			sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
			with open(sampleGeno,"r") as fIN:
				for line in fIN:
					fields = line[:-1].rsplit("\t",5)
					id, presents, absents, ambiguous, values = fields[5] , int(fields[1]), int(fields[2]), int(fields[3]), fields[0]
					if(id in statsAll):
						statsAll[id]["presents"] += presents
						statsAll[id]["absents"] += absents
						statsAll[id]["ambiguous"] += ambiguous
					else:
						statsAll[id] = {"presents":presents,"absents":absents,"ambiguous":ambiguous, "values":values}
		allFILE = os.path.join(genoDir,"all_samples.genotypes.txt")
		with open(allFILE,"w") as fOUT:
			for id in statsAll:
				line = str(statsAll[id]["values"])  + "\t" + str(statsAll[id]["presents"]) + "\t" + str(statsAll[id]["absents"]) + "\t" + str(statsAll[id]["ambiguous"])
				if(id not in frequency):
					frequency[id] = []
				frequency[id] = pt.fq(line.split())
				line = line + "\t" + str(frequency[id]) + "\t" + id + "\n"
				fOUT.write(line)