
#This script is meant to create a map for each ROI, showing
#where the participant-wise peak sphere masks overlap across the group.
#This needs to be run after run_emerald_fmri_fsl_roi_analysis.py.

import os
import emerald_roi_analysis_lib as eral

this_env = os.environ

sphere_mask_temp = os.path.join(this_env['EMDIR'],
                                'Analysis/MRI/sub-{sub}/Func/Second_level_allruns.gfeat/cope{cope_num}.feat/featquery_{roi}sphere_output/mask.nii.gz')

final_output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_Analysis_Output')
output_file_temp = 'Group_sphereROImap_{roi}_{cope}.nii.gz'


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
              # 'EM0188',
              'EM0192',
              'EM0202',
              'EM0206',
              'EM0217',
              'EM0219',
              'EM0220',
              'EM0223',
              'EM0229',
              'EM0240',
              'EM0291',
              'EM0304',
              'EM0381',
              'EM0360',
              'EM0400',
              'EM0500',
              'EM0519',
              'EM0565',
              'EM0588',
              'EM0560',
              'EM0569'
                  ]

roi_list = ['amy', 'dACC', 'dlPFC', 'infPar', 'vlPFC', 'vmPFC']

cope_labels = {
               'reapGTflow':'4',
               'distGTflow':'5'
               }

for cope_label in cope_labels:
    cope_num = cope_labels[cope_label]
    print('cope_label: {}'.format(cope_label))
    # print('cope_num: {}'.format(cope_num))
    for roi in roi_list:
        print('roi: {}'.format(roi))
        sphere_mask_list = []
        output_file = os.path.join(final_output_dir, output_file_temp.format(roi=roi, cope=cope_label))
        # print('output_file: {}'.format(output_file))
        #Create list of input sphere mask image files
        for sub in subs_to_run:
            sphere_mask = sphere_mask_temp.format(sub=sub,roi=roi,cope_num=cope_num)
            sphere_mask_list.append(sphere_mask)
        output_created = eral.run_mean(output_file, sphere_mask_list)
        # print('sphere_mask_list: {}'.format(sphere_mask_list))
        # output_created = 'hi'
        if output_created is None:
            print('Something went wrong created group sphere map for {}, {}!'.format(cope_label, roi))
        else:
            print('Output written: {}'.format(output_created))
print('Done!')