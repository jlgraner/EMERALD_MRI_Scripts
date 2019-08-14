

import os, shutil

#This script moves .feat directories around.
#USE WITH CAUTION

this_env = os.environ

base_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{s}/Func/')
output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{s}/Func/old_feats/')

# subs_to_run = ['EM0001']

subs_to_run = [
              'EM0001',
              'EM0033',
              'EM0036',
              'EM0038',
              'EM0066',
              'EM0071',
              'EM0088',
              'EM0126',
              'EM0153',
              'EM0155',
              'EM0162',
              'EM0164',
              'EM0174',
              'EM0179',
              'EM0184',
              'EM0187',
              'EM0192',
              'EM0202',
              'EM0206',
              'EM0217',
              'EM0219',
              'EM0220',
              'EM0223',
              'EM0229',
              'EM0240',
              'EM0291'
              ]


for sub in subs_to_run:
    for contents in os.listdir(base_dir.format(s=sub)):
        print('{}'.format(contents))
        # if ('.feat' in contents) and os.path.isdir(os.path.join(base_dir, contents)):
        if '.feat' in contents:
            to_move = os.path.join(base_dir.format(s=sub), contents)
            target_dir = output_dir.format(s=sub)
            if not os.path.exists(target_dir):
              print('Creating old feat directory: {}'.format(target_dir))
              os.makedirs(target_dir)
            print('Moving directory: {}'.format(to_move))
            print('Target directory: {}'.format(target_dir))
            shutil.move(to_move, target_dir)