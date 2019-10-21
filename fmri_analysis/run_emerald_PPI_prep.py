

import emerald_roi_analysis_lib as emlab
import os
import subprocess

##NOTE: this code is currently in "just-finish-it" mode and doesn't have decent error handling or logging

this_env = os.environ

sub_list = [
            'EM0071',
            'EM0206'
            ]

run_list = ['1', '2', '3', '4']
# run_list = ['1']


roi_list = ['amy']

delete_things = 1

roi_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'ROIs')
base_input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'fmriprep', 'sub-{sub}', 'ses-day3', 'func')

# base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'Test_area', 'ROI_testing')
base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI')
png_output_dir = os.path.join(base_output_dir, 'PPI_Prep_Fit_Plots_source')

masking_info = {}

if not os.path.exists(png_output_dir):
    os.makedirs(png_output_dir)

for sub in sub_list:
    things_to_delete = []
    masking_info[sub] = {}
    sub_input_dir = base_input_dir.format(sub=sub)
    sub_output_dir = os.path.join(base_output_dir, 'sub-{}'.format(sub), 'Func', 'Intensity_Masked_ROIs')
    if not os.path.exists(sub_output_dir):
        os.makedirs(sub_output_dir)
    for run in run_list:
        masking_info[sub][run] = {}
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
        full_plot = os.path.join(png_output_dir, 'sub-{}_run{}_histo_plot.png'.format(sub, run))
        emlab.save_plot([x_first, x_last], [y_first, y_last], full_plot, sub, run)

        #Fit a gaussian to the latter portion of the histogram
        opt_params = emlab.fit_gauss(x_last, y_last)

        #Plot the fit
        x_gauss = x_last
        y_gauss = emlab.gauss_model(x_gauss, opt_params[0], opt_params[1], opt_params[2])
        fit_plot = os.path.join(png_output_dir, 'sub-{}_run{}_fit_plot.png'.format(sub, run))
        emlab.save_plot([x_gauss, x_last], [y_gauss, y_last], fit_plot, sub, run)

        #Divide the center of the gaussian by two (NOTE: THIS IS A ROUGH APPROXIMATION OF THE DOUBLE-GAUSS METHOD!!!)
        int_thresh = opt_params[1]/2.0

        #Save a bunch of stuff
        masking_info[sub][run]['int_thresh'] = int_thresh
        masking_info[sub][run]['x_first'] = x_first
        masking_info[sub][run]['y_first'] = y_first
        masking_info[sub][run]['x_last'] = x_last
        masking_info[sub][run]['y_last'] = y_last
        masking_info[sub][run]['x_array'] = x_array
        masking_info[sub][run]['y_array'] = y_array
        masking_info[sub][run]['opt_params'] = opt_params
        masking_info[sub][run]['histo_png'] = full_plot
        masking_info[sub][run]['fit_png'] = fit_plot

        for roi in roi_list:
            #Create a new mask for each run, keeping only voxels that are in both the Amygdala ROI
            #and the intensity-thresholded mask.
            roi_file = os.path.join(roi_dir, 'ROI_{}_final.nii.gz'.format(roi))
            output_file = os.path.join(sub_output_dir, 'sub_{}_run{}_ROI_{}_final.nii.gz'.format(sub,run,roi))

            if os.path.exists(output_file):
                os.remove(output_file)

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
        call_parts = [
                      'fslmaths',
                      roi_file
                      ]
        for run in masking_info[sub].keys():
            call_parts.append('-mul')
            call_parts.append(str(masking_info[sub][run][roi]['mask_file']))
        
        call_parts.append(final_output_roi)

        if os.path.exists(final_output_roi):
            os.remove(final_output_roi)
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()

    #Create an html file linking all the png files
    html_file = emlab.write_html(masking_info, base_output_dir)


    for element in things_to_delete:
        if delete_things:
            if os.path.exists(element):
                os.remove(element)
        else:
            print('Would delete: {}'.format(element))