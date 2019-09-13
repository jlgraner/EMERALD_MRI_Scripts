

########################################################################
#This script contains some useful wrappers to some basic preprocessing
#functions.
#
#
#

import os
import subprocess


def __add_prefix(input_file, prefix):
    #This function appends a string to the existing prefix of an image file.
    #It assumes the image file is either .nii or .nii.gz.
    input_beginning, input_end = input_file.split('.nii')
    output_file = input_beginning+str(prefix)+'.nii'+input_end
    return output_file


def remove_trs(input_image, output_image=None, cut_trs=4, overwrite=0):
    #This function uses AFNI's 3dTcat to remove a number of initial TRs from
    #a 4D image.
    print('----Starting: emerald_preproc_lib.remove_trs()----')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            print('input_image must contain a full path to the image file!')
            raise RuntimeError()

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            print('input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError()

        #Put together the output file
        if output_image is None:
            print('No output_image passed, will append "_short" to the input_image name!')
            output_file = __add_prefix(input_file, '_short')
            output_image = os.path.join(input_path, output_file)

        #Check to see if passed output image is already there
        if os.path.exists(output_image):
            print('output_image already exists!')
            if overwrite:
                print('Overwrite set to 1, deleting...')
                os.remove(output_image)
            else:
                print('Overwrite not set, exitting...')
                return None

        #Put together call to 3dTcat
        ct_call = [
                   '3dTcat',
                   '-prefix',
                   output_image,
                   input_image+"'[{}..$]'".format(cut_trs)
                  ]

        print('Removing TRs...')
        process = subprocess.Popen(ct_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            print('Something went wrong with 3dTcat call!')
            print(err)
            raise RuntimeError()

        if not os.path.exists(output_image):
            print('output_image should be there, but is not: {}'.format(output_image))
            return None
    except:
        print('ERROR in removing TRs!')
        return None

    print('TR removal successful.')
    return output_image


def tempfilt(input_image, overwrite=0):
    #This function applies temporal filtering to a passed image.
    #It uses settings that mimic the defaults used by the FEAT GUI

    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            print('input_image must contain a full path to the image file!')
            raise RuntimeError()

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            print('input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError()

        #Create the temporal mean filename
        temp_tmean_filename = __add_prefix(input_file, '_tmean')
        temp_tmean_output = os.path.join(input_path, temp_tmean_filename)
        #If the temporal mean file already exists, delete it
        if os.path.exists(temp_tmean_output):
            print('Temporal mean file exists: {}'.format(temp_tmean_output))
            print('Deleting it!!!')
            os.remove(temp_tmean_output)

        #Create the call to fslmaths that will calculate the temporal mean
        call_parts = [
                      'fslmaths',
                      input_image,
                      '-Tmean',
                      temp_tmean_output
                      ]
        #Carry out temporal mean creation
        print('...creating temporal mean...')
        process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            print('Something went wrong creating mean functional image!')
            print(err)
            raise RuntimeError()

        #Create the temporal-filtered image filename
        temp_filt_filename = __add_prefix(input_file, '_tempfilt')
        temp_filt_output = os.path.join(input_path, temp_filt_filename)
        #If the filtered data already exists, delete it
        if os.path.exists(temp_filt_output):
            print('Filtered file exists: {}'.format(temp_filt_output))
            if overwrite:
                print('Overwrite set, deleting existing file...')
                os.remove(temp_filt_output)
            else:
                print('Overwrite not set, exitting!')
                return None

        #Create call to fslmaths that will run the temporal filtering
        call_parts = [
                      'fslmaths',
                      input_image,
                      '-bptf', '25', '-1',
                      '-add', temp_tmean_output,
                      temp_filt_output
                      ]
        #Carry out temporal filtering
        print('...applying temporal filter...')
        process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            print('Something went wrong creating mean functional image!')
            print(err)
            raise RuntimeError()
        #Delete the mean image
        print('...deleting temporal mean...')
        os.remove(temp_tmean_output)
    except:
        print('ERROR in temporal filtering!')
        return None

    print('Temporal filtering successful!')
    return temp_filt_output


def apply_mask(input_image, mask_image, overwrite=0):
    #This function takes a binary mask image and applies it to another image
    #using AFNI's 3dCalc.

    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            print('input_image must contain a full path to the image file!')
            raise RuntimeError()

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            print('input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError()

        #Check the mask file for a path
        mask_path, mask_file = os.path.split(mask_image)
        if mask_path is '':
            print('mask_image must contain a full path to the mask file!')
            raise RuntimeError()

        #Check that the mask file is either .nii or .nii.gz
        if len(mask_file.split('.nii')) == 1:
            print('mask_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError()

        #Create the masked file name
        mask_out_file = __append_prefix(input_file, '_brain')
        mask_out_image = os.path.join(input_path, mask_out_file)
        #Check to see if output masked image is already there
        if os.path.exists(mask_out_image):
            print('mask_out_image already exists!')
            if overwrite:
                print('Overwrite set to 1, deleting...')
                os.remove(mask_out_image_image)
            else:
                print('Overwrite not set, exitting...')
                return None

        #Create call to mask the image
        call_parts = [
                      '3dcalc',
                      '-a', input_image,
                      '-b', mask_image,
                      '-float',
                      '-prefix', mask_out_image,
                      '-exp "a*b"'
                     ]
        #Carry out masking
        print('...applying mask...')
        process = subprocess.Popen(call_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            print('Something went wrong masking image!')
            print(err)
            raise RuntimeError()
    except:
        print('ERROR applying mask!')
        return None

    print('Masking successful.')
    return mask_out_image