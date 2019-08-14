

import os, sys
import numpy

this_env = os.environ

def main():
    # sub_list = [
    #           'EM0001',
    #           'EM0033',
    #           'EM0036',
    #           'EM0038',
    #           'EM0066',
    #           'EM0071',
    #           'EM0088',
    #           'EM0126',
    #           'EM0153',
    #           'EM0155',
    #           'EM0162',
    #           'EM0164',
    #           'EM0174',
    #           'EM0179',
    #           'EM0184',
    #           'EM0187',
    #           'EM0192',
    #           'EM0202',
    #           'EM0206',
    #           'EM0217',
    #           'EM0219',
    #           'EM0220',
    #           'EM0223',
    #           'EM0229',
    #           'EM0240'
    #               ]
    sub_list = [
                'EM0291',
                'EM0304',
                'EM0381',
                'EM0360',
                'EM0400',
                'EM0500',
                'EM0519'
                ]

    run_list = ['1','2','3','4']

    output_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/Higher_reapPPIfeat_postup_08122019')
    dir_output_name = 'SecondLevelFeatDirs_to_copy.txt'
    ev_output_name = 'SecondLevelEVMatrix_to_copy.txt'
    contrast_output_name = 'SecondLevelSubjectContrastMatrix_to_copy.txt'

    dir_output_file = os.path.join(output_dir, dir_output_name)
    ev_output_file = os.path.join(output_dir, ev_output_name)
    contrast_output_file = os.path.join(output_dir, contrast_output_name)

    print('Writing first-level directory list file...')
    write_firstleveldirs(sub_list, run_list, dir_output_file)

    print('Writing EV matrix for 2nd-Level analysis...')
    write_evmatrix(sub_list, run_list, ev_output_file)

    print('Writing Contrast matrix for 2nd-Level analysis...')
    write_subjectcontrastmatrix(sub_list, contrast_output_file)



def write_subjectcontrastmatrix(sub_list, output_file):

    sub_num = len(sub_list)
    contrast_matrix = numpy.identity(sub_num)

    #Write the contrast matrix out to a file
    if os.path.exists(output_file):
        print('Subject contrast matrix output file already exists!')
        print('Subject contrast matrix output file: {}'.format(output_file))
        print('EXITTING!!!')
        sys.exit()
    else:
        print('Writing subject contrast matrix output file: {}'.format(output_file))
        numpy.savetxt(output_file, contrast_matrix, delimiter='\t', fmt="%s")



def write_evmatrix(sub_list, run_list, output_file):

    sub_num = len(sub_list)
    run_num = len(run_list)
    total_rows = sub_num*run_num

    #This creates an initial row of 0s that will need to be removed
    ev_matrix = numpy.zeros(sub_num)

    for sub_count in range(sub_num):
        for run_count in range(run_num):
            #For each subject, for each run, add a row that has a 1
            #in the subject column.
            this_row = numpy.zeros(sub_num)
            this_row[sub_count] = 1
            ev_matrix = numpy.row_stack((ev_matrix, this_row))

    #Remove the leading row of 0s
    ev_matrix = numpy.delete(ev_matrix, 0, 0)

    #Write the EV matrix out to a file
    if os.path.exists(output_file):
        print('EV matrix output file already exists!')
        print('EV matrix output file: {}'.format(output_file))
        print('EXITTING!!!')
        sys.exit()
    else:
        print('Writing EV matrix output file: {}'.format(output_file))
        numpy.savetxt(output_file, ev_matrix, delimiter='\t', fmt="%s")



def write_firstleveldirs(sub_list, run_list, output_file):

    firstlevel_dir_template = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/First_Level_PPI_amy_reap_run{run}.feat')
    output_lines = []

    for sub in sub_list:
        for run in run_list:
            this_line = firstlevel_dir_template.format(sub=sub, run=run)
            output_lines.append(this_line)

    #Check to see if the output file already exists
    if os.path.exists(output_file):
        print('Output file already exists!')
        print('Output file: {}'.format(output_file))
        print('Exitting!!!')
        sys.exit()
    else:
        print('Writing output file: {}'.format(output_file))
        with open(output_file,'w') as fid:
            for line in output_lines:
                fid.write('{}\n'.format(line))



if __name__ == '__main__':
    main()
    print('Done')