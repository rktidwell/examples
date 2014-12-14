#!/usr/bin/env python
#----------------------------
# Copyright 2014 Ryan Tidwell
#----------------------------

import sys
import minedit

if len(sys.argv) != 3:
  print "Usage: wer_test <results file> <reference file>"

file = open(sys.argv[1])

results = []
reference = []

for line in file:
  reference.append(line.split())

file.close()

file = open(sys.argv[2])

for line in file:
  results.append(line.split())

total_edit_distance = 0

for i in range(0,len(results)):
   min_ed = float(minedit.minEditDist(results[i], reference[i]))
   wer = min_ed / float(len(results[i]))
   total_edit_distance += wer

print "Average WER:", float(total_edit_distance)/float(len(results))
