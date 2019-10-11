
import os, sys
import json
import emerald_csvconvert as ecc

this_env = os.environ

base_input_dir = os.path.join(this_env['EMDIR'], 'Data/MRI/Orig/Data/Func/')
base_fsl_output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{em_id}/Func/Condition_files')

em_to_biac_file = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/EM_to_BIAC.json')
with open(em_to_biac_file) as fd:
    em_to_biac = json.loads(fd.read())

em_to_run = [
            'EM0643'
            ]

for em_id in em_to_run:
    biac_ses = em_to_biac['em_to_biac'][em_id]

    output_dir = base_fsl_output_dir.format(em_id=em_id)

    for run_num in ['run1', 'run2', 'run3', 'run4']:
        file_search_string = 'emerald_emoregData_{}_{}_'.format(em_id, run_num)
        dir_to_search = os.path.join(base_input_dir, biac_ses, 'Scanner_behav')
        contents = os.listdir(dir_to_search)
        file_found = 0
        for element in contents:
            if (file_search_string in element) and (element[-4:] == '.csv'):
                file_to_run = os.path.join(dir_to_search, element)
                file_found = file_found + 1
        #Make sure we only found one
        if file_found != 1:
            print('Wrong number of .csv files found. Should be one!')
            print('Instead is: {}'.format(file_found))
            print('Search String: {}'.format(file_search_string))
            print('Directory: {}'.format(dir_to_search))
            sys.exit()

        print('Creating BIDS .tsv files and FSL .txt files for: {}'.format(file_to_run))
        ecc.csv2bids(input_file=file_to_run)
        print('Creating FSL .txt files for: {}'.format(file_to_run))
        ecc.csv2fsl(input_file=file_to_run, output_dir=output_dir)

print('Done!')