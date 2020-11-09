

import os, shutil
import subprocess
import pandas


this_env = os.environ

# sub_list = [
#             'EM0565',
#             'EM0588',
#             'EM0560',
#             'EM0673',
#             'EM0573',
#             'EM0643',
#             'EM0812',
#             'EM0787',
#             'EM0880',
#             'EM1050',
#             'EM0946'
#             ]

sub_list = [
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
            # 'EM0182',
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
            'EM0673',
            'EM0573',
            'EM0643',
            'EM0812',
            'EM0787',
            'EM0880',
            'EM1050',
            'EM0946',
            'EM1201',
            'EM1657',
            'EM1611',
            'EM1569',
            'EM1708',
            'EM2562',
            'EM2569'
            ]

tract_list = [
              'L_SLFII',
              'R_SLFII',
              'L_Unc',
              'R_Unc'
              ]

bad_runs = []
good_runs = []

base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'DTI_FA_06172020')
#If the output directory does not exist, create it
if not os.path.exists(base_output_dir):
    print('Output directory not found; creating it: {}'.format(base_output_dir))
    os.mkdir(base_output_dir)

output_file = os.path.join(base_output_dir, 'DTI_tract_FAs_06172020.csv')

##Calculate average FA for each subject for each tract
all_fa_dictionary = {}
all_fa_dictionary['subID'] = sub_list
for tract in tract_list:
    tract_fa_list = []
    for sub in sub_list:
        try:
            sub_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{}'.format(sub), 'DWI')
            fa_file = os.path.join(sub_dir, 'sub-{}_ses-day3_dwi_d_ss_prep_ss_bc_fa_final.nii.gz'.format(sub))
            tract_roi_file = os.path.join(sub_dir, '{}_tractROI_{}_final.nii.gz'.format(tract, sub))

            #Save the region's FA into the list
            call_parts = [
                          '3dROIstats',
                          '-mask', tract_roi_file,
                          '-nomeanout',
                          '-nzmean',
                          '-quiet',
                          fa_file
                          ]
            process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if err != '':
                if 'If you are performing spatial transformations on an oblique dset' not in err:
                    bad_runs.append([sub, tract, 'ave_FA'])
                    print('Error extracting average FA for {}, {}'.format(sub, tract))
                    # raise RuntimeError('Error extracting average FA for {}, {}'.format(sub, tract))
                    tract_fa_list.append('NaN')
                else:
                    print('Got a deoblique warning from 3dROIstats for {}, {}'.format(sub, tract))
                    tract_fa_list.append(out.strip())
            else:
                tract_fa_list.append(out.strip())
            good_runs.append([sub, tract])
        except Exception as err_gen:
            print('Ran into odd problems extracting average FA for {}, {}\n{}'.format(sub, tract, err_gen))
    #Save the FAs into a dictionary
    all_fa_dictionary[tract] = tract_fa_list

#Convert the big dictionary into a pandas data frame
all_fa_dataframe = pandas.DataFrame(all_fa_dictionary)

#Save the pandas data frame as a csv
print('Saving FA data frame to file: {}'.format(output_file))
all_fa_dataframe.to_csv(path_or_buf=output_file, sep=',', index=False)
print('Done!')

print('---------------------------------------')
print('good_runs: {}'.format(good_runs))
print('bad_runs: {}'.format(bad_runs))
print('---------------------------------------')
