
import os, shutil

#AUTHOR:
#John Graner, Ph.D., 2018
#LaBar Lab, Center for Cognitive Neuroscience
#Duke University, Durham, NC


#This file contains a number of functions that are used in the multiple
#levels of FSL analysis.

def read_replace_copy_design(input_file, old_list, new_list, output_file):
    #This function reads in a .fsf file, replaces instances of strings in
    #old_list with those in new_list, and then writes the resulting string
    #to an output_file.

    print('--Starting emerald_fsl_tools.read_replace_copy_design()--')

    #Make sure input file exists
    if not os.path.exists(input_file):
        msg = 'Passed input_file does not exist: {}'.format(input_file)
        raise RuntimeError(msg)

    #Make sure the number of entries in old_list is the same as the number
    #in new_list.
    if len(old_list) != len(new_list):
        msg = 'Number of elements in old_list ({}) not equal to number in new_list ({}).'.format(len(old_list), len(new_list))
        raise RuntimeError(msg)

    #Make sure the output location can be written to.
    output_dir = os.path.split(output_file)[0]
    if not os.path.exists(output_dir):
        msg = 'Output location does not seem to be there: {}'.format(output_dir)
        raise RuntimeError(msg)

    #Read in the input_file
    print('Reading input file: {}'.format(input_file))
    fd = open(input_file, 'r')
    contents_string = fd.read()
    fd.close()

    #Replace all instances of old strings with new ones
    print('Replacing place-hold values in template string...')
    for pair in zip(old_list, new_list):
        contents_string = contents_string.replace(pair[0], pair[1])

    #Write the new string to the output file
    print('Writing new file: {}'.format(output_file))
    new_fd = open(output_file, 'w')
    new_fd.write(contents_string)
    new_fd.close()

    print('--Finished emerald_fsl_tools.read_replace_copy_design()--')


def create_fake_reg(feat_dir):
    #This function creates the /reg directory inside a run's .feat directory and copies
    #things into it that will trick FSL into thinking registration has
    #been performed for that directory (for EMERALD we're using fmriprep to do the
    #registration, so we don't want FSL re-doing it). This is only necessary because
    #of the inflexibility of FSL.

    print('-----Starting create_fake_reg()-----')

    #Make sure passed directory is there
    if not os.path.exists(feat_dir):
        msg = 'Passed .feat directory cannot be found: {}'.format(feat_dir)
        raise RuntimeError(msg)

    #Create reg dir if it's not there
    reg_dir = os.path.join(feat_dir, 'reg')
    if not os.path.exists(reg_dir):
        print('Creating reg dir: {}'.format(reg_dir))
        os.mkdir(reg_dir)

    #Copy identity matrix into examplefunc2standard.mat
    #This prevents the data from being moved from the space it's already in
    #cp $FSLDIR/etc/flirtsch/ident.mat reg/example_func2standard.mat
    fsl_dir = os.environ['FSLDIR']
    destination = os.path.join(reg_dir, 'example_func2standard.mat')
    ident_mat_file = os.path.join(fsl_dir, 'etc', 'flirtsch', 'ident.mat')
    if not os.path.exists(ident_mat_file):
        msg = 'FSL identity matrix file cannot be found: {}'.format(ident_mat_file)
        raise RuntimeError(msg)

    print('Copying identity matrix into reg dir...')
    shutil.copy2(ident_mat_file, destination)

    #Copy the mean_func.nii.gz into standard.nii.gz
    #This prevents the data from being interpolated again
    #cp mean_func.nii.gz reg/standard.nii.gz
    mean_image_file = os.path.join(feat_dir, 'mean_func.nii.gz')
    destination = os.path.join(reg_dir, 'standard.nii.gz')

    print('Copying mean_func.nii.gz into standard.nii.gz...')
    shutil.copy2(mean_image_file, destination)

    print('-----Finished create_fake_reg()-----')