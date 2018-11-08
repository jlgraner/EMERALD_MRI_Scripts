
import os, sys
import emerald_csvconvert as ecc

base_input_dir = '[Orig Functional Dir]'
base_fsl_output_dir = '[Analysis subject condition file dir]'

biac_ses_to_run = ['12345678_12345']

biac_to_em = {
            '12345678_12345':'EM9999'
            }

for biac_ses in biac_ses_to_run:
    em_id = biac_to_em[biac_ses]

    output_dir = base_fsl_output_dir.format(em_id)

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