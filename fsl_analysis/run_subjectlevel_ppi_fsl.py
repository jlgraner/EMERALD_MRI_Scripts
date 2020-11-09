
import os, subprocess
import emerald_fsl_tools as eft

this_env = os.environ

template_directory = os.path.join(this_env['EMDIR'], 'Scripts/MRI_Analysis/fsl_templates/subjectlevel_ppi_template_files_07132020/')
template_file = 'subjectlevel_amy_ppi_template.fsf'

template_string_list = ['[[SUBID]]']

full_template = os.path.join(template_directory, template_file)

# subs_to_run = [
#                'EM0946',
#                'EM1657',
#                'EM1611',
#                'EM1569',
#                'EM1708'
#                ]

subs_to_run = ['EM2562','EM2569']

good_runs = []
bad_runs = []

for sub in subs_to_run:
  run_template_file = os.path.join(template_directory, '{sub}_subjectlevel_amy_ppi.fsf'.format(sub=sub))
  #Replace the template .fsf file place-holder strings with this
  #run's strings and write a new .fsf file for this run.
  new_list = [sub]
  eft.read_replace_copy_design(full_template, template_string_list, new_list, run_template_file)

  #Call FEAT with this new run file
  feat_parts = [
                'feat',
                run_template_file
                ]
  print('Running call: {}'.format(feat_parts))
  error_flag = subprocess.call(feat_parts)
  if error_flag:
      print('Subject {} did NOT run!'.format(sub))
      bad_runs.append('{}'.format(sub))
  else:
      good_runs.append('{}'.format(sub))

print('Runs that ran: {}'.format(good_runs))
print('Runs that did NOT run: {}'.format(bad_runs))