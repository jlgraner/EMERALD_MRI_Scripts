
import subprocess
import os, shutil
import string
import time

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS')
fs_license = '/usr/local/freesurfer/license.txt'

retry = 0
#If retry is set to 1, the script will repeat up to 5 times upon erroring out.

subs_to_run = [
               'EM2562',
               'EM2569'
               ]

good_runs = []
bad_runs = []

for sub in subs_to_run:
  call_try = 1
  while call_try < 6:
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
              if retry:
                print('Waiting for 1 minute, then retrying.')
                time.sleep(60)
                call_try = call_try + 1
                #Delete failed attempt
                full_out_dir = os.path.join(output_dir, 'fmriprep', 'sub-{}'.format(sub))
                shutil.rmtree(full_out_dir)
                #From here, if call_try is less than 6, we loop back to the "while" above.
              else:
                call_try = 6
              print('-------------------------------------')
              bad_runs.append([sub])
       else:
              good_runs.append(sub)
              call_try = 6

print('--------------------------------------')
print('good_runs: {}'.format(good_runs))
print('\n')
print('bad_runs: {}'.format(bad_runs))
print('--------------------------------------')
print('Done')