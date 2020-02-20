

import os
import shutil
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts', 'MRI_Analysis', 'fsl_templates', 'first_level_PPI_template_files_01312020/')
template_file = 'fsl_ppi_template.fsf'

template_string_list = ['[[SUBID]]', '[[TRS]]', '[[RUN]]', '[[ROI]]']

full_template = os.path.join(template_directory, template_file)

subs_to_run = [
               'EM0126',
               'EM0153'
               ]

# subs_to_run = [
              # 'EM0001'
              # 'EM0033',
              # 'EM0036',
              # 'EM0038',
              # 'EM0066',
              # 'EM0071',
              # 'EM0088',
              # 'EM0126',
              # 'EM0153',
              # 'EM0155',
              # 'EM0162',
              # 'EM0164',
              # 'EM0174',
              # 'EM0179',
              # 'EM0184',
              # 'EM0187',
              # 'EM0192',
              # 'EM0202',
              # 'EM0206',
              # 'EM0217',
              # 'EM0219',
              # 'EM0220',
              # 'EM0223',
              # 'EM0229',
              # 'EM0240',
              # 'EM0291',
              # 'EM0304',
              # 'EM0381',
              # 'EM0360',
              # 'EM0400',
              # 'EM0500',
              # 'EM0519',
              # 'EM0565',
              # 'EM0588',
              # 'EM0560',
              # 'EM0569',
              # 'EM0812',
              # 'EM0787',
              # 'EM0880',
              # 'EM1050'
              #  ]


# runs_to_run = ['1', '2', '4']
runs_to_run = ['1', '2', '3', '4']
# rois_to_run = ['amy', 'dACC', 'dlPFC', 'infPar', 'vlPFC', 'vmPFC']
# rois_to_run = [ ['dlPFCsphere', 'dist'] , ['vlPFCsphere', 'reap'] ]
# rois_to_run = ['dlPFCsphere', 'vlPFCsphere']
rois_to_run = ['amy']

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

            #Call FEAT with this new run file
            feat_call = 'feat {}'.format(run_template_file)
            print('System call: {}'.format(feat_call))
            try:
                this_feat_dir = os.path.join(this_env['EMDIR'], 'Analysis', 'MRI', 'sub-{}/Func/First_level_{}_ppi_run{}.feat'.format(sub,roi,run))
                if os.path.exists(this_feat_dir):
                  print('FEAT dir already exists: {}'.format(this_feat_dir))
                  print('Deleting it!')
                  shutil.rmtree(this_feat_dir)
                os.system(feat_call)
                #Create a fake reg directory for higher-level analysis
                #TODO: read in the output directory from the .fsf that was run!!!
                
                eft.create_fake_reg(this_feat_dir)
            except Exception as ex:
                print('Subject {}, run {}, roi {} did NOT run!'.format(sub,run,roi))
                print(ex)
                bad_runs.append('{}-run{}-{}'.format(sub,run,roi))
            good_runs.append('{}-run{}-{}'.format(sub,run,roi))

print('-------------------------------------')
print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))
print('-------------------------------------')