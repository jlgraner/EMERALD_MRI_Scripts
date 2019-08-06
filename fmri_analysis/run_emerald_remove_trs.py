
import os, sys

#This script simply calls 3dTcat on the fmri data preprocessed by fmriprep to remove
#the first 4 TRs.

this_env = os.environ

overwrite = 0

subs_to_run = ['EM0381']

# subs_to_run = [
#               'EM0001',
#               'EM0033',
#               'EM0036',
#               'EM0038',
#               'EM0066',
#               'EM0071',
#               'EM0088',
#               'EM0126',
#               'EM0153',
#               'EM0155',
#               'EM0162',
#               'EM0164',
#               'EM0174',
#               'EM0179',
#               'EM0184',
#               'EM0187',
#               'EM0192',
#               'EM0202',
#               'EM0206',
#               'EM0217',
#               'EM0219',
#               'EM0220',
#               'EM0223',
#               'EM0229',
#               'EM0240',
#               'EM0291',
#               'EM0304'
#                ]

runs_to_run = ['1','2','3','4']

good_runs = []
failed_runs = []

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/sub-{s}/ses-day3/func/')

for sub in subs_to_run:
    for run in runs_to_run:
        try:
            #Put together the input file
            print('---------------------------------------')
            input_file = 'sub-{s}_ses-day3_task-emoreg_run-0{r}_space-MNI152NLin6Asym_desc-smoothAROMAnonaggr_bold.nii.gz'
            full_input = os.path.join(base_input_dir, input_file).format(s=sub,r=run)

            #Put together the output file
            output_file = 'sub-{s}_emoreg_run{r}_AROMApreproc_short.nii.gz'
            full_output = os.path.join(base_input_dir, output_file).format(s=sub,r=run)

            #Put together call to 3dTcat
            ct_call = "3dTcat -prefix {output} {input}'[4..$]'".format(output=full_output,input=full_input)

            #Check to see if output is already there
            ##TODO: the following flow should be set so there's only one copy of the call
            if os.path.exists(full_output):
                if overwrite:
                    print('Deleting existing output: {}'.format(full_output))
                    os.remove(full_output)

                    #Pass call to terminal
                    print('Removing first 4 TRs from preprocessed data. Subject {}, run {}.'.format(sub,run))
                    print('Input: {}'.format(full_input))
                    print('Output: {}'.format(full_output))
                    os.system(ct_call)
                else:
                    print('Output file already exists and overwrite is not set!')
                    print('Subject {}, run {}'.format(sub,run))
                    print('EXITTING!')
                    sys.exit()
            else:
                #Pass call to terminal
                print('Removing first 4 TRs from preprocessed data. Subject {}, run {}.'.format(sub,run))
                print('Input: {}'.format(full_input))
                print('Output: {}'.format(full_output))
                os.system(ct_call)
                good_runs.append([sub,run])
        except Exception as ex:
            failed_runs.append([sub,run,ex])

        print('---------------------------------------')
