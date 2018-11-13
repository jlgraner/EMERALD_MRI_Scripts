
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/new_fmriprep')
fs_license = '/usr/local/freesurfer/license.txt'

subs_to_run = [
              'sub-EM0001',
              'sub-EM0033',
              'sub-EM0036',
              'sub-EM0038',
              'sub-EM0066',
              'sub-EM0071',
              'sub-EM0088',
              'sub-EM0126',
              'sub-EM0153',
              'sub-EM0155',
              'sub-EM0162',
              'sub-EM0164',
              'sub-EM0174',
              'sub-EM0179',
              'sub-EM0184',
              'sub-EM0187',
              'sub-EM0192',
              'sub-EM0202',
              'sub-EM0206',
              'sub-EM0217',
              'sub-EM0219',
              'sub-EM0220',
              'sub-EM0223',
              'sub-EM0240'
               ]


# for sub in subs_to_run:
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
              '--participant_label'
              ]

for sub in subs_to_run:
  call_parts.append(sub)

print('Calling: {}'.format(string.join(call_parts)))
subprocess.call(call_parts)
print('Done')