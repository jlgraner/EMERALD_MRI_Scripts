
import os, sys
import emerald_preproc_lib as epl

#This script calls functions in the emerald_preproc_lib to:
#1) Remove the first 4 TRs of the post-fmriprep image.
#2) Apply temporal filtering to the post-fmriprep image.
#3) Mask the post-fmriprep image by the calculated brain mask.

this_env = os.environ

overwrite = 1
skip = 0

subs_to_run = ['EM0179', 'EM0184', 'EM0187']

# subs_to_run = [
#                # 'EM0033',
#                # 'EM0066',
#                'EM0071',
#                'EM0088',
#                'EM0126',
#                'EM0153',
#                'EM0155',
#                'EM0162',
#                'EM0164',
#                'EM0174',
#                'EM0179',
#                'EM0184',
#                'EM0187',
#                'EM0192',
#                'EM0202',
#                'EM0206',
#                'EM0217',
#                'EM0219',
#                'EM0220',
#                'EM0223',
#                'EM0229',
#                'EM0240',
#                'EM0291',
#                'EM0304',
#                'EM0381',
#                'EM0360',
#                # 'EM0500',
#                # 'EM0519',
#                'EM0565',
#                'EM0588',
#                'EM0560',
#                'EM0569'
#               ]

runs_to_run = ['1','2','3','4']
# runs_to_run = ['3', '4']

good_runs = []
failed_runs = []

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/sub-{s}/ses-day3/func/')
# base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/Test_area/fmri/Smooth_testing')

for sub in subs_to_run:
    for run in runs_to_run:
        try:
            #Put together the input file
            print('---------------------------------------')
            input_file = 'sub-{s}_ses-day3_task-emoreg_run-0{r}_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz'
            full_input = os.path.join(base_input_dir, input_file).format(s=sub,r=run)

            #Put together the mask file
            mask_file = 'sub-{s}_ses-day3_task-emoreg_run-0{r}_space-MNI152NLin6Asym_desc-brain_mask.nii.gz'
            full_mask = os.path.join(base_input_dir, mask_file).format(s=sub,r=run)

            #Put together base output image name
            new_file = 'sub-{s}_emoreg_run{r}_preproc.nii.gz'
            new_image = os.path.join(base_input_dir, new_file).format(s=sub,r=run)

            #Rename the image
            new_output = epl.rename_file(full_input, new_image)
            if new_output is None:
              raise RuntimeError('Renaming')

            #Remove the first 4 TRs from the data
            short_image = epl.remove_trs(new_image, cut_trs=4, overwrite=0, skip=skip)
            if short_image is None:
              raise RuntimeError('TR removal')

            #Apply temporal filter to the data
            temp_image = epl.tempfilt(short_image, skip=skip)
            if temp_image is None:
              raise RuntimeError('Temporal filter')

            #Smooth and mask the image
            smoothed_image = epl.smooth(temp_image, full_mask, overwrite=0)
            if smoothed_image is None:
                raise RuntimeError('Smoothing')

            # #Mask the image
            # masked_image = epl.apply_mask(temp_image, full_mask, overwrite=0, skip=skip)
            # if masked_image is None:
            #   raise RuntimeError('Masking')

            #Remove intermediate images
            epl.remove_file(new_image)
            epl.remove_file(short_image)
            epl.remove_file(temp_image)

            good_runs.append([sub,run])
        except Exception as ex:
            failed_runs.append([sub,run,ex])

print('---------------------------------------')
print('Good Runs: {}'.format(good_runs))
print('Bad Runs: {}'.format(failed_runs))
print('---------------------------------------')