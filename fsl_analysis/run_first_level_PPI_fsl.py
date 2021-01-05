

import os, time
import shutil
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts', 'MRI_Analysis', 'fsl_templates', 'first_level_PPI_template_files_01042021/')
template_file = 'fsl_ppi_template.fsf'

template_string_list = ['[[SUBID]]', '[[TRS]]', '[[RUN]]', '[[ROI]]']

full_template = os.path.join(template_directory, template_file)

run_log_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI')
run_log_file = os.path.join(run_log_dir, 'run_first_level_ppi_fsl_LOG.txt')
#Write a timestamp to the log file
time_stamp = str(time.localtime()[1])+str(time.localtime()[2])+str(time.localtime()[0])+str(time.localtime()[3])+str(time.localtime()[4])
fid = open(run_log_file, 'a')
fid.write('----------------------------------\n')
fid.write('NEW RUN: {}\n'.format(time_stamp))
fid.close()

subs_to_run = ['EM0001']

runs_to_run = ['2','3','4']
# runs_to_run = ['1', '2', '3', '4']
# rois_to_run = ['amy', 'dACC', 'dlPFC', 'infPar', 'vlPFC', 'vmPFC']
# rois_to_run = [ ['dlPFCsphere', 'dist'] , ['vlPFCsphere', 'reap'] ]
# rois_to_run = ['dlPFCsphere', 'vlPFCsphere']
rois_to_run = ['amy']

overwrite = 1
retry = 1
max_retry = 6

good_runs = []
bad_runs = []
for sub in subs_to_run:
    for run in runs_to_run:
        for roi in rois_to_run:
            run_template_file = os.path.join(template_directory, '{sub}_run{run}_fsl_ppi_{roi}_design.fsf'.format(sub=sub,run=run,roi=roi))

            #For now, set the number TRs based on what should be there, rather than on what IS there.
            if run in ['1','3']:
                trs = '236'
            else:
                trs = '215'

            #Replace the template .fsf file place-holder strings with this
            #run's strings and write a new .fsf file for this run.
            new_list = [sub,trs,run,roi]
            eft.read_replace_copy_design(full_template, template_string_list, new_list, run_template_file)

            if retry:
                try_count = 1
                wait_time = 120 #seconds
            else:
                try_count = max_retry - 1
                wait_time = 1
            while try_count < max_retry:
                try:
                    this_feat_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{}/Func/First_level_{}_ppi_run{}.feat'.format(sub,roi,run))
                    #If the output directory exists and overwrite is set, delete it.
                    if os.path.exists(this_feat_dir):
                        print('FEAT directory already exists...')
                        if overwrite:
                            print('Overwrite set...')
                            print('Deleting: {}'.format(this_feat_dir))
                            shutil.rmtree(this_feat_dir)
                        else:
                            raise RuntimeError('Overwrite not set! Skipping!')
                    #Call FEAT with this new run file
                    feat_call = 'feat {}'.format(run_template_file)
                    print('System call: {}'.format(feat_call))
                    os.system(feat_call)
                    #Create a fake reg directory in the new FEAT dir
                    eft.create_fake_reg(this_feat_dir)
                    good_runs.append('{}-run{}-{}'.format(sub,run,roi))
                    fid = open(run_log_file, 'a')
                    fid.write('GOOD: {}-run{}, {}\n'.format(sub,run,roi))
                    fid.close()
                    try_count = max_retry
                except Exception as ex:
                    print('Subject {}, run {}, roi {} did NOT run!'.format(sub,run,roi))
                    print(ex)
                    bad_runs.append('{}-run{}-{}'.format(sub,run,roi))
                    fid = open(run_log_file, 'a')
                    fid.write('BAD: {}-run{}, {}, try_count={}\n'.format(sub,run,roi,try_count))
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