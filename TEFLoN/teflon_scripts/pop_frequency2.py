import os,sys

def pop_frequency(popFILE,popDir,genoDir):
	populations={}
	print('lalalalalala')
	header = "chr\t5'breakpoint\t3'breackpoint\tlevel1\tlevel2\tstand\treference_TE_ID\t5'soft-clipped_reads\t3'soft-clipped_read\tteID\t"
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
					id,frequence,teID = fields[0], float(fields[4]), fields[5]
					if(id not in statsGroup):
						statsGroup[id] = {"presents":0,"absents":0,"polymorphs":0,"no data":0,"teID":teID}
					if frequence == -9 :
						statsGroup[id]["no data"] += 1
					elif frequence < 0.25 :
						statsGroup[id]["absents"] += 1
					elif frequence > 0.75 :
						statsGroup[id]["presents"] += 1
					else :
						statsGroup[id]["polymorphs"] += 1
		groupFILE = os.path.join(popDir,group + ".population.genotypes2.txt")
		with open(groupFILE,"w") as fOUT:
			for id in statsGroup:
				line = id + "\t" + str(statsGroup[id]["presents"]) + "\t" + str(statsGroup[id]["polymorphs"]) + "\t" + str(statsGroup[id]["absents"])
				if(id not in frequency):
					frequency[id] = {}
				total = statsGroup[id]["polymorphs"] + statsGroup[id]["presents"] + statsGroup[id]["absents"]
				frequency[id][group] = float((statsGroup[id]["presents"]) + float(statsGroup[id]["polymorphs"]*0.5))/total
				line = line + "\t" + str(frequency[id][group]) + "\t" + statsGroup[id]["teID"] + "\n"
				fOUT.write(line)

	allFrequencyPopFILE = os.path.join(popDir,"all_frequency.population.genotypes2.txt")
	with open(allFrequencyPopFILE, "w") as fOUT:
		fOUT.write(header[:-1] + "\n")
		for element in frequency:
			line = element +  "\t" + statsGroup[element]["teID"]
			for group in frequency[element] :
				line = line +"\t" + str(frequency[element][group])
			fOUT.write(line + "\n")


def all_frequency(samplesFILE,genoDir):
	with open(os.path.abspath(samplesFILE), 'r') as fIN:
		frequency = {}
		statsAll = {}
		for line in fIN:
			sample = line.split()[1]
			sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
			with open(sampleGeno,"r") as fIN:
				for line in fIN:
					fields = line[:-1].rsplit("\t",5)
					id,frequence,teID = fields[0], float(fields[4]), fields[5]
					if(id not in statsAll):
						statsAll[id] = {"presents":0,"absents":0,"polymorphs":0,"no data":0,"teID":teID}
					if frequence == -9 :
						statsAll[id]["no data"] += 1
					elif frequence < 0.25 :
						statsAll[id]["absents"] += 1
					elif frequence > 0.75 :
						statsAll[id]["presents"] += 1
					else :
						statsAll[id]["polymorphs"] += 1
		allFILE = os.path.join(genoDir,"all_samples.genotypes2.txt")
		with open(allFILE,"w") as fOUT:
			for id in statsAll:
				line = id + "\t" + str(statsAll[id]["presents"]) + "\t" + str(statsAll[id]["polymorphs"]) + "\t" + str(statsAll[id]["absents"])
				if(id not in frequency):
					frequency[id] = []
				total = statsAll[id]["polymorphs"] + statsAll[id]["presents"] + statsAll[id]["absents"]
				frequency[id] = float((statsAll[id]["presents"]) + float(statsAll[id]["polymorphs"]*0.5))/total
				line = line + "\t" + str(frequency[id]) + "\t" + statsAll[id]["teID"] + "\n"
				fOUT.write(line)
	#sample_names.txt