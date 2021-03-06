

import os
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/fsl_templates/first_level_motor_UT_template_files_09192019/')
template_file = 'first_level_design_template_UT_motor.fsf'

template_string_list = ['[[SUBID]]', '[[TRS]]', '[[RUN]]']

full_template = os.path.join(template_directory, template_file)

subs_to_run = [
               'UT0005',
               'UT0024',
               'UT0025'
               ]


# runs_to_run = ['2','3','4']
runs_to_run = ['1','2','3','4']


good_runs = []
bad_runs = []
for sub in subs_to_run:
    for run in runs_to_run:
        run_template_file = os.path.join(template_directory, '{sub}_run{run}_motor_first_level_design.fsf'.format(sub=sub,run=run))

        #For now, set the number TRs based on what should be there, rather than on what IS there.
        if run in ['1','3']:
            trs = '236'
        else:
            trs = '215'

        #Replace the template .fsf file place-holder strings with this
        #run's strings and write a new .fsf file for this run.
        new_list = [sub, trs,run]
        eft.read_replace_copy_design(full_template, template_string_list, new_list, run_template_file)

        #Call FEAT with this new run file
        feat_call = 'feat {}'.format(run_template_file)
        print('System call: {}'.format(feat_call))
        try:
            os.system(feat_call)
            good_runs.append('{}-run{}'.format(sub,run))
            #Create a fake reg directory for higher-level analysis
            #TODO: read in the output directory from the .fsf that was run!!!
            this_feat_dir = os.path.join(this_env['EMDIR'], 'Analysis/MRI/sub-{sub}/Func/First_level_motor_run{run}.feat'.format(sub=sub,run=run))
            eft.create_fake_reg(this_feat_dir)
        except Exception as ex:
            print('Subject {}, run {} did NOT run!'.format(sub,run))
            print(ex)
            bad_runs.append('{}-run{}'.format(sub,run))

print('-------------------------------------')
print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))
print('-------------------------------------')