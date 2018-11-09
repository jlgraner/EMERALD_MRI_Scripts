
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/mriqc')


call_parts = [
              'docker',
              'run',
              '-it',
              '--rm',
              '-v',
              '{}:/data:ro'.format(input_dir),
              '-v',
              '{}:/out'.format(output_dir),
              'poldracklab/mriqc:latest',
              '/data',
              '/out',
              'group'
              ]

print('Calling: {}'.format(string.join(call_parts)))
subprocess.call(call_parts)