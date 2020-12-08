
import os, time
import shutil
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/fsl_templates/subjectlevel_template_files_11042019/')
template_file = 'subjectlevel_design_template.fsf'

template_string_list = ['[[SUBID]]']

full_template = os.path.join(template_directory, template_file)

run_log_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI')
run_log_file = os.path.join(run_log_dir, 'run_subject_level_fsl_LOG.txt')
#Write a timestamp to the log file
time_stamp = str(time.localtime()[1])+str(time.localtime()[2])+str(time.localtime()[0])+str(time.localtime()[3])+str(time.localtime()[4])
fid = open(run_log_file, 'a')
fid.write('----------------------------------\n')
fid.write('NEW RUN: {}\n'.format(time_stamp))
fid.close()

subs_to_run = ['EM0291']

# subs_to_run = [
#                'EM1050',
#                'EM0946',
#                'EM1201',
#                'EM1657',
#                'EM1611',
#                'EM1569',
#                'EM1708',
#                'EM1655',
#                'EM2562',
#                'EM2569'
#                ]

overwrite = 1
retry = 1
max_retry = 6

good_runs = []
bad_runs = []

for sub in subs_to_run:
    run_template_file = os.path.join(template_directory, '{sub}_subjectlevel_design.fsf'.format(sub=sub))
    #Replace the template .fsf file place-holder strings with this
    #run's strings and write a new .fsf file for this run.
    new_list = [sub]

    if retry:
        try_count = 1
        wait_time = 120 #seconds
    else:
        try_count = max_retry - 1
        wait_time = 1
    while try_count < max_retry:
      try:
        this_feat_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/Second_level_allruns.gfeat'.format(sub=sub))
        #If the output directory exists and overwrite is set, delete it.
        if os.path.exists(this_feat_dir):
            print('FEAT directory already exists...')
            if overwrite:
                print('Overwrite set...')
                print('Deleting: {}'.format(this_feat_dir))
                shutil.rmtree(this_feat_dir)
            else:
                raise RuntimeError('Overwrite not set! Skipping!')

        eft.read_replace_copy_design(full_template, template_string_list, new_list, run_template_file)

        #Call FEAT with this new run file
        feat_call = 'feat {}'.format(run_template_file)
        print('Running call: {}'.format(feat_call))
        os.system(feat_call)

        #Check for output directory (FEAT does not pass errors)
        if not os.path.exists(this_feat_dir):
            print('FEAT call failed: {}'.format(sub))
            raise RuntimeError('FEAT call failed!')

        good_runs.append('{}'.format(sub))
        fid = open(run_log_file, 'a')
        fid.write('GOOD: {}\n'.format(sub))
        fid.close()
        try_count = max_retry

      except Exception as ex:
        bad_runs.append('{}'.format(sub))
        print('Subject {} did NOT run!'.format(sub))
        print(ex)
        fid = open(run_log_file, 'a')
        fid.write('BAD: {}, try_count={}\n'.format(sub,try_count))
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
print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))