#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 

import argparse, sys, os
import json



pseudo2refFILE = "/home/ozone/Stage_M2/TEFLoN-Python3/test_files/sample_output/reference/TEST.prep_TF/TEST.pseudo2ref.txt"
with open(pseudo2refFILE,"r") as file :
    posMap = json.load(file)



