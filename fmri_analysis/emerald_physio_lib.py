
import os
import bioread
from bioread.writers import txtwriter
import pandas

#This script will read in .acq files, remove pre-scan contents,
#write out the results as .txt files.

#This script is currently very clunky and specific to EMERALD.

subs_that_failed = []
subs_that_worked = []

for biac_ses, subid in sub_list:
    for run in ['1', '2', '3', '4']:
        try:
            #Find input file
            input_file = os.path.join(base_input_dir.format(ses=biac_ses), '{s}_physio_run{r}.acq'.format(s=subid, r=run))
            txt_file = os.path.join(base_input_dir.format(ses=biac_ses), '{s}_physio_run{r}.txt'.format(s=subid, r=run))
            trim_output = os.path.join(base_input_dir.format(ses=biac_ses), '{s}_physio_run{r}_trim.txt'.format(s=subid, r=run))
            fsl_output = os.path.join(base_input_dir.format(ses=biac_ses), '{s}_physio_run{r}_fsl.txt'.format(s=subid, r=run))
            if not os.path.exists(input_file):
                print('Input file not found: {}'.format(input_file))
                raise RuntimeError
            #Write out .txt version
            data = bioread.read(input_file)
            print('Writing text file: {}'.format(txt_file))
            with open(txt_file, 'w') as fid:
                txtwriter.write_text(data,fid,[0,1,9],None)

            #Read .txt version in with pandas
            txt_data = pandas.read_csv(txt_file, sep='\t', engine='python')

            #Find the row with the beginning of the scan.
            #(Marked with 32.0 in the code channel)
            start_row = txt_data.loc[txt_data['Code (Volts)'] == 32.0]

            #Remove the rows of the dataframe before this row
            short_data = txt_data.drop(range(start_row.index[0]))

            #Calculate the length of the acquisition in seconds
            if run in ['1', '3']:
                trs = 240
            else:
                trs = 219
            acq_secs = trs * 2.0

            #Calculate the length of the acquisition in number of physio rows
            acq_rows = acq_secs * 200.0

            #Find the final row index
            last_acq_row = short_data.index[0] + acq_rows

            #Create a dataframe with only recordings during the acqusition
            #(Remove recordings after the acquisition stopped)
            trimmed_data = short_data.drop(range(int(last_acq_row),int(short_data.index[-1]+1)))

            #Write the trimmed output data
            print('Writing file: {}'.format(trim_output))
            trimmed_data.to_csv(path_or_buf=trim_output, sep='\t', index=False, header=False)

            #Create a version of the data frame replacing the code column
            #with a made-up scanner trigger column for FSL's sake.
            fsl_data = trimmed_data.drop('Code (Volts)', axis=1)
            entry_count = len(fsl_data['time (s)'])
            trig_column = [0] * entry_count
            for index in range(0,entry_count,400):
                trig_column[index] = 1.0
            fsl_data['scannertrig'] = trig_column

            #Write out the FSL-format output data
            print('Writing FSL-friendly file: {}'.format(fsl_output))
            fsl_data.to_csv(path_or_buf=fsl_output, sep='\t', index=False, header=False)

            subs_that_worked.append(subid)
        except Exception as err:
            print(str(err))
            subs_that_failed.append(subid)

print('Worked: {}'.format(subs_that_worked))
print('Failed: {}'.format(subs_that_failed))