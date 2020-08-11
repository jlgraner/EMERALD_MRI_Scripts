
import os, sys
import emerald_preproc_lib as epl

#This script calls functions in the emerald_preproc_lib to:
#1) Remove the first 4 TRs of the post-fmriprep image.
#2) Apply temporal filtering to the post-fmriprep image.
#3) Mask the post-fmriprep image by the calculated brain mask.

this_env = os.environ

overwrite = 1
skip = 0

subs_to_run = ['EM1655']

# subs_to_run = [
#                'EM0126',
#                'EM0153',
#                'EM0155',
#                'EM0162',
#                'EM0164',
#                'EM0174',
#                'EM0179',
#                'EM0184',
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
#                'EM0360',
#                'EM0400',
#                'EM0500',
#                'EM0519'
#               ]

runs_to_run = ['1','2','3','4']
# runs_to_run = ['1', '2', '3']

good_runs = []
failed_runs = []

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/sub-{s}/ses-day3/func/')
# base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep_UT/fmriprep/fmriprep/sub-{s}/ses-day3/func/')

for sub in subs_to_run:
    for run in runs_to_run:
        try:
            #Run the AROMA version
            #Put together the input file
            print('---------------------------------------')
            input_file = 'sub-{s}_ses-day3_task-emoreg_run-0{r}_space-MNI152NLin6Asym_desc-smoothAROMAnonaggr_bold.nii.gz'
            full_input = os.path.join(base_input_dir, input_file).format(s=sub,r=run)

            #Put together the mask file
            mask_file = 'sub-{s}_ses-day3_task-emoreg_run-0{r}_space-MNI152NLin6Asym_desc-brain_mask.nii.gz'
            full_mask = os.path.join(base_input_dir, mask_file).format(s=sub,r=run)

            #Put together base output image name
            new_file = 'sub-{s}_emoreg_run{r}_AROMApreproc.nii.gz'
            new_image = os.path.join(base_input_dir, new_file).format(s=sub,r=run)

            #See if the full output image name is already there
            full_output_image = new_image[:-7]+'_short_tempfilt_brain.nii.gz'
            if os.exists(full_output_image):
                print('Final output image already exists!')
                raise RuntimeError('Image already there')

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

            #Mask the image
            masked_image = epl.apply_mask(temp_image, full_mask, overwrite=0, skip=skip)
            if masked_image is None:
              raise RuntimeError('Masking')

            #Remove intermediate images
            epl.remove_file(new_image)
            epl.remove_file(short_image)
            epl.remove_file(temp_image)

            good_runs.append([sub,run, 'AROMA'])
        except Exception as ex:
            failed_runs.append([sub,run,'AROMA',ex])

        try:
            #Run the non-AROMA version both with smoothing and without smoothing
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

            #See if the full output image name is already there
            skip_smooth = 0
            skip_nosmooth = 0
            smooth_output_image = new_image[:-7]+'_short_tempfilt_smooth_brain.nii.gz'
            if os.exists(smooth_output_image):
                skip_smooth = 1
                print('------------------------------')
                print('Smoothed output already there!')
                print('------------------------------')
            full_output_image = new_image[:-7]+'_short_tempfilt_brain.nii.gz'
            if os.exists(full_output_image):
                skip_nosmooth = 1
                print('------------------------------')
                print('Non-smoothed output already there!')
                print('------------------------------')
            if skip_smooth and skip_nosmooth:
                raise RuntimeError('Both non-AROMA outputs already there!')

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

            if not skip_smooth:
                #Smooth and mask the image
                smoothed_image = epl.smooth(temp_image, full_mask, overwrite=0)
                if smoothed_image is None:
                    raise RuntimeError('Smoothing')

            if not skip_nosmooth:
                #Mask the image
                masked_image = epl.apply_mask(temp_image, full_mask, overwrite=0, skip=skip)
                if masked_image is None:
                  raise RuntimeError('Masking')

            #Remove intermediate images
            epl.remove_file(new_image)
            epl.remove_file(short_image)
            epl.remove_file(temp_image)

            good_runs.append([sub,run,'noAROMA'])
        except Exception as ex:
            failed_runs.append([sub,run,'noAROMA',ex])

print('---------------------------------------')
print('Good Runs: {}'.format(good_runs))
print('Bad Runs: {}'.format(failed_runs))
print('---------------------------------------')