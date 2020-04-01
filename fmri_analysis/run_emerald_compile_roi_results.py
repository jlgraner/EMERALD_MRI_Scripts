

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


for cope in cope_list:
	#Put together results for big ROIs
	string_to_write = 'sub,roi,mean,stdev'
	for element in file_list:
		with open(element, 'r') as fid:
			contents = fid.read()
		#Ignore the first line, which is a header
		contents_to_keep = contents.split()[1:]
		string_to_write = string_to_write + contents_to_keep
