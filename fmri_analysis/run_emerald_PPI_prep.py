

import emerald_roi_analysis_lib as emlab
import os

##NOTE: this code is currently in "just-finish-it" mode and doesn't have decent error handling or logging

this_env = os.environ

sub_list = [
            'EM0400'
            ]

# run_list = ['1', '2', '3', '4']
run_list = ['1']


roi_list = ['amy']

delete_things = 0

roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'ROIs')
base_input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'fmriprep', 'sub-{sub}', 'ses-day3', 'func')

base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'Test_area', 'ROI_testing')

masking_info = {}

for sub in sub_list:
    things_to_delete = []
    sub_input_dir = base_input_dir.format(sub=sub)
    sub_output_dir = base_output_dir
    for run in run_list:
        #Create a mean image of the 4D run data
        run_data = os.path.join(sub_input_dir, 'sub-{sub}_ses-day3_task-emoreg_run-0{run}_space-MNI152NLin6Asym_desc-smoothAROMAnonaggr_bold.nii.gz'.format(sub=sub, run=run))
        temp_mean_image = os.path.join(sub_output_dir, 'sub-{sub}_emoreg_run{run}_AROMApreproc_mean.nii.gz'.format(sub=sub, run=run))
        temp_mean_image = emlab.mean_image(run_data, temp_mean_image)

        things_to_delete.append(temp_mean_image)

        #Create a histogram of the mean image
        x_array, y_array = emlab.create_histo(run_data)

        #Split the histogram where the deriviative changes
        x_first, y_first, x_last, y_last = emlab.split_histo(x_array, y_array)

        #Save some plots for debugging
        full_plot = os.path.join(sub_output_dir, 'sub-{}_run{}_histo_plot.png'.format(sub, run))
        emlab.save_plot([x_first, x_last], [y_first, y_last], full_plot, sub, run)

        raise RuntimeError('QUITTING')

        #Fit a gaussian to the latter portion of the histogram
        opt_params = emlab.fit_gauss(x_last, y_last)

        #Divide the center of the gaussian by two (NOTE: THIS IS A ROUGH APPROXIMATION OF THE DOUBLE-GAUSS METHOD!!!)
        int_thresh = opt_params[1]/2.0

        #Save a bunch of stuff
        masking_info[sub] = {}
        masking_info[sub][run] = {}
        masking_info[sub][run]['int_thresh'] = int_thresh
        masking_info[sub][run]['x_first'] = x_first
        masking_info[sub][run]['y_first'] = y_first
        masking_info[sub][run]['x_last'] = x_last
        masking_info[sub][run]['y_last'] = y_last
        masking_info[sub][run]['x_array'] = x_array
        masking_info[sub][run]['y_array'] = y_array
        masking_info[sub][run]['opt_params'] = opt_params

        for roi in roi_list:
            #Create a new mask for each run, keeping only voxels that are in both the Amygdala ROI
            #and the intensity-thresholded mask.
            roi_file = os.path.join(roi_dir, 'ROI_{}_final.nii.gz'.format(roi))
            output_file = os.path.join(sub_output_dir, 'sub_{}_run{}_ROI_{}_final.nii.gz'.format(sub,run,roi))

            new_roi_file = emlab.mask_roi(temp_mean_image, roi_file, output_file, int_thresh)

            things_to_delete.append(new_roi_file)

            #Store the file name into the info dictionary
            masking_info[sub][run][roi] = {}
            masking_info[sub][run][roi]['mask_file'] = new_roi_file

    #Create final ROI masks for this subject
    for roi in roi_list:
        mask_list = []
        roi_file = os.path.join(roi_dir, 'ROI_{}_final.nii.gz'.format(roi))
        final_output_roi = os.path.join(sub_output_dir, 'sub_{}_ROI_{}_final.nii.gz'.format(sub,roi))
        mul_part = ''
        for run in masking_info[sub].keys():
            mul_part.append('-mul')
            mul_part.append(masking_info[sub][run][roi]['mask_file'])
        call_parts = [
                      'fslmaths',
                      roi_file
                      ]
        for element in mul_part:
            call_parts.append(element)
        call_parts.append(final_output_roi)

        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()


    for element in things_to_delete:
        if delete_things:
            if os.path.exists(element):
                os.remove(element)