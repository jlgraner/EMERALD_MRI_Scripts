
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/')
fs_license = '/usr/local/freesurfer/license.txt'

subs_to_run = ['EM0033', 'EM00036']

# subs_to_run = [
#               'EM0001'
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
              # 'EM0400'
               # ]


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