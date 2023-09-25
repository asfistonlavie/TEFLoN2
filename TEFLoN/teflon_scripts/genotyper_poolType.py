import os, sys
def avgReads(line,readLen):
	F,R="",""
	if line[1].isdigit():
		F=int(line[1])
	if line[2].isdigit():
		R=int(line[2])
	totalReads = int(line[9]) + int(line[10]) + int(line[11])
	if F != "" and R != "" and max([F,R])-min([F,R]) != 0:
		if line[7] == "-" and line[8] == "-":
			return int(totalReads/float(int((max([F,R])-min([F,R]))/float(readLen))+1))+1
		else:
			return int(totalReads/2.0)+1
	else:
		return totalReads

def fq(line):
	if int(line[9]) + int(line[10]) == 0:
		return -9
	else:
		return round(int(line[9])/float(int(line[9]) + int(line[10])), 3)


def pt_portal(countDir, genoDir, sample, posMap, readLen, p2rC, l_thresh, h_thresh, dataType, frequencyLoThresh, frequencyHiThresh):
	cts=[]
	inFILE=os.path.join(countDir,sample[1]+".counts.txt")
	with open(inFILE, "r") as fIN:
		for line in fIN:
			cts.append(line.split())
	outCall=[]
	for i in range(len(cts)):
		avgr = avgReads(cts[i],readLen)
		if avgr > h_thresh or avgr < l_thresh:
			outCall.append(-9)
		else:
			outCall.append(fq(cts[i]))
	outFILE1=os.path.join(genoDir,"pseudoSpace",sample[1]+".pseudoSpace.genotypes.txt")
	with open(outFILE1, "w") as fOUT:
		for i in range(len(cts)):
			fOUT.write("\t".join([str(x) for x in cts[i]])+"\t%s\n" %(str(outCall[i])))
	outFILE2=os.path.join(genoDir,sample[1]+".genotypes.txt")
	p2rC.pseudo2refConvert_portal(outFILE1,posMap,outFILE2,dataType,frequencyLoThresh,frequencyHiThresh)