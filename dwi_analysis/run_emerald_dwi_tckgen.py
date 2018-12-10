

import os
import logging, time
import emerald_dwi_analysis as eda

this_env = os.environ

ses = 'day3'

sub_list = [
            'EM0001'
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
              'R_UNC',
              'L_UNC'
              ]

# track_num = '20K'
track_num = '2'
# sift_num = '5K'
sift_num = '1'


log_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/tckgen_logs/')
if not os.path.exists(log_dir):
     print('Log directory not found, creating it: {}'.format(log_dir))
     os.makedirs(log_dir)

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/dwiprep/sub-{sub}/ses-{ses}/')
# base_output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/DWI/')
base_output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/Test_area/dwi/NewMaskTest/sub-{sub}/DWI/')
# base_anat_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/fmriprep/sub-{sub}/ses-{ses}/anat/')
base_anat_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/new_fmriprep/fmriprep/sub-{sub}/anat/')

tract_mask_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/DTI_TractCreationMasks/')

#Templates for input file names
dti_in_temp = 'sub-{sub}_ses-{ses}_dwi_d_ss_prep_ss_bc_mask.nii.gz'
fod_in_temp = 'sub-{sub}_ses-{ses}_dwi_d_ss_prep_ss_bc_FOD.nii.gz'
bvec_temp = 'sub-{sub}_ses-{ses}_dwi_prep.bvec'
bval_temp = 'sub-{sub}_ses-{ses}_dwi_prep.bval'

#Standard space tract mask and inclusion spheres (input to transform function)
tract_mask_temp = os.path.join(tract_mask_dir, '{tract}_mask.nii.gz')
tract_sphere1_temp = os.path.join(tract_mask_dir, '{tract}_sphere1.nii.gz')
tract_sphere2_temp = os.path.join(tract_mask_dir, '{tract}_sphere2.nii.gz')
tract_sphere3_temp = os.path.join(tract_mask_dir, '{tract}_sphere3.nii.gz')
mask_list=[tract_mask_temp, tract_sphere1_temp, tract_sphere2_temp, tract_sphere3_temp]

#Subject-space tract mask and inclusion spheres (output of transform function)
sub_tract_mask_temp = os.path.join(base_output_dir, '{tract}_mask_sub-{sub}.nii.gz')
sub_tract_sphere1_temp = os.path.join(base_output_dir, '{tract}_sphere1_sub-{sub}.nii.gz')
sub_tract_sphere2_temp = os.path.join(base_output_dir, '{tract}_sphere2_sub-{sub}.nii.gz')
sub_tract_sphere3_temp = os.path.join(base_output_dir, '{tract}_sphere3_sub-{sub}.nii.gz')
sub_mask_list=[sub_tract_mask_temp, sub_tract_sphere1_temp, sub_tract_sphere2_temp, sub_tract_sphere3_temp]

#Previously generated FA; used as reference image for Ants transforms
fa_temp = 'sub-{sub}_ses-{ses}_dwi_d_ss_prep_ss_bc_tensor_FA.nii.gz'
# transform_temp = 'sub-{sub}_ses-{ses}_T1w_space-MNI152NLin2009cAsym_target-T1w_warp.h5'
transform_temp = 'sub-{sub}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5'

tckgen_out_temp = 'sub-{sub}_ses-{ses}_{tract}.tck'

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
     input_dti = os.path.join(sub_input_dir, dti_in_temp.format(sub=sub,ses=ses))
     input_fod = os.path.join(sub_input_dir, fod_in_temp.format(sub=sub,ses=ses))
     bvec = os.path.join(sub_input_dir, bvec_temp.format(sub=sub,ses=ses))
     bval = os.path.join(sub_input_dir, bval_temp.format(sub=sub,ses=ses))
     transform_file = os.path.join(sub_anat_dir, transform_temp.format(sub=sub, ses=ses))
     ref_image = os.path.join(sub_input_dir, fa_temp.format(sub=sub,ses=ses))

     #Create output directory if it is not there
     if not os.path.exists(sub_output_dir):
          logging.info('Output directory not found!')
          logging.info('Creating it: {}'.format(sub_output_dir))
          os.makedirs(sub_output_dir)
 
     for tract in tract_list:
          try:
               #Set up mask and sphere file names
               # tract_mask = os.path.join(tract_mask_dir, tract_mask_temp.format(tract=tract))
               # tract_spheres = os.path.join(tract_mask_dir, tract_sphere_temp.format(tract=tract))
               mask_list=[tract_mask_temp.format(tract=tract), tract_sphere1_temp.format(tract=tract), tract_sphere2_temp.format(tract=tract), tract_sphere3_temp.format(tract=tract)]

               #Set up subject-space mask and sphere file names
               # sub_tract_mask = os.path.join(sub_output_dir, sub_tract_mask_temp.format(tract=tract, sub=sub))
               # sub_sphere_mask = os.path.join(sub_output_dir, sub_tract_spheres_temp.format(tract=tract, sub=sub))
               sub_mask_list=[sub_tract_mask_temp.format(tract=tract,sub=sub), sub_tract_sphere1_temp.format(tract=tract,sub=sub), sub_tract_sphere2_temp.format(tract=tract,sub=sub), sub_tract_sphere3_temp.format(tract=tract,sub=sub)]

               tckgen_out = os.path.join(sub_output_dir, tckgen_out_temp.format(sub=sub, ses=ses, tract=tract))

               #Transform mask and spheres into subject space
               for in_mask,out_mask in zip(mask_list,sub_mask_list):
                   okay = eda.transform_roi(in_image=in_mask, out_image=out_mask, ref=ref_image, transform=transform_file)
                   if okay is None:
                        logging.error('Transforming mask to subject space failed: {}'.format(in_mask))
                        raise RuntimeError('Transforming mask to subject space failed!')

               # okay = eda.transform_roi(in_image=tract_spheres, out_image=sub_sphere_mask, ref=ref_image, transform=transform_file)
               # if okay is None:
               #      logging.error('Transforming sphere mask to subject space failed!')
               #      raise RuntimeError('Transforming sphere mask to subject space failed!')

               #Run tckgen to generate tracks
               okay = eda.generate_tracks(in_dwi=input_dti, in_fod=input_fod, out_tck=tckgen_out, mask=sub_mask_list[0], include_list=sub_mask_list[1:], bval=bval, bvec=bvec, track_num=track_num)
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
                    