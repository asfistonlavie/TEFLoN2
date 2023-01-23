import argparse, sys, os


def mkdir_if_not_exist(*dirs):
	for dir in dirs:
		if not os.path.exists(dir):
			os.makedirs(dir,exist_ok=True)
			print("creating directory: %s" %(dir))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-wd',dest='wd',help='full path to working directory that you want created',default=-1)
	args = parser.parse_args()

	# identify current working directory
	if args.wd == -1:
		sys.exit("Error : Please use : $ python create_our_personal_input.py -wd <path_for_your_directory_input>")
	else:
		cwd=os.path.abspath(args.wd)
		lwd=os.path.join(cwd,"library")
		rwd=os.path.join(cwd,"reference")
		swd=os.path.join(cwd,"samples")
		sbwd=os.path.join(swd,"bam")
		sr1wd=os.path.join(swd,"reads")
		sr1wd=os.path.join(swd,"reads1")
		sr2wd=os.path.join(swd,"reads2")



	mkdir_if_not_exist(cwd,lwd,rwd,swd,sbwd,sr1wd,sr2wd)

	print("YOUR INPUT DATA FOLDER IS READY!")


if __name__ == "__main__":
	main()