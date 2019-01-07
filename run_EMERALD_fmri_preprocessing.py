

import os, sys
import logging
import subprocess
import string
import json
import pandas, numpy

subs_to_run = ['EM0240']
runs_to_run = ['1', '2', '3', '4']

this_env = os.environ
here = os.path.dirname(os.path.realpath(__file__))
fmri_lib_dir = os.path.join(here, 'fmri_analysis')
sys.path.append(fmri_lib_dir)
bxh2bids_dir = os.path.join(this_env['MYDIR'], 'Data', 'bxh2bids')
sys.path.append(bxh2bids_dir)
pick_confounds_dir = os.path.join(this_env['MYDIR'], 'Data', 'Graner_BIDS_tools', 'fmriprep_related')
sys.path.append(pick_confounds_dir)

#Import local libraries
import emerald_physio_lib
import bxh2bids as b2b
import fmriprep_pick_confounds as fpc

em2biac_file = os.path.join(this_env['EMDIR'], 'Scripts', 'MRI_Analysis', 'EM_to_BIAC.json')

#Read in the EM-BIAC dictionary
with open(em2biac_file) as fd:
    em_to_biac = json.loads(fd.read())

subs_that_failed = []
subs_that_worked = []

for emsub in subs_to_run:
    for run in runs_to_run:
        try:
            #--Process physiology files--
            ###TODO: Check to make sure the EM ID is in the EM_to_BIAC json
            biacsub = em_to_biac['em_to_biac'][emsub]
            physio_input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'Orig', 'Data', 'Func', biacsub, 'Scanner_physio')
            #Make sure physiology input file is there
            physio_input_file = emerald_physio_lib.find_physio_file(physio_input_dir, biacsub, emsub, run)
            if physio_input_file is None:
                runs_that_failed.append([emsub, biacsub, run, 'finding physio input file'])
                raise RuntimeError()
            #Convert physio file from acq to txt
            text_file = emerald_physio_lib.acq_to_txt(physio_input_file)
            if text_file is None:
                runs_that_failed.append([emsub, biacsub, run, 'acq to txt'])
                raise RuntimeError()
            #Trim the physio data to only include data during the actual acquisition
            trim_file, fsl_file = emerald_physio_lib.trim_physio_txt(text_file, run)
            if trim_file or fsl_file is None:
                runs_that_failed.append([emsub, biacsub, run, 'trim txt'])
                raise RuntimeError()

            #--Convert csv task files to tsv (for BIDS) and fsl format
            csv_input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'Orig', 'Data', 'Func', biacsub, 'Scanner_behav')
            fsl_output_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{}'.format(emsub), 'Func', 'Condition_files')

            #Look for task csv files
            file_search_string = 'emerald_emoregData_{}_run{}_'.format(em_id, run)
            found_file_list = ecc.search_for_files(csv_input_dir, file_search_string)

            #Make sure we only found one
            if len(found_file_list) != 1:
                logging.error('Wrong number of task .csv files found. Should be one!')
                logging.error('Instead is: {}'.format(file_found))
                logging.error('Search String: {}'.format(file_search_string))
                logging.error('Directory searched: {}'.format(csv_input_dir))
                runs_that_failed.append([emsub, biacsub, run, 'csv search'])
                raise RuntimeError()
            else:
                file_to_run = found_file_list[0]
            #Create BIDS tsv file
            logging.info('Creating BIDS .tsv files from: {}'.format(file_to_run))
            ecc.csv2bids(input_file=file_to_run)
            #Create FSL txt file
            print('Creating FSL .txt files from: {}'.format(file_to_run))
            ecc.csv2fsl(input_file=file_to_run, output_dir=fsl_output_dir)

            #--Put data into BIDS format
            hopes_dreams_file = os.path.join(this_env['EMDIR'] 'Data', 'MRI', 'Orig', 'bxh2bids_hopes_dreams.json')
            #Read in the hopes and dreams file
            with open(hopes_dreams_file) as fd:
                hopes_dreams = json.loads(fd.read())
            #Pull out some variables
            source_study_dir = hopes_dreams['source_study_dir']
            target_study_dir = hopes_dreams['target_study_dir']
            ses_info_dir = hopes_dreams['ses_info_dir']
            ses_files = hopes_dreams['ses_files']
            log_dir = hopes_dreams['log_dir']

            dataid = biacsub
            ses_info_file = os.path.join(ses_info_dir, hopes_dreams['ses_files'][dataid])
            with open(ses_info_file) as fd:
                ses_dict = json.loads(fd.read())

            try:
                b2b.multi_bxhtobids(dataid, ses_dict, source_study_dir, target_study_dir, log_dir)
            except:
                logging.error('Conversion to BIDS failed!')
                runs_that_failed.append([emsub, biacsub, run, 'bids conversion'])
                raise RuntimeError

            #--Run fmriqc
            input_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'EMERALD')
            output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'mriqc')

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
                          '--participant_label',
                          'sub-{}'.format(emsub)
                          ]

            logging.info('Calling: {}'.format(string.join(call_parts)))
            error_flag = subprocess.call(call_parts)
            if error_flag:
                logging.error('fmriqc call failed!')
                runs_that_failed.append([emsub, biacsub, run, 'fmriqc'])
                raise RuntimeError

            #--Run fmriprep
            output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'new_fmriprep')
            fs_license = '/usr/local/freesurfer/license.txt'
            call_parts = [
                     'docker',
                     'run',
                     '-it',
                     '--rm',
                     '-v',
                     '{}:/data:ro'.format(input_dir),
                     '-v',
                     '{}:/out'.format(output_dir),
                     '-v',
                     '{}:/opt/freesurfer/license.txt'.format(fs_license),
                     'poldracklab/fmriprep:latest',
                     '/data',
                     '/out',
                     'participant',
                     '--task', 'emoreg',
                     '--use-aroma',
                     '--ignore-aroma-denoising-errors',
                     '--output-space',
                     'template',
                     '--template-resampling-grid',
                     'native',
                     '--nthreads',
                     '4',
                     '--fs-no-reconall',
                     '--participant_label',
                     'sub-{}'.format(emsub)
                     ]

            logging.info('Calling: {}'.format(string.join(call_parts)))
            error_flag = subprocess.call(call_parts)
            if error_flag:
                logging.error('fmriprep call failed!')
                runs_that_failed.append([emsub, biacsub, run, 'fmriprep'])
                raise RuntimeError

            #--Create confound files for FSL
            rows_to_remove = 4
            output_suffix = '_forFSL'
            confound_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/BIDS/new_fmriprep/fmriprep/sub-{}/ses-day3/func/'.format(emsub))
            confound_name = 'sub-{}_ses-day3_task-emoreg_run-0{}_desc-confounds_regressors.tsv'.format(emsub, run)
            include_tr_motcen_regs = 1
            mot_cen_limit = 0.2

            confounds_to_include = ['csf', 'white_matter', 'dvars', 'framewise_displacement', 't_comp_cor',
                                    'a_comp_cor', 'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                                    'CSF', 'WhiteMatter', 'stdDVARS', 'FramewiseDisplacement', 'tCompCor',
                                    'aCompCor', 'X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']

            confound_file = os.path.join(confound_dir, confound_name)

            logging.info('Creating confound file from: {}'.format(confound_file))
            output_name = os.path.split(confound_file)[-1][:-4]+str(output_suffix)
            output_file = os.path.join(confound_dir, output_name+'.tsv')
            logging.info('Output file name set: {}'.format(output_file))

            if not os.path.exists(confound_file):
                logging.error('Confound file cannot be found: {}'.format(confound_file))
                runs_that_failed.append([emsub, biacsub, run, 'confound input file missing'])
                raise RuntimeError
            #Create a list of confound column names to include in the new file
            include_list = [] #This list will contain the specific names of columns to be included in the output
            data = pandas.read_csv(confound_file, sep='\t', engine='python', dtype=float)
            #Create an empty data frame to fill in
            new_data = pandas.DataFrame()
            for element in confounds_to_include:
                #Deal with labels with more than one confound column
                if element in ['t_comp_cor', 'a_comp_cor', 'cosine', 'non_steady_state_outlier',
                               'aroma_motion', 'tCompCor', 'aCompCor', 'Cosine', 'NonSteadyStateOutlier', 'AROMA']:
                    #Find column header names that contain the label category
                    match_list = fpc.match_columns(data, element)
                    print('Confound label matched with list: {}'.format(match_list))
                    #Add them all to the full list
                    include_list = include_list + match_list
                #Deal with labels that don't have multiple confound columns
                else:
                    include_list.append(element)
            #Put the columns with the included column labels into the new data frame
            new_data = fpc.add_columns(data, new_data, include_list)
            #If desired, create single-TR regressors and add them to the new data frame
            if include_tr_motcen_regs:
                mot_censor_dataframe = fpc.create_motion_censor_regs(data, mot_cen_limit, rows_to_remove)
                new_data = fpc.add_columns(mot_censor_dataframe, new_data, mot_censor_dataframe.keys())
            #If desired, remove initial entries corresponding to pre-steady-state TRs
            if rows_to_remove > 0:
                new_data = new_data.drop(range(rows_to_remove))
            #Write the new data frame out as a new confound file
            logging.info('Writing confounds output file: {}'.format(output_file))
            new_data.to_csv(path_or_buf=output_file, sep='\t', index=False)

            runs_that_ran.append([emsub, biacsub, run])
        except:
            logging.error('Top-level exception caught for subject {}, run {}.'.format(emsub, run))

logging.info('--------------------------------------------')
logging.info('Runs that ran: {}'.format(runs_that_ran))
logging.info('Runs that failed: {}'.format(runs_that_failed))
logging.info('--------------------------------------------')

