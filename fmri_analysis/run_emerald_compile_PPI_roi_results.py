

import os

#Find files to read in

#For each file, read in the contents and add them to the big list to output.

#Write output file
this_env = os.environ
input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_PPI_Analysis_Output/Participant_Output')

output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_PPI_Analysis_Output')
output_file = os.path.join(output_dir, 'Group_ROI_PPI_means_{cope}.csv')

file_list = []

cope_list = {
           'reapGTflow',
           'distGTflow'
           }

dir_contents = os.listdir(input_dir)
for element in dir_contents:
    if '_ROI_PPImeans_fsl_' in element:
        file_list.append(os.path.join(input_dir, element))

#Big ROIs
for cope in cope_list:
    #Put together results for big ROIs
    strings_to_write = ['sub,roi,mean,stdev']
    for element in file_list:
        if cope in element:
            with open(element, 'r') as fid:
                contents = fid.read()
            #Ignore the first line, which is a header
            contents_to_keep = contents.split()[1:]
            for part in contents_to_keep:
                strings_to_write.append(part)
    #Write to big ROI output file
    this_output_file = output_file.format(cope=cope)
    print('Writing output file: {}'.format(this_output_file))
    with open(this_output_file, 'w') as fid:
        for this_line in strings_to_write:
            fid.write(this_line + '\n')

