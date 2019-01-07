

import os, sys
import logging
import json

subs_to_run = ['EM0240']
runs_to_run = ['1', '2', '3', '4']

this_env = os.environ
here = os.path.dirname(os.path.realpath(__file__))
fmri_lib_dir = os.path.join(here, 'fmri_analysis')
sys.path.append(fmri_lib_dir)

#Import local libraries
import emerald_physio_lib

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

            runs_that_ran.append([emsub, biacsub, run])
        except:

