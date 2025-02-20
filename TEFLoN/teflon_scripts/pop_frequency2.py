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
		groupFILE = os.path.join(popDir,element + ".population.genotypes2.txt")
		with open(groupFILE, 'r') as fIN:
			for line in fIN:
				fields = line[:-1].rsplit("\t",7)
				values, id, freq  = fields[0], fields[7],fields[5]
				if(id not in frequency):
					frequency[id] = {"values":values}
				frequency[id][element] = freq
		
	
	allFrequencyPopFILE = os.path.join(popDir,"all_frequency.population.genotypes2.txt")
	with open(allFrequencyPopFILE, "w") as fOUT:
		fOUT.write(header[:-1] + "\n")
		for element in frequency:
			line = frequency[element]["values"] +  "\t" + element
			for group in frequency[element] :
				if group != "values" :
					line = line +"\t" + str(frequency[element][group])
			fOUT.write(line + "\n")



def pop_frequency(population,group,popDir,genoDir,populationLoThresh,populationHiThresh):
	frequency = {}
	statsGroup = {}
	for sample in population:
		sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
		with open(sampleGeno,"r") as fIN:
			for line in fIN:
				fields = line[:-1].rsplit("\t",6)
				id,frequence,values = fields[6], float(fields[4]), fields[0]
				if(id not in statsGroup):
					statsGroup[id] = {"presents":0,"absents":0,"polymorphs":0,"no data":0,"values":values}
				if frequence == -9 :
					statsGroup[id]["no data"] += 1
				elif frequence < float(populationLoThresh) :
					statsGroup[id]["absents"] += 1
				elif frequence > float(populationHiThresh) :
					statsGroup[id]["presents"] += 1
				else :
					statsGroup[id]["polymorphs"] += 1
	groupFILE = os.path.join(popDir,group + ".population.genotypes2.txt")
	with open(groupFILE,"w") as fOUT:
		for id in statsGroup:
			line = str(statsGroup[id]["values"]) + "\t" + str(statsGroup[id]["presents"]) + "\t" + str(statsGroup[id]["polymorphs"]) + "\t" + str(statsGroup[id]["absents"]) + "\t" + str(statsGroup[id]["no data"])
			if(id not in frequency):
				frequency[id] = {}
			total = statsGroup[id]["polymorphs"] + statsGroup[id]["presents"] + statsGroup[id]["absents"]
			if(total == 0):
				frequency[id][group] = -9
			else :
				frequency[id][group] = round(float((statsGroup[id]["presents"]) + float(statsGroup[id]["polymorphs"]*0.5))/total,3)
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



def all_frequency(samplesFILE,genoDir,populationLoThresh,populationHiThresh):
	with open(os.path.abspath(samplesFILE), 'r') as fIN:
		frequency = {}
		statsAll = {}
		for line in fIN:
			sample = line.split()[1]
			sampleGeno = os.path.join(genoDir,sample + ".genotypes.txt")
			with open(sampleGeno,"r") as fIN:
				for line in fIN:
					fields = line[:-1].rsplit("\t",6)
					id,frequence,values = fields[6], float(fields[4]), fields[0]
					if(id not in statsAll):
						statsAll[id] = {"presents":0,"absents":0,"polymorphs":0,"no data":0,"values":values}
					if frequence == -9 :
						statsAll[id]["no data"] += 1
					elif frequence < float(populationLoThresh) :
						statsAll[id]["absents"] += 1
					elif frequence > float(populationHiThresh) :
						statsAll[id]["presents"] += 1
					else :
						statsAll[id]["polymorphs"] += 1
		allFILE = os.path.join(genoDir,"all_samples.genotypes2.txt")
		with open(allFILE,"w") as fOUT:
			for id in statsAll:
				line = str(statsAll[id]["values"]) + "\t" + str(statsAll[id]["presents"]) + "\t" + str(statsAll[id]["polymorphs"]) + "\t" + str(statsAll[id]["absents"]) + "\t" + str(statsAll[id]["no data"])
				if(id not in frequency):
					frequency[id] = []
				total = statsAll[id]["polymorphs"] + statsAll[id]["presents"] + statsAll[id]["absents"]
				if(total == 0):
					frequency[id] = -9
				else:
					frequency[id] = round(float((statsAll[id]["presents"]) + float(statsAll[id]["polymorphs"]*0.5))/total,3)
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
