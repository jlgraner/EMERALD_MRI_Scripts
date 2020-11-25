

import os, shutil
import time
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/fsl_templates/first_level_template_files_11192020/')
template_file = 'first_level_design_template.fsf'

run_log_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI')
run_log_file = os.path.join(run_log_dir, 'run_first_level_fsl_LOG.txt')
#Write a timestamp to the log file
time_stamp = str(time.localtime()[1])+str(time.localtime()[2])+str(time.localtime()[0])+str(time.localtime()[3])+str(time.localtime()[4])
fid = open(run_log_file, 'a')
fid.write('----------------------------------\n')
fid.write('NEW RUN: {}\n'.format(time_stamp))
fid.close()

template_string_list = ['[[SUBID]]', '[[TRS]]', '[[RUN]]']

full_template = os.path.join(template_directory, template_file)

subs_to_run = [
               #'EM0188',
               'EM0192',
               'EM0202',
               'EM0206',
               'EM0217',
               'EM0219'
               ]


# runs_to_run = ['2']
runs_to_run = ['1','2','3','4']

overwrite = 1
retry = 1
max_retry = 6

good_runs = []
bad_runs = []
for sub in subs_to_run:
    for run in runs_to_run:
        run_template_file = os.path.join(template_directory, '{sub}_run{run}_first_level_design.fsf'.format(sub=sub,run=run))

        #For now, set the number TRs based on what should be there, rather than on what IS there.
        if run in ['1','3']:
            trs = '236'
        else:
            trs = '215'

        #Replace the template .fsf file place-holder strings with this
        #run's strings and write a new .fsf file for this run.
        new_list = [sub, trs,run]
        eft.read_replace_copy_design(full_template, template_string_list, new_list, run_template_file)
        
        if retry:
            try_count = 1
            wait_time = 120 #seconds
        else:
            try_count = max_retry - 1
            wait_time = 1
        while try_count < max_retry:
            try:
                #TODO: read in the output directory from the .fsf that was run!!!
                this_feat_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/First_level_run{run}.feat'.format(sub=sub,run=run))
                #If the output directory exists and overwrite is set, delete it.
                if os.path.exists(this_feat_dir):
                    print('FEAT directory already exists...')
                    if overwrite:
                        print('Overwrite set...')
                        print('Deleting: {}'.format(this_feat_dir))
                        shutil.rmtree(this_feat_dir)
                    else:
                        raise RunTimeError('Overwrite not set! Skipping!')

                #Call FEAT with this new run file
                feat_call = 'feat {}'.format(run_template_file)
                print('System call: {}'.format(feat_call))
                os.system(feat_call)
                #Create a fake reg directory for higher-level analysis
                eft.create_fake_reg(this_feat_dir)
                good_runs.append('{}-run{}'.format(sub,run))
                fid = open(run_log_file, 'a')
                fid.write('GOOD: {}-run{}\n'.format(sub,run))
                fid.close()
                try_count = max_retry
            except Exception as ex:
                print('Subject {}, run {} did NOT run!'.format(sub,run))
                print(ex)
                bad_runs.append('{}-run{}'.format(sub,run))
                fid = open(run_log_file, 'a')
                fid.write('BAD: {}-run{}, try_count={}\n'.format(sub,run,try_count))
                fid.write(str(ex)+'\n')
                fid.close()
                try_count = try_count + 1
                time.sleep(wait_time)
                
fid = open(run_log_file, 'a')
fid.write('FINISHED\n')
fid.write('Runs that ran: {}\n'.format(good_runs))
fid.write('Runs that did NOT run: {}\n'.format(bad_runs))
fid.write('-------------------------------------\n')
fid.close()
print('-------------------------------------')
print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))
print('-------------------------------------')