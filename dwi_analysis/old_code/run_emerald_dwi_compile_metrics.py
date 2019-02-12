
import os
import numpy
import math
import string

this_env = os.environ

def main():
    sub_list = [
                'EM0001',
                'EM0033',
                'EM0036',
                'EM0038',
                'EM0066',
                'EM0071',
                'EM0088',
                'EM0126',
                'EM0153',
                'EM0155',
                'EM0162',
                'EM0164',
                'EM0174',
                'EM0179',
                'EM0182',
                'EM0184',
                'EM0187',
                # 'EM0188',
                'EM0192',
                'EM0202',
                'EM0206',
                'EM0217',
                # 'EM0219',
                'EM0220',
                'EM0223',
                # 'EM0229',
                'EM0240'
                ]


    tract_list = [
                  'R_SLFII',
                  'L_SLFII',
                  'R_UNC',
                  'L_UNC'
                  ]

    sift_prefix = 'sift5K_'
    wholebrain_sift_prefix = 'sift100K_'

    base_input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/DWI')
    input_file_template = 'sub-{sub}_ses-day3_{tract}_{sift}meanFA.txt'
    wholebrain_input_file_template = 'sub-{sub}_ses-day3_wholebrain_{wbsift}meanFA.txt'

    output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/DTI_Tract_Metrics')
    subwise_output_file_template = '{tract}_sub-wise_group_FA.csv'

    fa_dict = {}

    for sub in sub_list:
        sub_input_dir = base_input_dir.format(sub=sub)
        fa_dict[sub] = {}
        fa_dict[sub]['wholebrain'] = {}
        #Get whole-brain FA metrics
        input_file = os.path.join(sub_input_dir, wholebrain_input_file_template.format(sub=sub, wbsift=wholebrain_sift_prefix))
        mean, stdev, sem = __calculate_metrics(input_file)
        fa_dict[sub]['wholebrain']['mean'] = mean
        fa_dict[sub]['wholebrain']['stdev'] = stdev
        fa_dict[sub]['wholebrain']['sem'] = sem

        for tract in tract_list:
            input_file = os.path.join(sub_input_dir, input_file_template.format(sub=sub,tract=tract,sift=sift_prefix))
            #Each entry into the main dictionary will be a sub-dictionary with
            #keys of "mean", "stdev", and "sem".
            #Read in the input file and calculate the mean and standard deviation
            mean, stdev, sem = __calculate_metrics(input_file)
            fa_dict[sub][tract] = {}
            fa_dict[sub][tract]['mean'] = mean
            fa_dict[sub][tract]['stdev'] = stdev
            fa_dict[sub][tract]['sem'] = sem
            #Put together normed mean
            fa_dict[sub][tract]['mean_norm'] = float(mean) / float(fa_dict[sub]['wholebrain']['mean'])

    #Create subject-wise output files.
    for tract in tract_list:
        #Create the output file name
        subwise_output_file = os.path.join(output_dir, subwise_output_file_template.format(tract=tract))
        #Create a header line
        file_lines = []
        file_lines.append(['subject', 'mean', 'stdev', 'sem', 'mean_normed'])
        #Create a line for each subject
        for sub in sub_list:
            sub_line = []
            sub_line.append(sub)
            sub_line.append(str(fa_dict[sub][tract]['mean']))
            sub_line.append(str(fa_dict[sub][tract]['stdev']))
            sub_line.append(str(fa_dict[sub][tract]['sem']))
            sub_line.append(str(fa_dict[sub][tract]['mean_norm']))
            file_lines.append(sub_line)
        #Write out a file for this tract containing info from every subject
        print('Writing file: {}'.format(subwise_output_file))
        with open(subwise_output_file, 'w') as fd:
            for line in file_lines:
                fd.write(string.join(line, ',')+'\n')



def __calculate_metrics(input_file):

    #Check to make sure input file is there
    if not os.path.exists(input_file):
        print('Input file cannot be found!')
        print('Missing file: {}'.format(input_file))
        raise RuntimeError('Missing file: {}'.format(input_file))

    #Read in the contents of the file
    with open(input_file, 'r') as fd:
        contents = fd.read()

    #Calculate the mean of the input
    contents_list = contents.split(' ')
    contents_array = numpy.array(contents_list)
    contents_float_array = contents_array.astype(float)

    mean_value = numpy.nanmean(contents_float_array)
    std_value = numpy.nanstd(contents_float_array)
    sem_value = std_value/math.sqrt(len(contents_float_array))

    return mean_value, std_value, sem_value



if __name__ == '__main__':
    main()
    print('Done')
