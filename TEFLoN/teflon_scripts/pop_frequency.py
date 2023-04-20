import os,sys

def pop_frequency_all(popFILE,popDir):
	populations={}
	header = "chr\t5'breakpoint\t3'breackpoint\tlevel1\tlevel2\tstand\treference_TE_ID\t5'soft-clipped_reads\t3'soft-clipped_read\tteID\t"
	group = []
	with open(popFILE,"r") as fIN:
		for line in fIN:
			if line.endswith("\n") :
				fields = line[:-1].split("\t")
			else : 
				fields = line.split("\t")
			group.append(fields[1])
		group = set(group)

	frequency = {}
	for element in group :
		header = header + element + "_popFrequency\t"
		groupFILE = os.path.join(popDir,element + ".population.genotypes.txt")
		with open(groupFILE, 'r') as fIN:
			for line in fIN:
				fields = line[:-1].rsplit("\t",7)
				values, id, freq  = fields[0], fields[7],fields[5]
				if(id not in frequency):
					frequency[id] = {"values":values}
				frequency[id][element] = freq
		
	
	allFrequencyPopFILE = os.path.join(popDir,"all_frequency.population.genotypes.txt")
	with open(allFrequencyPopFILE, "w") as fOUT:
		fOUT.write(header[:-1] + "\n")
		for element in frequency:
			line = frequency[element]["values"] +  "\t" + element
			for group in frequency[element] :
				if group != "values" :
					line = line +"\t" + str(frequency[element][group])
			fOUT.write(line + "\n")





def pop_frequency(population,group,popDir,genoDir,pt,populationLoThresh,populationHiThresh):
	frequency = {}
	statsGroup = {}
	for sample in population:
		sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
		with open(sampleGeno,"r") as fIN:
			for line in fIN:
				fields = line[:-1].rsplit("\t",6)
				id, presents, absents, ambiguous,values, type = fields[6], int(fields[1]), int(fields[2]), int(fields[3]), fields[0], fields[5]
				if (type != "no_data" ):
					if(id in statsGroup):
						statsGroup[id]["presents"] += presents
						statsGroup[id]["absents"] += absents
						statsGroup[id]["ambiguous"] += ambiguous
					else:
						statsGroup[id] = {"presents":presents,"absents":absents,"ambiguous":ambiguous,"no_data":0,"values":values}
				else :
					if(id in statsGroup):
						statsGroup[id]["no_data"] += 1
					else:
						statsGroup[id] = {"presents":0,"absents":0,"ambiguous":0,"no_data":1,"values":values}


	groupFILE = os.path.join(popDir,group + ".population.genotypes.txt")
	with open(groupFILE,"w") as fOUT:
		for id in statsGroup:
			line = str(statsGroup[id]["values"]) + "\t" + str(statsGroup[id]["presents"]) + "\t" + str(statsGroup[id]["absents"]) + "\t" + str(statsGroup[id]["ambiguous"]) + "\t" + str(statsGroup[id]["no_data"])
			if(id not in frequency):
				frequency[id] = {}
			frequency[id][group] = (pt.fq(line.split()[:-1]))
			interpretation = ""
			if float(frequency[id][group]) == -9 :
				interpretation = "no_data"
			elif float(frequency[id][group]) < float(populationLoThresh) :
				interpretation = "absent"
			elif float(frequency[id][group]) > float(populationHiThresh) :
				interpretation = "present"
			else:
				interpretation = "polymorphic"
			line = line + "\t" + str(frequency[id][group]) + "\t" + interpretation + "\t" + id + "\n"
			fOUT.write(line)


def all_frequency(samplesFILE,genoDir,pt,populationLoThresh,populationHiThresh):
	with open(os.path.abspath(samplesFILE), 'r') as fIN:
		frequency = {}
		statsAll = {}
		for line in fIN:
			sample = line.split()[1]
			sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
			with open(sampleGeno,"r") as fIN:
				for line in fIN:
					fields = line[:-1].rsplit("\t",6)
					id, presents, absents, ambiguous, values, type = fields[6] , int(fields[1]), int(fields[2]), int(fields[3]), fields[0], fields[5]
					if (type != "no_data" ):
						if(id in statsAll):
							statsAll[id]["presents"] += presents
							statsAll[id]["absents"] += absents
							statsAll[id]["ambiguous"] += ambiguous
						else:
							statsAll[id] = {"presents":presents,"absents":absents,"ambiguous":ambiguous,"no_data":0,"values":values}
					else :
						if(id in statsAll):
							statsAll[id]["no_data"] += 1
						else:
							statsAll[id] = {"presents":0,"absents":0,"ambiguous":0,"no_data":1,"values":values}
		allFILE = os.path.join(genoDir,"all_samples.genotypes.txt")
		with open(allFILE,"w") as fOUT:
			for id in statsAll:
				line = str(statsAll[id]["values"])  + "\t" + str(statsAll[id]["presents"]) + "\t" + str(statsAll[id]["absents"]) + "\t" + str(statsAll[id]["ambiguous"])+ "\t" + str(statsAll[id]["no_data"])
				if(id not in frequency):
					frequency[id] = []
				frequency[id] = pt.fq(line.split()[:-1])
				interpretation = ""
				if float(frequency[id]) == -9 :
					interpretation = "no_data"
				elif float(frequency[id]) < float(populationLoThresh) :
					interpretation = "absent"
				elif float(frequency[id]) > float(populationHiThresh) :
					interpretation = "present"
				else:
					interpretation = "polymorphic"
				line = line + "\t" + str(frequency[id]) + "\t" + interpretation + "\t" + id + "\n"
				fOUT.write(line)
