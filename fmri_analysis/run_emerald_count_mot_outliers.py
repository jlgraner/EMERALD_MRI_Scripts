
import os

this_env = os.environ

##############################################
##  PURPOSE: 
##
##  USAGE:   
##
##  VARS:    
###################################################

subs_to_run = [
              'EM0001',
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
              'EM0519',
              'EM0565',
              'EM0588',
              'EM0560',
              'EM0569',
              'EM0812',
              'EM0787',
              'EM0880',
              'EM1050',
              'EM0946',
              'EM1201',
              'EM1657',
              'EM1611',
              'EM1569',
              'EM1708'
              ]



ses_to_run = ['day3']
runs_to_run = ['1', '2', '3', '4']

confound_file_base_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/sub-{sub}/ses-day3/func/')
confound_file_base_name = 'sub-{sub}_ses-day3_task-emoreg_run-0{run}_desc-confounds_regressors_forFSL.tsv'

output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/')
output_file = os.path.join(output_dir, 'motion_outlier_counts.csv')

confounds_to_include = [
                        'motion_outlier'
                        ]

good_runs = []
failed_runs = []

output_header = 'sub,run,motion_outliers,perc_motion_outliers'

output_lines = []
output_lines.append(output_header)

#
for sub in subs_to_run:
    for run in runs_to_run:
        try:
            confound_dir = confound_file_base_dir.format(sub=sub)
            confound_name = confound_file_base_name.format(sub=sub, run=run)
            confound_file = os.path.join(confound_dir, confound_name)

            if not os.path.exists(confound_file):
                print('Confound file cannot be found: {}'.format(confound_file))
                raise RuntimeError('confound_file_missing')

            #Open the confound file and read in the first (header_ line)
            with open(confound_file, 'r') as fid:
              header_line = fid.readline()

            motion_outlier_count = len(header_line.split('motion_outlier')) - 1
            if run in ['1','3']:
                trs = '236'
            else:
                trs = '215'
            perc_motion_outlier = (float(motion_outlier_count)/float(trs)) * 100.0

            line_to_add = '{},{},{},{}'.format(sub,run,motion_outlier_count,perc_motion_outlier)
            output_lines.append(line_to_add)
            good_runs.append([sub,run])
        except Exception as err:
            print('Error running sub {}, run {}'.format(sub,run))
            print(err)
            failed_runs.append([sub,run,err])
            
print('Writing file: {}'.format(output_file))            
with open(output_file, 'w') as fid:
  for element in output_lines:
    fid.write('{}\n'.format(element))

print('---------------------------------------')
print('Good Runs: {}'.format(good_runs))
print('Failed Runs: {}'.format(failed_runs))
print('---------------------------------------')
print('Done!')