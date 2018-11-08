
import subprocess
import os
import string


input_dir = '[BIDS EMERALD]'
output_dir = '[BIDS mriqc]'

subs_to_run = [
               'EM0291'
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
                  '--fft-spikes-detector',
                  '--no-sub',
                  '--participant_label',
                  'sub-{}'.format(sub)
                  ]

    print('Calling: {}'.format(string.join(call_parts)))
    subprocess.call(call_parts)