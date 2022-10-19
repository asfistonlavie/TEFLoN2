import sys, os
import subprocess as sp
import shlex

def wb_portal(ID, union, samples, tmpDir, tmpUnion, exePATH, qual, refine):
    if refine == "refine":
        # 1. rewrite bed
        tmpUnion[ID] = []
        if union[ID][7] == "+":
            tmpUnion[ID] = tmpUnion[ID] + [union[ID][0], int(union[ID][1])-1, int(union[ID][1])+1]
        if union[ID][8] == "+":
            tmpUnion[ID] = tmpUnion[ID] + [union[ID][0], int(union[ID][2])-1, int(union[ID][2])+1]
        if union[ID][7] == "-" and union[ID][8] == "-" and union[ID][1] != "-" and union[ID][2] != "-":
            tmpUnion[ID] = tmpUnion[ID] + [union[ID][0], min(int(union[ID][1]),int(union[ID][2]))-1, max(int(union[ID][1]),int(union[ID][2]))+1]

        # 2. samtools view > sample.sam
        for sample in samples:
            try:
                StringBed = '"'
                for i in range(int(len(tmpUnion[ID])/3)) :
                    cpt = i*3
                    StringBed = StringBed + str(tmpUnion[ID][0+cpt]) + '\t' + str(tmpUnion[ID][1+cpt]) + '\t' + str(tmpUnion[ID][2+cpt]) + '\n'
                StringBed = StringBed + '"'
                cmd = "%s view -L /dev/stdin %s <<< %s" %(exePATH, sample[0], StringBed)
                p = sp.Popen(cmd,  shell=True, executable='/bin/bash', stdout=sp.PIPE)
                OUT = p.communicate()[0] # communicate returns a tuple (stdout, stderr)
                return OUT
                if p.returncode != 0:
                    print("Error running samtools: p.returncode =",p.returncode)
                    #os.remove(outBED)
                    return ""
            except OSError:
                print("Cannot run samtools")
                #os.remove(outBED)
                return ""
    else:
        # 2. samtools view > sample.sam
        for sample in samples:
            try:
                StringBed = '"'
                for i in range(int(len(tmpUnion[ID])/3)) :
                    cpt = i*3
                    StringBed = StringBed + str(tmpUnion[ID][0+cpt]) + '\t' + str(tmpUnion[ID][1+cpt]) + '\t' + str(tmpUnion[ID][2+cpt]) + '\n'
                StringBed = StringBed + '"'
                # commend to execute
                cmd = "%s view -L /dev/stdin %s <<< %s" %(exePATH, sample[0], StringBed)
                #print "cmd:", cmd
                # run cmd in Popen with bash and redirect output in p
                p = sp.Popen(cmd,  shell=True, executable='/bin/bash', stdout=sp.PIPE)
                # extract output in p to OUT variable
                OUT = p.communicate()[0] # communicate returns a tuple (stdout, stderr)
                return OUT
                if p.returncode != 0:
                    print("Error running samtools: p.returncode =",p.returncode)
                    #os.remove(outBED)
                    return ""
            except OSError:
                print("Cannot run samtools")
                #os.remove(outBED)
                return ""
