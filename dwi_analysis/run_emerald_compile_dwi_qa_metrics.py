
import os
import sys
import pandas


this_env = os.environ
qa_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'dwiqa')

#Make sure qa dir is there
if not os.path.exists(qa_dir):
    print('ERROR: QA directory cannot be found: {}'.format(qa_dir))
    raise RuntimeError('QA directory not found')

#Create output file
output_file = os.path.join(qa_dir, 'Group_dwi_QA_metrics.csv')

#Find existing subject directories
sub_dirs = []
sub_list = []
big_frame = pandas.DataFrame(columns=['sub','shell','outcount_mean','outcount_max','maxdisp','tsnr_mean'])
for element in os.listdir(qa_dir):
    if element[:4] == 'sub-':
        print('subject directory found: {}'.format(element))
        sub_dirs.append(element)
        sub = element[-6:]
        sub_list.append(sub)
        qa_file = os.path.join(qa_dir, element, 'sub-{}_ses-day3_dwi_QA_metrics.csv'.format(sub))

        qa_frame = pandas.read_csv(qa_file, sep=',', header=0, engine='python')
        #Append the new data to the group data frame
        big_frame = pandas.concat([big_frame, qa_frame], ignore_index=True)

#Print group data frame to a file
big_frame.to_csv(path_or_buf=output_file, sep=',', index=False, header=True)