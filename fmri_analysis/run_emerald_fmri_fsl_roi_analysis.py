
import os, subprocess
import shutil
import logging
import emerald_roi_analysis_lib as eral

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/Second_level_allruns.gfeat')
feat_output_dir = 'featquery_{roi}_output'

final_output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_Analysis_Output')
output_file_template = 'Group_ROI_means_fsl_{cope}.txt'

# roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'ROIs')
roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{sub}', 'Func', 'Intensity_Masked_ROIs')

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

subs_to_run = ['EM0569']
# subs_to_run = [
              # 'EM0001',
              # 'EM0033',
              # 'EM0036',
              # 'EM0038',
              # 'EM0066',
              # 'EM0071',
              # 'EM0088',
              # 'EM0126',
              # 'EM0153',
              # 'EM0155',
              # 'EM0162',
              # 'EM0164',
              # 'EM0174',
              # 'EM0179',
              # 'EM0184',
              # 'EM0187',
              # # 'EM0188',
              # 'EM0192',
              # 'EM0202',
              # 'EM0206',
              # 'EM0217',
              # 'EM0219',
              # 'EM0220',
              # 'EM0223',
              # 'EM0229',
              # 'EM0240',
              # 'EM0291',
              # 'EM0304',
              # 'EM0381',
              # 'EM0360',
              # 'EM0400',
              # 'EM0500',
              # 'EM0519',
              # 'EM0565',
              # 'EM0588',
              # 'EM0560',
              # 'EM0569'
              #     ]

# roi_list = ['amy', 'dACC', 'dlPFC', 'infPar', 'vlPFC', 'vmPFC']
roi_list = ['amy']
#This dictionary will house all the ROI means and input files
output_dict = {}

cope_labels = {
                'reapGTflow':'4'
              }

# cope_labels = {
#                'reapGTflow':'4',
#                'distGTflow':'5'
#                }

print('---------------------------------------------------')
print('Participants to run: {}'.format(subs_to_run))
print('Cope labels to run: {}'.format(cope_labels.keys()))

print('Checking for input images...')
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

    #Look for masked ROIs
    for roi in roi_list:
      roi_file = os.path.join(roi_dir.format(sub=sub), 'sub_{sub}_ROI_{roi}_final.nii.gz'.format(sub=sub,roi=roi))
      if not os.path.exists(roi_file):
        print('Input ROI mask image cannot be found! Sub: {sub}; File: {file}'.format(sub=sub,file=roi_file))
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
        for roi in roi_list:
            output_dict[sub][cope][roi] = {}
            dir_to_delete = os.path.join(cope_dir, feat_output_dir.format(roi=roi))
            roi_file = os.path.join(roi_dir.format(sub=sub), 'sub_{sub}_ROI_{roi}_final.nii.gz'.format(sub=sub,roi=roi))
            if os.path.exists(dir_to_delete):
              print('Output directory already there; DELETING it!')
              shutil.rmtree(dir_to_delete)
            report_file = eral.run_featquery(cope_dir=cope_dir, output_dir=feat_output_dir.format(roi=roi), roi_file=roi_file)
            peak_file = os.path.join(cope_dir, feat_output_dir.format(roi=roi), 'peak_coords.txt')
            if report_file is not None:
              with open(report_file) as fid:
                contents = fid.read()
            else:
              raise RuntimeError
            output_dict[sub][cope][roi]['mean'] = contents.split()[5]
            output_dict[sub][cope][roi]['max'] = contents.split()[8]
            output_dict[sub][cope][roi]['max_x'] = contents.split()[10]
            output_dict[sub][cope][roi]['max_y'] = contents.split()[11]
            output_dict[sub][cope][roi]['max_z'] = contents.split()[12]
            output_dict[sub][cope][roi]['max_xmm'] = contents.split()[13]
            output_dict[sub][cope][roi]['max_ymm'] = contents.split()[14]
            output_dict[sub][cope][roi]['max_zmm'] = contents.split()[15]
            output_dict[sub][cope][roi]['report_file'] = report_file
            output_dict[sub][cope][roi]['peak_file'] = peak_file

            #Write ROI peak centers for each participant for each ROI
            #These will be used by 3dUndump to create spherical sub-ROIs
            peak_line = '{x} {y} {z}'.format(x=output_dict[sub][cope][roi]['max_x'],y=output_dict[sub][cope][roi]['max_y'],z=output_dict[sub][cope][roi]['max_z'])
            with open(peak_file, 'w') as fid:
              fid.write(peak_line)


#Write the ROI means into .txt files
if actually_run:
  for cope in cope_labels:
      lines_to_write = ['sub\troi\tmean']
      output_file = os.path.join(final_output_dir, output_file_template.format(cope=cope))
      for roi in roi_list:
          for sub in subs_to_run:
              lines_to_write.append('{sub}\t{roi}\t{mean}'.format(sub=sub,roi=roi,mean=output_dict[sub][cope][roi]['mean']))
      print('Writing file: {}'.format(output_file))
      with open(output_file, 'w') as fd:
          for line in lines_to_write:
              fd.write(line+'\n')





print('Done')
print('---------------------------------------------------')