

import os
import subprocess
import pandas

##
#This script creates a couple Explanatory Variable (EV) files to run PPI analysis in FSL.
#1) Time-course for seed ROIs of the PPI (here, Bilateral Amygdala and vlPFC)
#2) Contrast EVs for the pairs of conditions we want to compare (here, NegativeDistract-NegativeFlow
#   and NegativeReapraise-NegativeFlow).

##3dROIstats -mask ROI_amy_final_resamp.nii.gz -nomeanout -quiet -nzmean sub-EM0126_emoreg_run1_AROMApreproc_short.nii.gz

this_env = os.environ

run_list = ['1', '2', '3', '4']
# run_list = ['2', '3', '4']

# masks_to_apply = ['amy', 'dACC', 'dlPFC', 'infPar', 'vlPFC', 'vmPFC']
masks_to_apply = ['amy']

contrasts_to_make = [ ['diststrategycues', 'negflowstrategycues'], ['reapstrategycues', 'negflowstrategycues'] ]

subs_to_run = [
              # 'EM0001'
              'EM0033',
              'EM0036',
              'EM0038',
              'EM0066',
              'EM0071',
              'EM0088',
              'EM0126',
              'EM0153',
              'EM0155',
              'EM0162',
              'EM0164',
              'EM0174',
              'EM0179',
              'EM0184',
              'EM0187',
              'EM0192',
              'EM0202',
              'EM0206',
              'EM0217',
              'EM0219',
              'EM0220',
              'EM0223',
              'EM0229',
              'EM0240',
              'EM0291',
              'EM0304',
              'EM0381',
              'EM0360',
              'EM0400',
              'EM0500',
              'EM0519'
               ]


#Directory containing the event timing files
condition_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{sub}', 'Func', 'Condition_files')

#Directory containing the image files from which we'll extract the ROI time-courses
image_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'fmriprep', 'sub-{sub}', 'ses-day3', 'func')

#Directory containing masks to apply
mask_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'ROIs')

#Directory in which to write the new EV files
output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{sub}', 'Func', 'Condition_files')
# output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'Test_area', 'fmri')

good_runs = []
bad_runs = []

for sub in subs_to_run:
    print('-----------------------------------------')
    print('Subject: {}'.format(sub))
    for run in run_list:
        print('Run: {}'.format(run))
        #Extract ROI mask time-courses and save them to files
        try:
            for mask in masks_to_apply:
                print('Extracting ROI time-course for mask: {}'.format(mask))
                fmri_image = os.path.join(image_dir.format(sub=sub), 'sub-{}_emoreg_run{}_AROMApreproc_short_tempfilt.nii.gz'.format(sub,run))
                mask_image = os.path.join(mask_dir, 'ROI_{}_final.nii.gz'.format(mask))
                output_file = os.path.join(output_dir.format(sub=sub), 'sub-{sub}_emoreg_run{run}_AROMApreproc_short_{mask}_timecourse.txt'.format(sub=sub, run=run, mask=mask))

                call_parts = ['3dROIstats',
                              '-mask', mask_image,
                              '-nomeanout',
                              '-quiet',
                              '-nzmean',
                              fmri_image]

                print('Calling: {}'.format(' '.join(call_parts)))
                proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
                call_output, stderr = proc.communicate()
                with open(output_file, 'w') as fid:
                    fid.write('{}'.format(call_output.decode("utf-8").replace('\t','')))

            #Put together contrast EVs for PPI
            for first, second in contrasts_to_make:
                #Contrast EVs will be created setting the third column of the
                #"first" events to 1 and the third column of the "second" events
                #to -1.

                print('Putting together PPI contrast regressor for conditions:')
                print('Condition 1: {}'.format(first))
                print('Condition 2: {}'.format(second))
                #Create dataframe that will hold both sets of timings for a while
                appended_data = pandas.DataFrame(columns=['onset','duration','weight'])

                #Read in the contents of the first file
                first_file = os.path.join(condition_dir.format(sub=sub), '{sub}_run{run}_{cond}_fslconds.txt'.format(sub=sub, run=run, cond=first))
                first_data = pandas.read_csv(first_file, sep='\t', names=['onset','duration','weight'], engine='python')
                appended_data = pandas.concat([appended_data, first_data], ignore_index=True)

                #Read in the contents of the second file
                second_file = os.path.join(condition_dir.format(sub=sub), '{sub}_run{run}_{cond}_fslconds.txt'.format(sub=sub, run=run, cond=second))
                second_data = pandas.read_csv(second_file, sep='\t', names=['onset','duration','weight'], engine='python')
                second_data.loc[:,'weight'] = -1
                appended_data = pandas.concat([appended_data, second_data], ignore_index=True)

                #Sort the new event data frame by onset
                df_sorted = appended_data.sort_values(['onset'])

                #Write output file
                output_file = os.path.join(output_dir.format(sub=sub), '{sub}_run{run}_{first}-{second}_ppi.txt'.format(sub=sub,run=run,first=first,second=second))
                df_sorted.to_csv(path_or_buf=output_file, sep='\t', index=False, header=False)
                good_runs.append([sub,run,mask])
        except Exception as err:
            print('Something went wrong for {}, run {}!'.format(sub,run))
            bad_runs.append([sub,run,err])
print('-----------------------------------------')
print('Good Runs: {}'.format(good_runs))
print('Bad Runs: {}'.format(bad_runs))
print('-----------------------------------------')
