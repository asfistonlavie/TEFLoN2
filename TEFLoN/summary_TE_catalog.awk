BEGIN {
	OFS="\t";
	output="TE_catalog.summary";
	annotations=0;
	de_novo=0;

	chr[""]=0;
	chr_annotations[$1]=0;
	chr_de_novo[$1]=0;

	hierarchy_level1[""]=0;
	hierarchy_level1_annotation[""]=0;
	hierarchy_level1_de_novo[""]=0;

	hierarchy_level2[""]=0;
	hierarchy_level2_annotation[""]=0;
	hierarchy_level2_de_novo[""]=0;

}
{
	chr[$1]++;
	hierarchy_level1[$4]++;
	hierarchy_level2[$5]++;

	if($7 != "-"){
		annotations++;
		chr_annotations[$1]++;

		hierarchy_level1_annotation[$4]++;
		hierarchy_level2_annotation[$5]++;
	}
	else{
		de_novo++;
		chr_de_novo[$1]++;

		hierarchy_level1_de_novo[$4]++;
		hierarchy_level2_de_novo[$5]++;
	}
}

END {
	print "" > output
	print "#Summary informations on",ARGV[1] >> output
	print "#Generale:" >> output
	print "Number of insersions:",NR >> output
	print "References:",annotations >> output
	print "De novo:",de_novo >> output
	print "\n" >> output

	print "#By chromosme:" >> output
	print "Chromosome\tall\tannotation\tde novo" >> output
	for (i in chr) {
		if (chr_annotations[i] == 0){
			chr_annotations[i]=0
		}
		if (chr_de_novo[i] == 0){
			chr_de_novo[i]=0
		}
		if (i != "") {
			print i,chr[i],chr_annotations[i],chr_de_novo[i] >> output
		}
	}
	print "\n" >> output

	print "#By hierarchy level 1:" >> output
	print "Level_1\tall\tannotation\tde novo" >> output
	for (i in hierarchy_level1) {
		if (hierarchy_level1_annotation[i] == 0){
			hierarchy_level1_annotation[i]=0
		}
		if (hierarchy_level1_de_novo[i] == 0){
			hierarchy_level1_de_novo[i]=0
		}
		if (i != "") {
			print i,hierarchy_level1[i],hierarchy_level1_annotation[i],hierarchy_level1_de_novo[i] >> output
		}
	}
	print "\n" >> output

	print "#By hierarchy level 2:" >> output
	print "Level_2\tall\tannotation\tde novo" >> output
	for (i in hierarchy_level2) {
		if (hierarchy_level2_annotation[i] == 0){
			hierarchy_level2_annotation[i]=0
		}
		if (hierarchy_level2_de_novo[i] == 0){
			hierarchy_level2_de_novo[i]=0
		}
		if (i != "") {
			print i,hierarchy_level2[i],hierarchy_level2_annotation[i],hierarchy_level2_de_novo[i] >> output
		}
	}

}
