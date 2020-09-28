
import subprocess
import os
import string

this_env = os.environ

input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'EMERALD')
output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'mriqc')


subs_to_run = [
               'EM2562',
               'EM2569'
               ]


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