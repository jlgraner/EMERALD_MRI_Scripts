

import subprocess
import os

#This code just removes the first 4 TRs from participants' fmri data.

this_env = os.environ

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD/sub-{sub}/ses-{ses}/func')
base_output_dir = ''


subs_to_run = [
               'EM0291'
               ]

