
import os, subprocess
import shutil
import logging

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/Second_level_{sub}.gfeat')
feat_output_dir = 'featquery_{roi}_output'

final_output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/UT_PrePost_Comparison/ROI_Analysis_Output_zstat')
output_file_template = 'Group_ROI_means_fsl_{cope}.txt'

roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'ROIs')

#for each subject:
#	1) Locate the dist>flow map
#	2) Locate the reap>flow map
#	3) Locate mask images
#	4) Extract average activations:
#		a) dist>flow for dACC, dlPFC, inf. par.
#		b) reap>flow for vmPFC, vlPFC, amygdala
#	5) Save the average activations into an output file

ses = 'day3'
actually_run = 1

subs_to_run = [
              'UT0004',
              'UT0005',
              'UT0024',
              'UT0025'
                  ]

#Create a dictionary of all ROI files.
#Keys will be region names, values will be full file path/names.
roi_dict = {}
#This dictionary will house all the ROI means and input files
output_dict = {}

cope_labels = {
               'flow':'1',
               'reap':'2',
               'dist':'3',
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
        if (len(file_parts)==3) and (file_parts[0]=='ROI') and (file_parts[-1]=='final.nii.gz'):
            #We've found an ROI image file
            print('Found ROI file: {}'.format(element))
            roi_dict[file_parts[1]] = os.path.join(roi_dir, element)

print('Checking for input images...')
for sub in subs_to_run:
    #Make sure the input directory is there
    if not os.path.exists(input_dir.format(sub=sub, ses=ses)):
        print('Input directory cannot be found for subject {}! {}'.format(sub,input_dir.format(sub=sub,ses=ses)))
        raise RuntimeError

    #Look for the output for copes in list
    for key in cope_labels:
        cope_file = os.path.join(input_dir.format(sub=sub,ses=ses), 'cope{}.feat'.format(cope_labels[key]), 'stats', 'cope1.nii.gz')
        if not os.path.exists(cope_file):
            print('Input cope image cannot be found! Sub: {sub}; File: {file}'.format(sub=sub,file=cope_file))
            raise RuntimeError

#If we get here, everything is ready to go
for sub in subs_to_run:
    output_dict[sub] = {}
    print('Running Sub: {}'.format(sub))
    for cope in cope_labels:
        print('Contrast: {}'.format(cope))
        output_dict[sub][cope] = {}
        cope_dir = os.path.join(input_dir.format(sub=sub,ses=ses), 'cope{}.feat'.format(cope_labels[cope]))
        output_dict[sub][cope]['dir'] = cope_dir
        for roi in roi_dict:
            dir_to_delete = os.path.join(cope_dir, feat_output_dir.format(roi=roi))
            if os.path.exists(dir_to_delete):
              print('Output directory already there; DELETING it!')
              shutil.rmtree(dir_to_delete)
            call_parts = [
                          'featquery',
                          '1',
                          cope_dir,
                          '1',
                          'stats/cope1',
                          feat_output_dir.format(roi=roi),
                          # '-p',
                          '-b',
                          roi_dict[roi]
                          ]
            #Call featquery
            print('Calling: {}'.format(' '.join(call_parts)))
            if actually_run:
              error_flag = subprocess.call(call_parts)
              #Save the ROI mean, as a string, into the dictionary
              report_file = os.path.join(cope_dir, feat_output_dir.format(roi=roi), 'report.txt')
              with open(report_file) as fid:
                contents = fid.read()
              output_dict[sub][cope][roi] = contents.split()[5]

#Write the ROI means into .txt files
if actually_run:
  for cope in cope_labels:
      lines_to_write = ['sub\troi\tmean']
      output_file = os.path.join(final_output_dir, output_file_template.format(cope=cope))
      for roi in roi_dict:
          for sub in subs_to_run:
              lines_to_write.append('{sub}\t{roi}\t{mean}'.format(sub=sub,roi=roi,mean=output_dict[sub][cope][roi]))
      print('Writing file: {}'.format(output_file))
      with open(output_file, 'w') as fd:
          for line in lines_to_write:
              fd.write(line+'\n')


print('Done')
print('---------------------------------------------------')