
import os, subprocess
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/fsl_templates/subjectlevel_ppi_template_files_01222020/')
template_file = 'subjectlevel_{ppi}_ppi_template.fsf'

ppi_list = ['dlPFCdist', 'vlPFCreap']

template_string_list = ['[[SUBID]]']

full_template = os.path.join(template_directory, template_file)

subs_to_run = [
               'EM0001'
               ]

# subs_to_run = [
#               # 'EM0001',
#               'EM0033',
#               'EM0036',
#               'EM0038',
#               'EM0066',
#               'EM0071',
#               'EM0088',
#               'EM0126',
#               'EM0153',
#               'EM0155',
#               'EM0162',
#               'EM0164',
#               'EM0174',
#               'EM0179',
#               'EM0184',
#               'EM0187',
#               'EM0192',
#               'EM0202',
#               'EM0206',
#               'EM0217',
#               'EM0219',
#               'EM0220',
#               'EM0223',
#               'EM0229',
#               'EM0240',
#               'EM0291',
#               'EM0304',
#               'EM0381',
#               'EM0360',
#               'EM0400',
#               'EM0500',
#               'EM0519',
#               'EM0565',
#               'EM0588',
#               'EM0560',
#               'EM0569'
#               ]


good_runs = []
bad_runs = []

for sub in subs_to_run:
  for ppi in ppi_list:
    ppi_template = full_template.format(ppi=ppi)
    run_template_file = os.path.join(template_directory, '{sub}_subjectlevel_{ppi}_ppi.fsf'.format(sub=sub,ppi=ppi))
    #Replace the template .fsf file place-holder strings with this
    #run's strings and write a new .fsf file for this run.
    new_list = [sub]
    eft.read_replace_copy_design(ppi_template, template_string_list, new_list, run_template_file)

    #Call FEAT with this new run file
    feat_parts = [
                  'feat',
                  run_template_file
                  ]
    print('Running call: {}'.format(feat_parts))
    error_flag = subprocess.call(feat_parts)
    if error_flag:
        print('Subject {} {} did NOT run!'.format(sub, ppi))
        bad_runs.append('{}-{}'.format(sub,ppi))
    else:
        good_runs.append('{}-{}'.format(sub,ppi))

print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))