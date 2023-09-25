import argparse, sys, os, gzip
import gc
import json

from teflon_scripts import pseudo2refConvert as p2rC

def mkdir_if_not_exist(*dirs):
	for dir in dirs:
		if not os.path.exists(dir):
			os.makedirs(dir,exist_ok=True)
			print("creating directory: %s" %(dir))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-wd',dest='wd',help='full path to working directory', default=-1)
	parser.add_argument('-d',dest='DIR',help='full path to prep_TF directory')
	args = parser.parse_args()

	# identify current working directory
	if args.wd == -1:
		cwd=os.getcwd()
	else:
		cwd=os.path.abspath(args.wd)


	## create the preliminary_results directory
	preliminaryResultsDir = os.path.join(cwd,"2-preliminaryResults")
	mkdir_if_not_exist(preliminaryResultsDir)


	prep_TF=os.path.abspath(args.DIR)
	prefix=os.path.abspath(args.DIR).split("/")[-1].replace(".prep_TF","")
	countDir = os.path.join(cwd,"3-countPos")
	catalog = os.path.join(countDir,"union_sorted.collapsed.txt")


	#load pseudo2ref.txt
	pseudo2refFILE = os.path.join(prep_TF,prefix+".pseudo2ref.txt")

	print(pseudo2refFILE)
	with open(pseudo2refFILE,"r") as file :
		posMap = json.load(file)

	convertedOutFile = os.path.join(preliminaryResultsDir,"converted_TE_catalog.union_sorted.collapsed.txt")
	p2rC.pseudo2refConvert_portal(catalog,posMap,convertedOutFile)
	
	print("POSITION CONVERSION FINISHED!")
	
if __name__ == "__main__":
	main()
