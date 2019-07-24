
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD_UT')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep_UT')
fs_license = '/usr/local/freesurfer/license.txt'

subs_to_run = [
               'UT0003',
               'UT0004',
               'UT0005',
               'UT0013',
               'UT0014',
               'UT0015',
               'UT0025'
               ]


for sub in subs_to_run:
    call_parts = [
                  'docker',
                  'run',
                  '-it',
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
    subprocess.call(call_parts)
    print('Done')