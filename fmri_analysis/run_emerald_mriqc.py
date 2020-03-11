
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'mriqc')


subs_to_run = [
               'EM1657',
               'EM1611',
               'EM1569',
               'EM1708'
               ]

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
#                'EM0291',
#                'EM0304',
#                'EM0381'
#                ]


good_runs = []
bad_runs = []

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
    error_flag = subprocess.call(call_parts)

    if error_flag:
        print('-------------------------------------')
        print('Subject failed to run: {}'.format([sub,'emoreg']))
        print('-------------------------------------')
        bad_runs.append([sub,'emoreg'])
    else:
        good_runs.append([sub,'emoreg'])


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
    error_flag = subprocess.call(call_parts)

    if error_flag:
        print('-------------------------------------')
        print('Subject failed to run: {}'.format([sub,'T1']))
        print('-------------------------------------')
        bad_runs.append([sub,'T1'])
    else:
        good_runs.append([sub,'T1'])

print('--------------------------------------')
print('good_runs: {}'.format(good_runs))
print('\n')
print('bad_runs: {}'.format(bad_runs))
print('--------------------------------------')
print('Done')