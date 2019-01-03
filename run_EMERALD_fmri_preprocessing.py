

import os, sys
import logging
import json

subs_to_run = ['EM0240']


this_env = os.environ
here = os.path.dirname(os.path.realpath(__file__))
fmri_lib_dir = os.path.join(here, 'fmri_analysis')
sys.path.append(fmri_lib_dir)

#Import local libraries
import emerald_physio_lib

em2biac_file = os.path.join(this_env['EMDIR'], 'Scripts', 'MRI_Analysis', 'EM_to_BIAC.json')

#Read in the EM-BIAC dictionary
with open(em2biac_file) as fd:
    em2biac = json.loads(fd.read())

subs_that_failed = []
subs_that_worked = []

for emsub in subs_to_run:
    #Process physiology files
    ###Check to make sure the EM ID is in the EM_to_BIAC json
    biacsub = em2biac['em_to_biac'][emsub]
    physio_input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'Orig', 'Data', 'Func', biacsub, 'Scanner_physio')