

import os

#Find files to read in

#For each file, read in the contents and add them to the big list to output.

#Write output file
this_env = os.environ
input_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_Analysis_Output/Participant_Output')

output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/ROI_Analysis_Output')
output_file = os.path.join(output_dir, 'Group_ROI_means_{cope}.csv')
sphere_output_file = os.path.join(output_dir, 'Group_sphereROI_means_{cope}.csv')

# output_file_template = '{sub}_ROI_means_fsl_{cope}.txt'

file_list = []
sphere_file_list = []

cope_list = {
           'reapGTflow',
           'distGTflow'
           }

dir_contents = os.listdir(input_dir)
for element in dir_contents:
    if '_ROI_means_fsl_' in element:
        file_list.append(os.path.join(input_dir, element))
    if '_sphereROI_means_fsl_' in element:
        sphere_file_list.append(os.path.join(input_dir, element))

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

#Spherical ROIs
for cope in cope_list:
    #Put together results for sphere ROIs
    strings_to_write = ['sub,roi,mean,stdev']
    for element in sphere_file_list:
        if cope in element:
            with open(element, 'r') as fid:
                contents = fid.read()
            #Ignore the first line, which is a header
            contents_to_keep = contents.split()[1:]
            for part in contents_to_keep:
                strings_to_write.append(part)
    #Write to sphere ROI output file
    this_output_file = sphere_output_file.format(cope=cope)
    print('Writing output file: {}'.format(this_output_file))
    with open(this_output_file, 'w') as fid:
        for this_line in strings_to_write:
            fid.write(this_line + '\n')



