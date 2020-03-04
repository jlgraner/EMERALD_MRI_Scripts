
import sys
import os
import logging


this_env = os.environ

dti_qa_dir = os.path.join(this_env['MYDIR'], 'Code', 'DTI_qa')

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
                'EM0033',
                'EM0036',
                'EM0400'
                ]


for sub in subs_to_run:
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

    try:
        output_written = dqa.qa_the_dti(dti_image, mask_image, shell_index_file, sub_output_dir, overwrite)
        output_file_list.append(output_written)
    except Exception as err:
        logging.error('ERROR: Something went wrong: {}'.format(err))
        raise RuntimeError('Something went wrong: {}'.format(err))
