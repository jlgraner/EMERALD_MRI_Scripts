

import os, shutil
import subprocess
import pandas


this_env = os.environ

sub_list = [
            'EM0001'
            ]

tract_list = [
              'L_SLFII',
              'R_SLFII',
              'L_Unc',
              'R_Unc'
              ]

bad_runs = []
good_runs = []

base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'DTI_FA_02082019')
#If the output directory does not exist, create it
if not os.path.exists(base_output_dir):
    print('Output directory not found; creating it: {}'.format(base_output_dir))
    os.mkdir(base_output_dir)

output_file = os.path.join(base_output_dir, 'DTI_tract_FAs_02082019.csv')

##Calculate average FA for each subject for each tract

#Save these into dictionaries
#Concatenate the dictionaries into a pandas data frame
#Save the pandas data frame as a csv