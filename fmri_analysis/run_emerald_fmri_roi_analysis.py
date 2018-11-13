
import os, subprocess
import logging

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/{sub}/Func/ses-{ses}/Second_level.feat')
output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_Analysis_Output')

#for each subject:
#	1) Locate the dist>flow map
#	2) Locate the reap>flow map
#	3) Locate mask images
#	4) Extract average activations:
#		a) dist>flow for dACC, dlPFC, inf. par.
#		b) reap>flow for vmPFC, vlPFC, amygdala
#	5) Save the average activations into an output file

ses = 'day3'

# subs_to_run = [
#               'sub-EM0001',
#               'sub-EM0033',
#               'sub-EM0036',
#               'sub-EM0038',
#               'sub-EM0066',
#               'sub-EM0071',
#               'sub-EM0088',
#               'sub-EM0126',
#               'sub-EM0153',
#               'sub-EM0155',
#               'sub-EM0162',
#               'sub-EM0164',
#               'sub-EM0174',
#               'sub-EM0179',
#               'sub-EM0184',
#               'sub-EM0187',
#               'sub-EM0192',
#               'sub-EM0202',
#               'sub-EM0206',
#               'sub-EM0217',
#               'sub-EM0219',
#               'sub-EM0220',
#               'sub-EM0223',
#               'sub-EM0240'
#                ]

subs_to_run = ['sub-EM0001']

for sub in subs_to_run:
	#Make sure the input directory is there
	if not os.path.exists(input_dir.format(sub=sub, ses=ses))
		logging.error('Input directory cannot be found for subject {}!'.format(sub))
		raise RuntimeError