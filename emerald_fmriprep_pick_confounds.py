
import os
import pandas as pd
import numpy as np


def read_confound_file(input_file):
    ##############################
    # PURPOSE: Make sure a file is there, then read it in as a pandas Data Frame
    # INPUTS:
    #          input_file: a string containing the full path and file name of
    #                      the input confound file to read
    # RETURN:
    #          data: a pandas data frame containing the contents of the input_file
    ###############################
    this_code = 'fmriprep_pick_confounds.read_confound_file()'

    if not os.path.exists(input_file):
        raise RuntimeError('Input file cannot be found {} -- {}'.format(input_file, this_code))
    #Read in the confound file as a pandas dataframe
    with open(input_file, 'r') as fid:
        data = pd.read_csv(input_file, sep='\t', engine='python')
    return data

def add_columns(source_dataframe, target_dataframe, column_list):
    ##############################
    # PURPOSE: Add columns from one data frame to another data frame
    # INPUTS:
    #          source_dataframe: a pandas data frame containing the columns
    #                            you want to copy into the other one.
    #          target_dataframe: a pandas data frame to which you want to add
    #                            data columns
    #          column_list: list of strings containing the names of columns to
    #                       be copied from the source into the target
    # RETURN:
    #          target_dataframe
    ###############################
    this_code = 'fmriprep_pick_confounds.add_columns()'

    for element in column_list:
        if element not in source_dataframe.keys():
            raise RuntimeError('Column name not found in source dataframe header: {} -- {}'.format(element, this_code))
        else:
            target_dataframe[element] = source_dataframe[element]
    return target_dataframe

def exclude_columns(dataframe, column_list):
    ##############################
    # PURPOSE: Remove specific data columns from a data frame
    # INPUTS:
    #          dataframe: a pandas data frame containing the columns
    #                     you want to remove.
    #          column_list: list of strings containing the names of columns to
    #                       be removed
    # RETURN:
    #          new_data: version of dataframe with the desired columns removed
    ###############################
    this_code = 'fmriprep_pick_confounds.exclude_columns()'

    new_data = dataframe
    for element in column_list:
        if element not in dataframe.keys():
            raise RuntimeError('Column name not found in header: {} -- {}'.format(element, this_code))
        else:
            new_data.drop(element, axis=1)
    return new_data

def match_columns(dataframe, column_label):
    ##############################
    # PURPOSE: Create a list of data column names that contain the input string
    # INPUTS:
    #          dataframe: a pandas data frame from which you want to get data
    #                     column names that match the passed label.
    #          column_label: keep all data columns containing this string in
    #                        their names
    # RETURN:
    #          match_list: a list of data frame column names as strings
    ###############################
    this_code = 'fmriprep_pick_confounds.match_columns()'

    name_list = dataframe.keys()
    match_list = []
    for element in name_list:
        if column_label in element:
            match_list.append(element)
    return match_list

def create_motion_censor_regs(dataframe, mot_limit, rows_to_remove):
    ##############################
    # PURPOSE: Create regressors to censor out specific TRs in a GLM. Each of these regressors
    #          will have a value of 1 for the TR it censors and a value of 0 for all
    #          other time points. Selection of TRs to censor is based on having a
    #          Framewise Displacement value greater than 0.20mm (the threshold used
    #          by fmriprep).
    # INPUTS:
    #          dataframe: a pandas data frame from which you want to get the displacement
    #                     data and to which you want to add the censor regressors.
    #          mot_limit: the framewise displcement upper threshold (in mm) for determining whether
    #                     to censor a TR.
    #          rows_to_remove: the number of rows (TRs) the script is set to remove once the
    #                          final confound file has been created. If a TR that would be
    #                          censored falls into this range, this function will not include
    #                          a censor regressor for it (as the resulting column in the output
    #                          file would just be a list of 0s).
    # RETURN:
    #          mot_censor_dataframe: a pandas dataframe containing the motion censor regressors
    ###############################
    this_code = 'fmriprep_pick_confounds.create_motion_censor_regs()'

    # if 'FramewiseDisplacement' not in dataframe.keys():
    if 'framewise_displacement' not in dataframe.keys():
        raise RuntimeError('Passed data frame does not have a framewise_displacement column! -- {}'.format(this_code))

    boolean_series = dataframe['framewise_displacement'] > mot_limit
    tr_list = dataframe['framewise_displacement'][boolean_series].keys()

    mot_censor_dataframe = pd.DataFrame()

    for element in tr_list:
        if element >= rows_to_remove:
            #Create a column of all 0s
            zero_list = np.zeros(shape=(len(dataframe),1))
            #Change the element associated with this TR to 1.
            zero_list[element] = 1
            #Change the numpy array into a pandas dataframe.
            zero_dataframe = pd.DataFrame(zero_list, columns=['mot_cen{}'.format(element+1)])
            #Add the column to the dataframe to return.
            mot_censor_dataframe['mot_cen{}'.format(element+1)] = zero_dataframe['mot_cen{}'.format(element+1)]

    return mot_censor_dataframe