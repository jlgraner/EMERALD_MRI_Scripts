
import os
import logging
import subprocess
import string


def create_b0(input_file, rpe_file, output_dir, sub, ses):
    #This function creates an image file with two volumes. The
    #first volume is a b=0 volume from the DTI data set, the second
    #volume is a b=0 volumes from a reverse-phase-encode-direction
    #data set.

    #Check for inputs
    for element in [input_file, rpe_file]:
        if not os.path.exists(element):
            logging.error('Needed image cannot be found: {}'.format(element))
            return None

    #Create output file name
    b0_image_name = 'sub-{sub}_ses-{ses}_dwi_b0s.nii.gz'.format(sub=sub, ses=ses)
    b0_image_file = os.path.join(output_dir, b0_image_name)

    #Pull out the first volume of each image and put them into a single NIFTI
    call_parts = ['3dTcat', '-prefix', b0_image_file, input_file+'[0]', rpe_file+'[0]']
    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    return b0_image_file


def create_output_name(input_name, suffix, output_dir):
    #This function adds a suffix to an input file name to generate
    #a new file name.

    input_name = os.path.split(input_name)[-1]
    # file_part, ending_part = os.path.splitext(input_name)
    file_part = input_name.split('.')[0]
    ending_part = string.join(input_name.split('.')[1:], '.')
    new_name = file_part+suffix+'.'+ending_part
    new_file = os.path.join(output_dir, new_name)

    return new_file


def denoise(input_file, output_dir):
    #Run the input data through mrtrix's dwidenoise
    #Make sure the input file exists
    if not os.path.exists(input_file):
        logging.error('Input file cannot be found: {}'.format(input_file))
        return None

    #Put together the output file name
    output_file = create_output_name(input_file, '_d', output_dir)

    #Put together the denoise call
    # denoise_call = 'dwidenoise {input} {output} -force'.format(input=input_file, output=output_file)
    call_parts = ['dwidenoise', input_file, output_file, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))
    # logging.info('Running: {}'.format(call_parts))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the name of the output file
    return output_file


def skull_strip(input_file, output_dir):
    #Run the input data through bet

    #Make sure the input file exists
    if not os.path.exists(input_file):
        logging.error('Input file cannot be found: {}'.format(input_file))
        return None

    #Put together the output file name
    output_file = create_output_name(input_file, '_ss', output_dir)

    #Put together the skull strip call
    call_parts = ['bet', input_file, output_file, '-f', '0.1', '-F']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the name of the output file
    return output_file


def preproc(input_file, output_dir, bvec_file, bval_file, b0_image_file):
    #Run the input data through dwipreproc

    #Make sure the input file exists
    for element in [input_file, bvec_file, bval_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None, None, None

    #Check for the b0 image if it should be there
    if b0_image_file is not None:
        if not os.path.exists(b0_image_file):
            logging.error('b0 image should be there but cannot be found: {}'.format(b0_image_file))
            return None, None, None

    #Put together the output file name
    output_file = create_output_name(input_file, '_prep', output_dir)
    output_bvec = create_output_name(bvec_file, '_prep', output_dir)
    output_bval = create_output_name(bval_file, '_prep', output_dir)

    #Put together the preprocessing call
    if b0_image_file is None:
        call_parts = ['dwipreproc', input_file, output_file, '-rpe_none', '-pe_dir', 'AP', '-fslgrad', bvec_file, bval_file, '-export_grad_fsl', output_bvec, output_bval, '-force']
    else:
        call_parts = ['dwipreproc', input_file, output_file, '-rpe_pair', '-se_epi', b0_image_file, '-pe_dir', 'AP', '-fslgrad', bvec_file, bval_file, '-export_grad_fsl', output_bvec, output_bval, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None, None, None

    #Return the name of the output file
    return output_file, output_bvec, output_bval


def ss_preproc(input_file, output_dir):
    #Run the input data through bet

    #Make sure the input file exists
    if not os.path.exists(input_file):
        logging.error('Input file cannot be found: {}'.format(input_file))
        return None, None

    #Put together the output file name
    output_file = create_output_name(input_file, '_ss', output_dir)

    #The output name of the mask file will be this
    output_mask_file = create_output_name(output_file, '_mask', output_dir)

    #Put together the skull strip call
    call_parts = ['bet', input_file, output_file, '-f', '0.2', '-F', '-m']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None, None

    #Return the name of the output file
    return output_file, output_mask_file


def bias_corr(input_file, input_mask, output_dir, bvec_file, bval_file):
    #Run the input through dwibiascorrect

    #Make sure the input file exists
    for element in [input_file, input_mask, bvec_file, bval_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None

    #Put together the output file name
    output_file = create_output_name(input_file, '_bc', output_dir)

    #Put together the bias correction call
    call_parts = ['dwibiascorrect', input_file, output_file, '-ants', '-mask', input_mask, '-fslgrad', bvec_file, bval_file, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the name of the output file
    return output_file



def dwimask(input_file, output_dir, bvec_file, bval_file):
    #Create a mask of the dwi data

    #Make sure the input file exists
    for element in [input_file, bvec_file, bval_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None

    #Put together the output file name
    output_file = create_output_name(input_file, '_mask', output_dir)

    #Put together the bias correction call
    call_parts = ['dwi2mask', input_file, output_file, '-fslgrad', bvec_file, bval_file, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the name of the output file
    return output_file


def make_tensor(input_file, input_mask, output_dir, bvec_file, bval_file):
    #Create tensor images

    #Make sure the input file exists
    for element in [input_file, input_mask, bvec_file, bval_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None

    #Put together the output file name
    output_file = create_output_name(input_file, '_tensor', output_dir)

    #Put together the bias correction call
    call_parts = ['dwi2tensor', '-mask', input_mask, input_file, output_file, '-fslgrad', bvec_file, bval_file, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the name of the output file
    return output_file


def make_metrics(input_file, output_dir):
    #Create FA, RD, and AD

    #Make sure the input file exists
    for element in [input_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None, None, None

    #Put together the output file name
    fa_file = create_output_name(input_file, '_FA', output_dir)
    rd_file = create_output_name(input_file, '_RD', output_dir)
    ad_file = create_output_name(input_file, '_AD', output_dir)

    #Put together the bias correction call
    call_parts = ['tensor2metric', input_file, '-fa', fa_file, '-rd', rd_file, '-ad', ad_file, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None, None, None

    #Return the name of the output file
    return fa_file, rd_file, ad_file


def make_response_txt(working_file, output_dir, working_bvec, working_bval):
    #Create response function .txt file

    #Make sure input file exists
    for element in [working_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None

    #Put together output file name
    temp_output_file = create_output_name(working_file, '_FOD_out', output_dir)
    output_file = temp_output_file.split('.nii')[0] + '.txt'
    
    #Put together the response function call
    call_parts = ['dwi2response', 'tournier', working_file, output_file, '-fslgrad', working_bvec, working_bval, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the name of the output file
    return output_file

def make_segment_response_txt(working_file, output_dir, working_bvec, working_bval):
    #Create response functions for each anatomical segmentation region
    #(GM, WM, CSF)

    #Make sure input file exists
    for element in [working_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None

    #Put together output file name
    temp_wm_output = create_output_name(working_file, '_sfwm_FOD', output_dir)
    temp_gm_output = create_output_name(working_file, '_gm_FOD', output_dir)
    temp_csf_output = create_output_name(working_file, '_csf_FOD', output_dir)

    wm_output_file = temp_wm_output.split('.nii')[0] + '.txt'
    gm_output_file = temp_gm_output.split('.nii')[0] + '.txt'
    csf_output_file = temp_csf_output.split('.nii')[0] + '.txt'

    #Put together the segmentation region response function call
    call_parts = ['dwi2response', 'dhollander', working_file, wm_output_file, gm_output_file, csf_output_file, '-fslgrad', working_bvec, working_bval, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the names of the output files
    return wm_output_file, gm_output_file, csf_output_file

def make_response_image(working_file, response_txt_file, bias_corr_mask, output_dir, working_bvec, working_bval):
    #Create FOD image

    #Make sure the input file exists
    for element in [working_file]:
        if not os.path.exists(element):
            logging.error('Input file cannot be found: {}'.format(element))
            return None

    #Put together output file name
    response_image_file = create_output_name(working_file, '_FOD', output_dir)

    #Put together response function image call
    call_parts = ['dwi2fod', 'csd', working_file, response_txt_file, response_image_file, '-mask', bias_corr_mask, '-fslgrad', working_bvec, working_bval, '-force']
    logging.info('Running: {}'.format(string.join(call_parts)))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.string.join(call_parts))
        return None

    #Return the names of the output files
    return response_image_file