
import sys
import os
import logging


this_env = os.environ

dti_qa_dir = os.path.join(this_env['MYDIR'], 'Code', 'GitRepos', 'DTI_qa')

sys.path.append(dti_qa_dir)
import dti_qa_lib as dqa

#Set basic logger
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

#Set inputs
dti_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'EMERALD', 'sub-{sub}', 'ses-day3', 'dwi')
dwiprep_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'dwiprep', 'sub-{sub}', 'ses-day3')
post_shell_index_file = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'dwiqa', 'PostUpdate_dwi_shell_index.txt')
pre_shell_index_file = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'dwiqa', 'PreUpdate_dwi_shell_index.txt')
output_dir = os.path.join(this_env['EMDIR'], 'Data', 'MRI', 'BIDS', 'dwiqa')

overwrite = 1


subs_to_run = [
                'EM0001',
                'EM0038',
                'EM0066',
                'EM0036',
                'EM0033',
                'EM0071',
                'EM0088',
                'EM0155',
                'EM0126',
                'EM0162',
                'EM0179',
                'EM0182',
                'EM0187',
                'EM0174',
                'EM0164',
                'EM0192',
                'EM0184',
                'EM0202',
                'EM0206',
                'EM0217',
                'EM0219',
                'EM0153',
                'EM0229',
                'EM0220',
                'EM0223',
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
                'EM0946'
                ]

# subs_to_run = ['EM0001', 'EM0033', 'EM0400']

good_runs = []
bad_runs = []

for sub in subs_to_run:
    try:
        sub_dti_dir = dti_dir.format(sub=sub)
        sub_dwiprep_dir = dwiprep_dir.format(sub=sub)
        sub_output_dir = os.path.join(output_dir, 'sub-{}'.format(sub))
        dti_image = os.path.join(sub_dti_dir, 'sub-{}_ses-day3_dwi.nii.gz'.format(sub))
        mask_image = os.path.join(sub_dwiprep_dir, 'sub-{}_ses-day3_dwi_d_ss_mask.nii.gz'.format(sub))

        #Select the correct shell index file
        if int(sub[-4:]) < 290:
            shell_index_file = pre_shell_index_file
        else:
            shell_index_file = post_shell_index_file

        #Try running the QA
        logging.info('Running Participant: {}'.format(sub))
        logging.info('----------Input Variables----------')
        logging.info('dti_image: {}'.format(dti_image))
        logging.info('mask_image: {}'.format(mask_image))
        logging.info('shell_index_file: {}'.format(shell_index_file))
        logging.info('output_dir: {}'.format(sub_output_dir))
        logging.info('overwrite: {}'.format(overwrite))
        logging.info('-----------------------------------')

        output_written = dqa.qa_the_dti(sub, dti_image, mask_image, shell_index_file, sub_output_dir, overwrite)
        good_runs.append(sub)
    except Exception as err:
        bad_runs.append(sub)
        logging.error('ERROR: Something went wrong with sub {}: {}'.format(sub,err))
        raise RuntimeError('Something went wrong: {}'.format(err))

logging.info('Finished Generating QA Metrics')
logging.info('------------------------------')
logging.info('Good Runs: {}'.format(good_runs))
logging.info('Bad Runs: {}'.format(bad_runs))
logging.info('------------------------------')