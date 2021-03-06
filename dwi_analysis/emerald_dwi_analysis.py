
import os
import logging
import subprocess

this_code = 'emerald_dwi_analysis.py'

def find_masks(dir_to_search, search_string_list):
    #Return file paths/names in dir_to_search that contain all
    #the strings in search_string_list

    this_function = 'find_masks()'
    files_to_return = []

    #Make sure directory is there
    if not os.path.exists(dir_to_search):
      logging.error('Proposed mask directory not found: {}'.format(dir_to_search))
      logging.error('Error from: {} -- {}'.format(this_code, this_function))
      return 0

    #List files in the directory
    contents = os.listdir(dir_to_search)

    for file_name in contents:
      count = 0
      for element in search_string_list:
        if element in file_name:
          count = count + 1
      if count == len(search_string_list):
        files_to_return.append(os.path.join(dir_to_search, file_name))

    return files_to_return


def transform_roi(in_image, add_suffix, ref, transform):
    #Put an input image through antsApplyTransforms
    this_function = 'transform_roi()'
    #Create output file name
    input_path, input_name = os.path.split(in_image)
    if '.nii' not in input_name:
      logging.error('Input image expected to be a .nii file!')
      logging.error('input file name: {}'.format(input_name))
      raise RuntimeError('Input image not a NIFTI file! -- {}, {}'.format(this_code,this_function))
    if input_name[-7:] == '.nii.gz':
      input_end = '.nii.gz'
    elif input_name[-4:] == '.nii':
      input_end = '.nii'
    else:
      logging.error('Input image name does not end in .nii or .nii.gz???')
      raise RuntimeError('Input image file name should end in .nii or .nii.gz! -- {}, {}'.format(this_code,this_function))

    input_prefix = input_name.split(input_end)[0]
    output_name = '{}_{}{}'.format(input_prefix, add_suffix, input_end)
    out_image = os.path.join(input_path, output_name)

    call_parts = [
                  'antsApplyTransforms',
                  '--float',
                  '--default-value', '0',
                  '--input', in_image,
                  '--interpolation', 'NearestNeighbor',
                  '--output', out_image,
                  '--reference-image', ref,
                  '--transform', transform
                  ]

    logging.info('Applying transform to image...')
    logging.info('Input Image: {}'.format(in_image))
    logging.info('Transform: {}'.format(transform))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.format(call_parts))
        return None
    else:
        return out_image

def generate_tracks(in_dwi, in_fod, out_tck, mask, include_list, bval, bvec, track_num):
    #Generate tracktography
    call_beginning = [
                      'tckgen',
                      '-seed_image', in_dwi, in_fod, out_tck,
                      '-mask', mask
                      ]

    for element in include_list:
        call_beginning.append('-include')
        call_beginning.append(element)

    call_ending = [
                   '-select', track_num,
                   '-maxlength', '300',
                   '-fslgrad', bvec, bval,
                   '-seeds', '0',
                   '-force'
                  ]

    call_parts = call_beginning + call_ending

    logging.info('Generating tracks...')
    logging.info('in_dwi: {}'.format(in_dwi))
    logging.info('in_fod: {}'.format(in_fod))
    logging.info('out_tck: {}'.format(out_tck))
    logging.info('mask: {}'.format(mask))
    logging.info('include: {}'.format(include_list))
    logging.info('bval: {}'.format(bval))
    logging.info('bvec: {}'.format(bvec))
    logging.info('track_num: {}'.format(track_num))

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.format(call_parts))
        return None
    else:
        return out_tck


def generate_wholebrain_tracks(in_dwi, in_fod, out_tck, bval, bvec, track_num):
    #Generate whole-brain tractography
    call_parts = [
                  'tckgen',
                  '-seed_image', in_dwi, in_fod, out_tck,
                  '-select', track_num,
                  '-maxlength', '250',
                  '-fslgrad', bvec, bval,
                  '-force'
                  ]

    logging.info('Generating whole-brain tracks...')
    logging.info('in_dwi: {}'.format(in_dwi))
    logging.info('in_fod: {}'.format(in_fod))
    logging.info('out_tck: {}'.format(out_tck))
    logging.info('bval: {}'.format(bval))
    logging.info('bvec: {}'.format(bvec))
    logging.info('track_num: {}'.format(track_num))

    error_flag = subprocess.call(call_parts)
    if error_flag:
      logging.error('Process failed: {}'.format(call_parts))
      return None
    else:
      return 1


def sift_tracks(in_tck, in_fod, out_sift, sift_num):
    #Sift tracks
    call_parts = [
                  'tcksift',
                  in_tck,
                  in_fod,
                  out_sift,
                  '-term_number', sift_num,
                  '-force'
                  ]

    logging.info('Sifting tracks...')

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.format(call_parts))
        return None
    else:
        return out_sift

def sample_FA(in_tck, in_fa, out_fa):
    #Sample FA
    call_parts = [
                  'tcksample',
                  in_tck,
                  in_fa,
                  out_fa,
                  '-stat_tck', 'mean',
                  '-force'
                  ]

    logging.info('Sampling FA...')

    error_flag = subprocess.call(call_parts)
    if error_flag:
        logging.error('Process failed: {}'.format(call_parts))
        return None
    else:
        return out_fa

def align_centers(base_image, moving_image):

    current_dir = os.getcwd()

    #Create output image file name
    if moving_image[-7:] == '.nii.gz':
      input_prefix = moving_image[:-7]
      input_extension = '.nii.gz'
    elif moving_image[-4:] == '.nii':
      input_prefix = moving_image[:-4]
      input_extension = '.nii'
    else:
      logging.error('Input moving image should be .nii or .nii.gz!')
      logging.error('moving_image: {}'.format(moving_image))
      logging.error('emerald_dwi_analysis.py -- align_centers()')
      return None

    out_image = '{}_shft{}'.format(input_prefix, input_extension)

    target_dir = os.path.split(base_image)[0]
    os.chdir(target_dir)

    #Align the centers of two images
    call_parts = [
                    '@Align_Centers',
                    '-base', base_image,
                    '-dset', moving_image
                    ]
    logging.info('Aligning centers...')

    error_flag = subprocess.call(call_parts)
    os.chdir(current_dir)
    if error_flag:
        logging.error('Process failed: {}'.format(call_parts))
        return None
    else:
        return out_image