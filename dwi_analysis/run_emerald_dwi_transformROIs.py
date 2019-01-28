

import os, shutil
import logging, time
import emerald_dwi_analysis as eda

this_env = os.environ

ses = 'day3'

sub_list = [
            'EM0001'
            # 'EM0038',
            # 'EM0184',
            # 'EM0291'
            ]

# sub_list = [
            # 'EM0001',
            # 'EM0033',
            # 'EM0036',
            # 'EM0038',
            # 'EM0066',
            # 'EM0071',
            # 'EM0088',
            # 'EM0126',
            # 'EM0153',
            # 'EM0155',
            # 'EM0162',
            # 'EM0164',
            # 'EM0174',
            # 'EM0179',
            # 'EM0182',
            # 'EM0184',
            # 'EM0187',
            # # 'EM0188',
            # 'EM0192',
            # 'EM0202',
            # 'EM0206',
            # 'EM0217',
            # 'EM0219',
            # 'EM0220',
            # 'EM0223',
            # 'EM0229',
            # 'EM0240'
            # ]

tract_list = [
              'R_SLFII',
              'L_SLFII',
              'R_Unc',
              'L_Unc'
              ]


log_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/tckgen_logs/')
if not os.path.exists(log_dir):
     print('Log directory not found, creating it: {}'.format(log_dir))
     os.makedirs(log_dir)

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/dwiprep/sub-{sub}/ses-{ses}/')

base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/DWI/')
# base_anat_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/sub-{sub}/ses-{ses}/anat/')
base_anat_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/new_fmriprep/fmriprep/sub-{sub}/anat/')

tract_mask_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/DTI_TractCreationMasks/')
# tract_mask_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/Test_area/dwi/NewMaskTest/dsi_studio_test_rois/')


good_runs = []
failed_runs = []

for sub in sub_list:
     #Set up logging
     time_stamp = str(time.localtime()[1])+str(time.localtime()[2])+str(time.localtime()[0])+str(time.localtime()[3])+str(time.localtime()[4])

     log_file = os.path.join(log_dir, 'run_emerald_dwi_tckgen_'+str(sub)+'_log_'+str(time_stamp)+'.txt')

     # if os.path.isfile(log_file):
     #    raise RuntimeError('Log file already exists!?  They should be time-stamped down to the minute!')

     logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
 
     logFormatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
     # shortFormatter = logging.Formatter('%(levelname)s:%(message)s')
     rootlogger = logging.getLogger()
 
     rootlogger.setLevel(logging.INFO)
 
     fileHandler = logging.FileHandler(log_file)
     fileHandler.setFormatter(logFormatter)
     fileHandler.setLevel(logging.INFO)
     rootlogger.addHandler(fileHandler)

     #Set up input file names
     sub_input_dir = base_input_dir.format(sub=sub, ses=ses)
     sub_output_dir = base_output_dir.format(sub=sub)
     sub_anat_dir = base_anat_dir.format(sub=sub, ses=ses)
     input_dti = os.path.join(sub_input_dir, 'sub-{}_ses-{}_dwi_d_ss_prep_ss_bc.nii.gz'.format(sub,ses))
     bvec = os.path.join(sub_input_dir, 'sub-{}_ses-{}_dwi_prep.bvec'.format(sub,ses))
     bval = os.path.join(sub_input_dir, 'sub-{}_ses-{}_dwi_prep.bval'.format(sub,ses))
     transform_file = os.path.join(sub_anat_dir, 'sub-{}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5'.format(sub,ses))
     ref_image = os.path.join(sub_input_dir, 'sub-{}_ses-{}_dwi_d_ss_prep_ss_bc_tensor_FA.nii.gz'.format(sub,ses))

     #Create output directory if it is not there
     if not os.path.exists(sub_output_dir):
          logging.info('Output directory not found!')
          logging.info('Creating it: {}'.format(sub_output_dir))
          os.makedirs(sub_output_dir)
 
     #Copy the reference FA image to the output directory, for easier visual QA
     shutil.copy2(ref_image, sub_output_dir)
     #Copy the bvec and bval files to the output directory, for use in dsi_studio
     shutil.copy2(bvec, sub_output_dir)
     shutil.copy2(bval, sub_output_dir)
     #Copy the input dti data to the output directory, for use in dsi_studio
     shutil.copy2(input_dti, sub_output_dir)

     for tract in tract_list:
          try:
               #Set up mask and sphere file names
               tract_mask = eda.find_masks(tract_mask_dir, [tract, '_mask.nii.gz'])
               if len(tract_mask) > 1:
                  logging.error('More than one mask file found for tract: {}'.format(tract))
                  logging.error('Files found: {}'.format(tract_mask))
                  raise RuntimeError('Found more than one mask file!')

               #find_masks() returns a list, even if there is only one file found
               tract_mask = tract_mask[0]
               include_roi_list = eda.find_masks(tract_mask_dir, [tract, '_include.nii.gz'])

               #Transform mask and spheres into subject space
               subspace_mask = eda.transform_roi(in_image=tract_mask, add_suffix=sub, ref=ref_image, transform=transform_file)
               if subspace_mask is None:
                  logging.error('Transforming mask to subject space failed: {}'.format(in_mask))
                  raise RuntimeError('Transforming mask to subject space failed!')
               #Move the transformed mask to the subject's directory
               shutil.move(subspace_mask, sub_output_dir)

               subspace_include_roi_list = []
               for element in include_roi_list:
                 out_name = eda.transform_roi(in_image=element, add_suffix=sub, ref=ref_image, transform=transform_file)
                 if out_name is None:
                      logging.error('Transforming sphere mask to subject space failed!')
                      raise RuntimeError('Transforming sphere mask to subject space failed!')
                 else:
                      subspace_include_roi_list.append(out_name)
                      #Move the transformed roi to the subject's directory
                      shutil.move(out_name, sub_output_dir)

               good_runs.append([sub, tract])

          except Exception as err:
               logging.error('\nSomething went wrong with subject {}, track {}.\n'.format(sub, tract))
               logging.error('{}'.format(err))
               failed_runs.append([sub, tract])


#Compile all output values.
logging.info('------------------------------------')
logging.info('Good Runs: {}'.format(good_runs))
logging.info('Failed Runs: {}'.format(failed_runs))
logging.info('------------------------------------')
logging.info('Done')
                    