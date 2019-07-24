
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'mriqc')


subs_to_run = ['EM0500', 'EM0519', 'EM0525']

# subs_to_run = [
#                'EM0001',
#                'EM0033',
#                'EM0036',
#                'EM0038',
#                'EM0066',
#                'EM0071',
#                'EM0088',
#                'EM0126',
#                'EM0153',
#                'EM0155',
#                'EM0162',
#                'EM0164',
#                'EM0174',
#                'EM0179',
#                'EM0184',
#                'EM0192',
#                'EM0202',
#                'EM0206',
#                'EM0217',
#                'EM0219',
#                'EM0220',
#                'EM0223',
#                'EM0229',
#                'EM0240',
#                'EM0304',
#                'EM0381'
#                ]


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
    subprocess.call(call_parts)