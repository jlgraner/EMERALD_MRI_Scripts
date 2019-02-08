
import os, shutil
import logging, time
import subprocess

this_env = os.environ

sub_list = [
            'EM0240'
            ]

# sub_list = [
#             # 'EM0001',
#             'EM0033',
#             'EM0036',
#             'EM0038',
#             'EM0066',
#             'EM0071',
#             'EM0088',
#             'EM0126',
#             'EM0153',
#             'EM0155',
#             'EM0162',
#             'EM0164',
#             'EM0174',
#             'EM0179',
#             # 'EM0182',
#             'EM0184',
#             'EM0187',
#             # 'EM0188',
#             'EM0192',
#             'EM0202',
#             'EM0206',
#             'EM0217',
#             'EM0219',
#             'EM0220',
#             'EM0223',
#             'EM0229',
#             'EM0240',
#             'EM0291'
#             ]

tract_list = [
              'L_SLFII',
              # 'R_SLFII',
              # 'L_Unc',
              # 'R_Unc'
              ]

bad_runs = []
good_runs = []

base_input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/DWI/')

for sub in sub_list:
    sub_dir = base_input_dir.format(sub=sub)
    preproc_dti = os.path.join(sub_input_dir, 'sub-{}_ses-{}_dwi_d_ss_prep_ss_bc.nii.gz'.format(sub,ses))
    #Align the FA file with the preprocessed DTI from the tract list
    fa_file = os.path.join(sub_dir, 'sub-{}_ses-day3_dwi_d_ss_prep_ss_bc_fa.nii.gz'.format(sub))
    centered_fa = fa_file.split('.nii.gz')[0]+'_shft.nii.gz'
    resampled_fa = fa_file.split('.nii.gz')[0]+'_final.nii.gz'

    call_parts = [
                  '@Align_Centers',
                  '-base', preproc_dti,
                  '-dset', fa_file
                  ]
    print('Running @Align_centers for {}, FA map'.format(sub))
    print('preproc_dti: {}'.format(preproc_dti))
    print('fa_file: {}'.format(fa_file))
    print(call_parts)
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('@Align_centers failed for subject {}, FA!'.format(sub))
        bad_runs.append([sub, 'FA', 'center align'])
        raise RuntimeError

    #Resample FA image to first tract mask
    call_parts = [
                  '3dresample',
                  '-master', preproc_dti,
                  '-inset', centered_fa,
                  '-prefix', resampled_fa
                  ]
    print('Running 3dresample for {}, FA'.format(sub))
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('3dresample failed for subject {}, FA!'.format(sub))
        bad_runs.append([sub, tract, 'resample'])
        raise RuntimeError

    for tract in tract_list:
        try:
            tract_mask_file = os.path.join(sub_dir, '{}_mask_{}.nii.gz'.format(tract, sub))
            tract_roi_file = os.path.join(sub_dir, '{}_tractROI_{}.nii.gz'.format(tract, sub))
            centered_roi_file = tract_roi_file.split('.nii.gz')[0]+'_shft.nii.gz'
            resampled_roi_file = tract_roi_file.split('.nii.gz')[0]+'_resamp.nii.gz'
            final_roi_file = tract_roi_file.split('.nii.gz')[0]+'_final.nii.gz'

            #Delete existing files if they are there
            for element in [centered_roi_file, resampled_roi_file, final_roi_file]:
                print(element)
                if os.path.exists(element):
                    print('Output file already there; deleting it:{}'.format(element))
                    os.remove(element)

            #Align the tract ROI with the preprocessed DTI
            call_parts = [
                          '@Align_Centers',
                          '-base', preproc_dti,
                          '-dset', tract_roi_file
                          ]
            print('Running @Align_centers for {}, tract {}'.format(sub, tract))
            print('preproc_dti: {}'.format(preproc_dti))
            print('tract_roi_file: {}'.format(tract_roi_file))
            print(call_parts)
            error_flag = subprocess.call(call_parts)
            if error_flag:
                print('@Align_centers failed for subject {}, tract {}!'.format(sub, tract))
                bad_runs.append([sub, tract, 'center align'])
                raise RuntimeError

            #Resample the aligned tract ROI to the tract mask
            call_parts = [
                          '3dresample',
                          '-master', preproc_dti,
                          '-inset', centered_roi_file,
                          '-prefix', resampled_roi_file
                          ]
            print('Running 3dresample for {}, tract {}'.format(sub, tract))
            error_flag = subprocess.call(call_parts)
            if error_flag:
                print('3dresample failed for subject {}, tract {}!'.format(sub, tract))
                bad_runs.append([sub, tract, 'resample'])
                raise RuntimeError

            #Mask the tract ROI by the tract mask
            call_parts = [
                          '3dcalc',
                          '-a', tract_mask_file,
                          '-b', resampled_roi_file,
                          '-prefix', final_roi_file,
                          '-exp', 'and(ispositive(a), ispositive(b))'
                          ]
            error_flag = subprocess.call(call_parts)
            if error_flag:
                print('3dcalc failed for subject {}, tract {}!'.format(sub, tract))
                bad_runs.append([sub, tract, '3dcalc'])
                raise RuntimeError
            good_runs.append([sub, tract])
        except Exception as err:
            print('\nSomething went wrong with subject {}, tract {}.\n'.format(sub, tract))
            print('{}'.format(err))
            bad_runs.append([sub, tract, 'somewhere...'])

print('-------------------------------------------')
print('Good Runs: {}'.format(good_runs))
print('Bad Runs: {}'.format(bad_runs))
print('-------------------------------------------')
