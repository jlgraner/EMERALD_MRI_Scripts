
import subprocess
import os
import string


this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/EMERALD_UT')
output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/mriqc_UT')

subs_to_run = [
               'UT0024'
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
                  'poldracklab/mriqc:latest',
                  '/data',
                  '/out',
                  'participant',
                  '--ica',
                  '--no-sub',
                  '--task-id', 'emoreg',
                  '--participant_label',
                  sub
                  ]

    print('Calling: {}'.format(string.join(call_parts)))
    subprocess.call(call_parts)

    other_call_parts = [
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
                        'participant',
                        '--ica',
                        '--no-sub',
                        '--modalities', 'T1w',
                        '--participant_label',
                        sub
                        ]
    print('Calling: {}'.format(string.join(other_call_parts)))
    subprocess.call(other_call_parts)