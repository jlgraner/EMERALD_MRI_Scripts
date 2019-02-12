

import os
import logging, time
import emerald_dwi_analysis as eda

this_env = os.environ

sub_list = [
            'UT0100'
            ]

tract_list = [
              'R_SLFII',
              'L_SLFII',
              'R_UNC',
              'L_UNC'
              ]

track_num = '20K'
sift_num = '5K'


log_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/tckgen_logs/')
if not os.path.exists(log_dir):
     print('Log directory not found, creating it: {}'.format(log_dir))
     os.makedirs(log_dir)

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/User_Test_Data/UserTest_10312018_BIDS/dwi_preproc_test/')
base_output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/User_Test_Data/UserTest_10312018_BIDS/dwi_preproc_test/')
base_anat_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/User_Test_Data/fmriprep/sub-{sub}/anat/')

tract_mask_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/DTI_TractCreationMasks/')

#Templates for input file names
dti_in_temp = 'dwi_dn_ss_prepnorpe_ss_bc_mask.nii.gz'
fod_in_temp = 'dwi_dn_ss_prepnorpe_ss_bc_FOD.nii.gz'
bvec_temp = 'fsl_prepnorpe.bvec'
bval_temp = 'fsl_prepnorpe.bval'

#Standard space tract mask and inclusion spheres
tract_mask_temp = '{tract}_mask.nii.gz'
tract_sphere_temp = '{tract}_spheres.nii.gz'

#Subject-space tract mask and inclusion spheres
sub_tract_mask_temp = '{tract}_mask_sub-{sub}.nii.gz'
sub_tract_spheres_temp = '{tract}_spheres_sub-{sub}.nii.gz'

#Previously generated FA; used as reference image for Ants transforms
# fa_temp = 'sub-{sub}_ses-{ses}_run-{run}_dwi_d_ss_prep_ss_bc_tensor_FA.nii.gz'
transform_temp = 'sub-{sub}_T1w_space-MNI152NLin2009cAsym_target-T1w_warp.h5'

fa_temp = 'dwi_dn_ss_prepnorpe_ss_bc_tensor_FA.nii.gz'

tckgen_out_temp = 'sub-{sub}_{tract}_norpe.tck'

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
     sub_input_dir = base_input_dir
     sub_output_dir = base_output_dir
     # sub_anat_dir = base_anat_dir.format(sub=sub, ses=ses)
     sub_anat_dir = base_anat_dir.format(sub=sub)
     input_dti = os.path.join(sub_input_dir, dti_in_temp)
     input_fod = os.path.join(sub_input_dir, fod_in_temp)
     bvec = os.path.join(sub_input_dir, bvec_temp)
     bval = os.path.join(sub_input_dir, bval_temp)
     transform_file = os.path.join(sub_anat_dir, transform_temp.format(sub=sub))
     ref_image = os.path.join(sub_input_dir, fa_temp)

     #Create output directory if it is not there
     if not os.path.exists(sub_output_dir):
          logging.info('Output directory not found!')
          logging.info('Creating it: {}'.format(sub_output_dir))
          os.makedirs(sub_output_dir)
 
     for tract in tract_list:
          try:
               #Set up mask and sphere file names
               tract_mask = os.path.join(tract_mask_dir, tract_mask_temp.format(tract=tract))
               tract_spheres = os.path.join(tract_mask_dir, tract_sphere_temp.format(tract=tract))

               #Set up subject-space mask and sphere file names
               sub_tract_mask = os.path.join(sub_output_dir, sub_tract_mask_temp.format(tract=tract, sub=sub))
               sub_sphere_mask = os.path.join(sub_output_dir, sub_tract_spheres_temp.format(tract=tract, sub=sub))

               tckgen_out = os.path.join(sub_output_dir, tckgen_out_temp.format(sub=sub, tract=tract))

               #Transform mask and spheres into subject space
               if not os.path.exists(sub_tract_mask):
                 okay = eda.transform_roi(in_image=tract_mask, out_image=sub_tract_mask, ref=ref_image, transform=transform_file)
                 if okay is None:
                      logging.error('Transforming tract mask to subject space failed!')
                      raise RuntimeError('Transforming tract mask to subject space failed!')
               else:
                 logging.info('Subject tract mask already exists: {}'.format(sub_tract_mask))

               if not os.path.exists(sub_sphere_mask):
                 okay = eda.transform_roi(in_image=tract_spheres, out_image=sub_sphere_mask, ref=ref_image, transform=transform_file)
                 if okay is None:
                      logging.error('Transforming sphere mask to subject space failed!')
                      raise RuntimeError('Transforming sphere mask to subject space failed!')
               else:
                logging.info('Subject sphere mask already exists: {}'.format(sub_sphere_mask))

               #Run tckgen to generate tracks
               okay = eda.generate_tracks(in_dwi=input_dti, in_fod=input_fod, out_tck=tckgen_out, mask=sub_tract_mask, include=sub_sphere_mask, bval=bval, bvec=bvec, track_num=track_num)
               if okay is None:
                    logging.error('Tract generation failed!')
                    raise RuntimeError('Tract generation failed!')

               #Sift tracks
               out_sift = '{}_sift{}.tck'.format(tckgen_out.split('.tck')[0], sift_num)
               okay = eda.sift_tracks(in_tck=tckgen_out, in_fod=input_fod, out_sift=out_sift, sift_num=sift_num)
               if okay is None:
                    logging.error('Tract sift failed!')
                    raise RuntimeError('Tract sift failed!')

               #Produce output metrics
               out_sample = '{}_meanFA.txt'.format(out_sift.split('.tck')[0])
               okay = eda.sample_FA(in_tck=out_sift, in_fa=ref_image, out_fa=out_sample)
               if okay is None:
                    logging.error('FA sampling failed!')
                    raise RuntimeError('FA sampling failed!')

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
                    