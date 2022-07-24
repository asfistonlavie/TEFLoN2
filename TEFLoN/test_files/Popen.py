import sys, os
import subprocess as sp
import shlex



# commend to execute
cmd = 'samtools view -L /dev/stdin  /home/ozone/Stage_M2/TEFLoN-Python3/test_files/sample_output/sample1.tmp/megaBed.bam <<< "2R        38144   38146"'
# run cmd in Popen with bash and redirect output in var
var = sp.Popen(cmd, shell=True, executable='/bin/bash', stdout=sp.PIPE)
# extract output in var to out variable
out = var.communicate()[0]
# cast output in ascii string
print(out.decode())


# p=sp.Popen(["samtools", "view", "-L", "/dev/stdin",  "/home/ozone/Stage_M2/TEFLoN-Python3/test_files/sample_output/sample1.tmp/megaBed.bam" , "<<<", '"2R        38144   38146"'], stdout=sp.PIPE)
# stdout = p.communicate()

# run = sp.run(["samtools", "view", "-L", "/dev/stdin",  "/home/ozone/Stage_M2/TEFLoN-Python3/test_files/sample_output/sample1.tmp/megaBed.bam" , "<<<", '"2R        38144   38146"'])
# print(run)

# list_files = sp.run(["samtools", "view", "-L", "/dev/stdin" ,"/home/ozone/Stage_M2/TEFLoN-Python3/test_files/sample_output/sample1.tmp/megaBed.bam", "<<<", '"2R        38144   38146"' ])
# print("The exit code was: %d" % list_files.returncode)