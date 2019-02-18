
import os
import subprocess


this_env = os.environ

#Apply temporal filtering to fMRI data that have been through fmriprep

sub_list = [
            'EM0001'
            ]

run_list = ['3']

base_input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'fmriprep')

good_runs = []
bad_runs = []

for sub in sub_list:
    sub_dir = os.path.join(base_input_dir, 'sub-{}'.format(sub), 'ses-day3', 'func')
    for run in run_list:
        #Set the input image filename
        input_image = os.path.join(sub_dir, 'sub-{}_emoreg_run{}_AROMApreproc_short.nii.gz'.format(sub, run))
        #Create the temporal mean filename
        temp_tmean_filename = 'sub-{}_emoreg_run{}_AROMApreproc_short_tmean.nii.gz'.format(sub, run)
        temp_tmean_output = os.path.join(sub_dir, temp_tmean_filename)
        #If the temporal mean file already exists, delete it
        if os.path.exists(temp_tmean_output):
            print('Temporal mean file exists: {}'.format(temp_tmean_output))
            print('Deleting it!!!')
            os.remove(temp_tmean_output)
        #Create the call to fslmaths that will calculate the temporal mean
        call_parts = [
                      'fslmaths',
                      input_image,
                      '-Tmean',
                      temp_tmean_output
                      ]
        #Carry out temporal mean creation
        process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            print('Something went wrong creating mean functional image for {}!'.format(sub))
            print(err)
            bad_runs.append([sub, run, 'func_mean'])
            raise RuntimeError()

        #Create the temporal-filtered image filename
        temp_filt_filename = 'sub-{}_emoreg_run{}_AROMApreproc_short_tempfilt.nii.gz'.format(sub, run)
        temp_filt_output = os.path.join(sub_dir, temp_filt_filename)
        #If the filtered data already exists, delete it
        if os.path.exists(temp_filt_output):
            print('Filtered file exists: {}'.format(temp_filt_output))
            print('Deleting it!!!')
            os.remove(temp_filt_output)
        #Create call to fslmaths that will run the temporal filtering
        call_parts = [
                      'fslmaths',
                      input_image,
                      '-bptf', '25', '-1',
                      '-add', temp_tmean_output,
                      temp_filt_output
                      ]
        #Carry out temporal filtering
        process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            print('Something went wrong creating mean functional image for {}!'.format(sub))
            print(err)
            bad_runs.append([sub, run, 'temporal_filtering'])
            raise RuntimeError()
        #Delete the mean image
        os.remove(temp_tmean_output)
        #Add the run to the list of good runs
        good_runs.append([sub, run])

print('Done!')
print('---------------------------------------------')
print('good_runs: {}'.format(good_runs))
print('bad_runs: {}'.format(bad_runs))
print('---------------------------------------------')