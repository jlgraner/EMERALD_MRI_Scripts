
import os, sys
import logging, time
import emerald_dwi_preproc as edp

this_env = os.environ

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/User_Test_Data/UserTest_10312018_BIDS/sub-{sub}/ses-{ses}/dwi/')
base_output_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/User_Test_Data/UserTest_10312018_BIDS/dwiprep/sub-{sub}/ses-{ses}/')


sub_list = [
            'UT0100'
            ]

run_list = [
            '01',
            '02',
            '03'
            ]

session = 'usertest'

#Create log file
log_dir = os.path.join(this_env['EMDIR'], 'Data/DTI_UserTest_09182018_BIDS/dwiprep/logs/')
if not os.path.exists(log_dir):
    print('Creating log file output directory: {}'.format(log_dir))
    os.makedirs(log_dir)


good_runs = []
failed_runs = []

for subject in sub_list:
    time_stamp = str(time.localtime()[1])+str(time.localtime()[2])+str(time.localtime()[0])+str(time.localtime()[3])+str(time.localtime()[4])

    log_file = os.path.join(log_dir, 'run_emerald_dwi_preproc_'+str(subject)+'_log_'+str(time_stamp)+'.txt')

    if os.path.isfile(log_file):
        raise RuntimeError('Log file already exists!?  They should be time-stamped down to the minute!')

    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

    logFormatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    # shortFormatter = logging.Formatter('%(levelname)s:%(message)s')
    rootlogger = logging.getLogger()

    rootlogger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler(log_file)
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.INFO)
    rootlogger.addHandler(fileHandler)

    #Write some initial basic info to the log file
    logging.info('Created this log file.')
    logging.info('--------Input Parameters---------')
    logging.info('Subject ID: {}'.format(subject))
    logging.info('Input Directory: {}'.format(base_input_dir.format(sub=subject, ses=session)))
    logging.info('Output Directory: {}'.format(base_output_dir.format(sub=subject, ses=session)))
    for run in run_list:

        logging.info('---------------------------------')

        #Put together the input image data file
        input_dir = base_input_dir.format(sub=subject, ses=session)
        input_name = 'sub-{sub}_ses-{ses}_run-{run}_dwi.nii.gz'.format(sub=subject, ses=session, run=run)
        input_file = os.path.join(input_dir, input_name)

        #Put together the input bvecs and bvals files
        bvec_name = 'sub-{sub}_ses-{ses}_run-{run}_dwi.bvec'.format(sub=subject, ses=session, run=run)
        bval_name = 'sub-{sub}_ses-{ses}_run-{run}_dwi.bval'.format(sub=subject, ses=session, run=run)
        bvec_file = os.path.join(input_dir, bvec_name)
        bval_file = os.path.join(input_dir, bval_name)

        try:
            #Make sure the necessary input files exist
            for element in [input_file, bvec_file, bval_file]:
                logging.info('Looking for input file: {}'.format(element))
                if not os.path.exists(element):
                    logging.error('Input file cannot be found: {}'.format(element))
                    raise RuntimeError('Input file not found: {}'.format(element))

            #Put together the output directory
            output_dir = base_output_dir.format(sub=subject, ses=session)
            if not os.path.exists(output_dir):
                logging.info('Creating output directory: {}'.format(output_dir))
                os.makedirs(output_dir)

            #Create a variable for the current version of the data of interest
            working_file = input_file

            #Run initial denoising
            working_file = edp.denoise(input_file, output_dir)
            if working_file is None:
                logging.error('Initial denoising failed for subject {}, session {}!'.format(subject, session))
                failed_runs.append([subject, session, 'Initial denoising'])
                raise RuntimeError

            #Skull Strip the denoised data
            working_file = edp.skull_strip(working_file, output_dir)
            if working_file is None:
                logging.error('Skull Strip of denoised data failed for subject {}, session {}!'.format(subject, session))
                failed_runs.append([subject, session, 'SS Denoised'])
                raise RuntimeError

            #Preprocess the dwi data
            working_file, working_bvec, working_bval = edp.preproc(working_file, output_dir, bvec_file, bval_file)
            for element in [working_file, working_bvec, working_bval]:
                if element is None:
                    logging.error('Preprocessing of DWI data failed for subject {}, session {}!'.format(subject, session))
                    failed_runs.append([subject, session, 'Preproc'])
                    raise RuntimeError

            #Create mask of preprocessed data
            working_file, preproc_mask = edp.ss_preproc(working_file, output_dir)
            for element in [working_file, preproc_mask]:
                if element is None:
                    logging.error('Mask creation of preprocessed DWI data failed for subject {}, session {}!'.format(subject, session))
                    failed_runs.append([subject, session, 'SS_Preproc'])
                    raise RuntimeError

            #Run bias field correction on the data
            working_file = edp.bias_corr(working_file, preproc_mask, output_dir, working_bvec, working_bval)
            if working_file is None:
                logging.error('Bias field correction failed for subject {}, session {}!'.format(subject, session))
                failed_runs.append([subject, session, 'bias_cor'])
                raise RuntimeError

            #Create a mask from the bias-corrected data
            bias_cor_mask = edp.dwimask(working_file, output_dir, working_bvec, working_bval)
            if bias_cor_mask is None:
                logging.error('Bias-corrrected mask creation failed for subject {}, session {}!'.format(subject, session))
                failed_runs.append([subject, session, 'bias_mask'])
                raise RuntimeError

            #Calculate tensors
            tensor_file = edp.make_tensor(working_file, bias_cor_mask, output_dir, working_bvec, working_bval)
            if tensor_file is None:
                logging.error('Tensor creation failed for subject {}, session {}!'.format(subject, session))
                failed_runs.append([subject, session, 'tensor_creation'])
                raise RuntimeError

            #Calculate FA, RD, AD
            fa_file, rd_file, ad_file = edp.make_metrics(tensor_file, output_dir)
            for element in [fa_file, rd_file, ad_file]:
                if element is None:
                    logging.error('FA, RD, AD creation failed for subject {}, session {}!'.format(subject, session))
                    failed_runs.append([subject, session, 'FA_RD_AD'])
                    raise RuntimeError

            ########
            #Create response function
            response_txt_file = edp.make_response_txt(working_file, output_dir, working_bvec, working_bval)
            if response_txt_file is None:
                logging.error('Response function creation failed for subject {}, session {}!'.format(subject, session))
                failed_runs.append([subject, session, 'response_creation'])
                raise RuntimeError

            #Create regional (GM/WM/CSF) response functions
            response_txt_file_wm, response_txt_gm, response_txt_csf = edp.make_segment_response_txt(working_file, output_dir, working_bvec, working_bval)
            for element in [response_txt_file_wm, response_txt_gm, response_txt_csf]:
                if element is None:
                    logging.error('Segmentation region response function creation failed for subject {}, session {}!'.format(subject, session))
                    failed_runs.append([subject, session, 'seg_response_creation'])
                    raise RuntimeError

            #Create FOD image
            response_image_file = edp.make_response_image(working_file, response_txt_file, bias_cor_mask, output_dir, working_bvec, working_bval)
            for element in [response_image_file]:
                if element is None:
                    logging.error('Response function image create failed for subject {}, session {}!'.format(subject, session))
                    failed_runs.append([subject, session, 'response_image_creation'])
                    raise RuntimeError
            ########

            logging.info('Finished without errors for subject {}, session {}.'.format(subject, session))
            good_runs.append([subject, session])

        except Exception as err:
            logging.error('\nSomething went wrong with subject {}, session {}. Check log file: {}\n'.format(subject, session, log_file))
            logging.error('{}'.format(err))
            failed_runs.append([subject, session, 'somewhere'])

logging.info('DWI preproc runs that ran: {}'.format(good_runs))
logging.info('DWI preproc runs that failed: {}'.format(failed_runs))