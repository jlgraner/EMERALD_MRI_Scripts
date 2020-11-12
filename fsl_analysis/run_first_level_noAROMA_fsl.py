

import os
import time
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/fsl_templates/first_level_noAROMA_template_files_02192020/')
template_file = 'first_level_noAROMA_design_template.fsf'

template_string_list = ['[[SUBID]]', '[[TRS]]', '[[RUN]]']

full_template = os.path.join(template_directory, template_file)

subs_to_run = [
               'EM0229',
               'EM0240'
               ]


# runs_to_run = ['3','4']
runs_to_run = ['1','2','3','4']

retry = 1
max_retry = 6

good_runs = []
bad_runs = []
for sub in subs_to_run:
    for run in runs_to_run:
        run_template_file = os.path.join(template_directory, '{sub}_run{run}_first_level_noAROMA_design.fsf'.format(sub=sub,run=run))

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
                #If the output feat directory already exists, skip this run
                #TODO: read in the output directory from the .fsf file!!!
                this_feat_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/First_level_run{run}_noAROMA.feat'.format(sub=sub,run=run))
                if os.path.exists(this_feat_dir):
                    try_count = max_retry
                    raise RuntimeError('Output FEAT dir already exists!')

                #Call FEAT with this new run file
                feat_call = 'feat {}'.format(run_template_file)
                print('System call: {}'.format(feat_call))

                os.system(feat_call)
                #Create a fake reg directory for higher-level analysis
                
                eft.create_fake_reg(this_feat_dir)
                good_runs.append([sub,run])
                try_count = max_retry
            except Exception as ex:
                print('Subject {}, run {} did NOT run!'.format(sub,run))
                print(ex)
                bad_runs.append([sub,run,ex])
                try_count = try_count + 1
                time.sleep(wait_time)

print('-------------------------------------')
print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))
print('-------------------------------------')