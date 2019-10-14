
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS')
fs_license = '/usr/local/freesurfer/license.txt'


# subs_to_run = [
#                'EM0565',
#                'EM0588',
#                'EM0560',
#                'EM0673',
#                'EM0573',
#                'EM0569',
#                'EM0643'
#               ]


subs_to_run = [
               "EM0560"
               ]

good_runs = []
bad_runs = []

for sub in subs_to_run:
       call_parts = [
                     'docker',
                     'run',
                     '-it',
                     # '-m',
                     # '20g',
                     '--rm',
                     '-v',
                     '{}:/data:ro'.format(input_dir),
                     '-v',
                     '{}:/out'.format(output_dir),
                     '-v',
                     '{}:/opt/freesurfer/license.txt'.format(fs_license),
                     'poldracklab/fmriprep:latest',
                     '/data',
                     '/out',
                     'participant',
                     '--task', 'emoreg',
                     '--use-aroma',
                     '--output-spaces', 'MNI152NLin6Asym:res-2',
                     '--dummy-scans', '4',
                     '--fd-spike-threshold', '0.3',
                     '--nthreads',
                     '4',
                     '--fs-no-reconall',
                     '--participant_label',
                     'sub-{sub}'.format(sub=sub)
                     ]

       print('Calling: {}'.format(string.join(call_parts)))
       error_flag = subprocess.call(call_parts)

       if error_flag:
              print('-------------------------------------')
              print('Subject failed to run: {}'.format(sub))
              print('-------------------------------------')
              bad_runs.append(sub)
       else:
              good_runs.append(sub)

print('--------------------------------------')
print('good_runs: {}'.format(good_runs))
print('\n')
print('bad_runs: {}'.format(bad_runs))
print('--------------------------------------')
print('Done')