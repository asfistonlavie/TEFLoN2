import sys, os
import subprocess as sp
import shlex

def wb_portal(ID, union, samples, tmpDir, tmpUnion, exePATH, qual, refine):
    if refine == "refine":
        # 1. rewrite bed
        tmpUnion[ID] = []
        if union[ID][7] == "+":
            # bed.append([union[ID][0], int(union[ID][1])-1, int(union[ID][1])+1])
            tmpUnion[ID] = tmpUnion[ID] + [union[ID][0], int(union[ID][1])-1, int(union[ID][1])+1]
        if union[ID][8] == "+":
            # bed.append([union[ID][0], int(union[ID][2])-1, int(union[ID][2])+1])
            tmpUnion[ID] = tmpUnion[ID] + [union[ID][0], int(union[ID][2])-1, int(union[ID][2])+1]
        if union[ID][7] == "-" and union[ID][8] == "-" and union[ID][1] != "-" and union[ID][2] != "-":
            # bed.append([union[ID][0], min(int(union[ID][1]),int(union[ID][2]))-1, max(int(union[ID][1]),int(union[ID][2]))+1])
            tmpUnion[ID] = tmpUnion[ID] + [union[ID][0], min(int(union[ID][1]),int(union[ID][2]))-1, max(int(union[ID][1]),int(union[ID][2]))+1]
        # outBED = os.path.join(tmpDir, "union_%s.bed" %(str(ID)))
        # with open(outBED, 'w') as fOUT:
        #     for line in bed:
        #         try:
        #             fOUT.write("\t".join([str(x) for x in line]) + "\n")
        #         except IOError:
        #             continue
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
                # #samFILE = outBED.replace(".bed", ".%s.sam" %(sample[1]))
                # cmd = "%s view -L %s %s" %(exePATH, outBED, sample[0])
                # #print "cmd:", cmd
                # p = sp.Popen(shlex.split(cmd), stdout=sp.PIPE)
                # OUT = p.communicate()[0] # communicate returns a tuple (stdout, stderr)
                # #print perr
                # #os.remove(outBED)
                # with open(samFILE, "w") as fOUT:
                #     for z in OUT:
                #         fOUT.write(chr(z))
                # return OUT
                if p.returncode != 0:
                    print("Error running samtools: p.returncode =",p.returncode)
                    #os.remove(outBED)
                    return ""
            except OSError:
                print("Cannot run samtools")
                #os.remove(outBED)
                return ""
    else:
        # 1. write bed
        #outBED = os.path.join(tmpDir, "union_%s.bed" %(str(ID)))

        # 2. samtools view > sample.sam
        for sample in samples:
            try:
                # samFILE = outBED.replace(".bed", ".%s.sam" %(sample[1]))
                # cmd = "%s view -L %s %s" %(exePATH, outBED, sample[0])
                # samtools view -L /dev/stdin  /home/ozone/Stage_M2/TEFLoN-Python3/test_files/sample_output/sample1.tmp/megaBed.bam <<< "2R        38144   38146"
                #String with information in file bed for 3 informations
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
                #print perr
                #os.remove(outBED)
                # with open(samFILE, "w") as fOUT:
                #     for z in OUT:
                #         fOUT.write(chr(z))
                return OUT
                if p.returncode != 0:
                    print("Error running samtools: p.returncode =",p.returncode)
                    #os.remove(outBED)
                    return ""
            except OSError:
                print("Cannot run samtools")
                #os.remove(outBED)
                return ""
