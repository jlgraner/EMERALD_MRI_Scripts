
import os, subprocess
import logging

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/{sub}/Func/Second_level_allruns.gfeat')
output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_Analysis_Output')

output_file_template = 'Group_ROI_means_{cope}.txt'

# roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'ROIs')
roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'Test_area', 'ROI_testing')

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

subs_to_run = ['sub-EM0179']

#Create a dictionary of all ROI files.
#Keys will be region names, values will be full file path/names.
roi_dict = {}
#This dictionary will house all the ROI means and input files
output_dict = {}

cope_labels = {
               'reapGTflow':'4',
               'distGTflow':'5'
               }

print('---------------------------------------------------')
print('Participants to run: {}'.format(subs_to_run))
print('Cope labels to run: {}'.format(cope_labels.keys()))

if not os.path.exists(roi_dir):
    print('ROI input directory cannot be found! {}'.format(roi_dir))
    raise RuntimeError
else:
    for element in os.listdir(roi_dir):
        file_parts = element.split('_')
        if (len(file_parts)==4) and (file_parts[0]=='ROI') and (file_parts[-1]=='resamp.nii.gz'):
            #We've found an ROI image file
            print('Found ROI file: {}'.format(element))
            roi_dict[file_parts[1]] = os.path.join(roi_dir, element)

for sub in subs_to_run:
    #Make sure the input directory is there
    if not os.path.exists(input_dir.format(sub=sub, ses=ses)):
        print('Input directory cannot be found for subject {}! {}'.format(sub,input_dir.format(sub=sub,ses=ses)))
        raise RuntimeError

    #Look for the output for cope4 (reap>flow) and cope5 (dist>flow)
    for key in cope_labels:
        cope_file = os.path.join(input_dir.format(sub=sub,ses=ses), 'cope{}.feat'.format(cope_labels[key]), 'stats', 'cope1.nii.gz')
        if not os.path.exists(cope_file):
            print('Input cope image cannot be found! Sub: {sub}; File: {file}'.format(sub=sub,file=cope_file))
            raise RuntimeError

#If we get here, everything is ready to go
for sub in subs_to_run:
    output_dict[sub] = {}
    for cope in cope_labels:
        output_dict[sub][cope] = {}
        cope_file = os.path.join(input_dir.format(sub=sub,ses=ses), 'cope{}.feat'.format(cope_labels[cope]), 'stats', 'cope1.nii.gz')
        output_dict[sub][cope]['file'] = cope_file
        for roi in roi_dict:
            call_parts = [
                          '3dROIstats',
                          '-nzmean',
                          '-nomeanout',
                          '-quiet',
                          '-mask',
                          roi_dict[roi],
                          cope_file
                          ]
            #Save the ROI mean, as a string, into the dictionary
            output_dict[sub][cope][roi] = subprocess.check_output(call_parts).strip()

#Write the ROI means into .txt files
for cope in cope_labels:
    lines_to_write = ['sub\troi\tmean']
    output_file = os.path.join(output_dir, output_file_template.format(cope=cope))
    for roi in roi_dict:
        for sub in subs_to_run:
            lines_to_write.append('{sub}\t{roi}\t{mean}'.format(sub=sub,roi=roi,mean=output_dict[sub][cope][roi]))
    print('Writing file: {}'.format(output_file))
    with open(output_file, 'w') as fd:
        for line in lines_to_write:
            fd.write(line+'\n')


print('Done')
print('---------------------------------------------------')