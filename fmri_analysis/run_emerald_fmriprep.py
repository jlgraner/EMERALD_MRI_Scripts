
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/TEMP')
fs_license = '/usr/local/freesurfer/license.txt'

subs_to_run = [
               'EM0291'
               ]


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
                  'poldracklab/fmriprep:1.0.15',
                  '/data',
                  '/out',
                  'participant',
                  '--task', 'emoreg',
                  '--use-aroma',
                  '--ignore-aroma-denoising-errors',
                  '--output-space',
                  'template',
                  '--template-resampling-grid',
                  'native',
                  '--nthreads',
                  '4',
                  # '--low-mem',
                  # '-vvv',
                  '--fs-no-reconall',
                  '--participant_label',
                  'sub-{}'.format(sub)
                  ]

    print('Calling: {}'.format(string.join(call_parts)))
    subprocess.call(call_parts)
    print('Done')