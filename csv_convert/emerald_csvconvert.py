
import os
import sys
from operator import itemgetter

#Importable functions:
#   csv2bids(input_file=None)
#   csv2fsl(input_file=None)

def __write_fsl(condition_name, start_times, durations, output_dir, subid, runid):
    
    #This function writes out condition files that can be read by FSL
    
    output_name = '{}_{}_{}_fslconds.txt'.format(subid, runid, condition_name)
    output_file = os.path.join(output_dir, output_name)
    
    #Don't look to see if the output file already exists; just
    #overwrite it if it does.
    
    fid = open(output_file, 'w')
    for count in range(len(start_times)):
        line_to_write = '{0:.2f}\t{1:.2f}\t1\n'.format(start_times[count],durations[count])
        fid.write(line_to_write)
    fid.close()
    
    
def __create_fsl_event_condition(event_type, lines, time_to_ignore, stimtype_select=None, stimdescrip_select=None):

    #lines is a list of lists. Each element of lines has the following:
    #[type, timefromstart, stimtype, stimdescrip]
    
    #This function returns start times for a given condition and sets all durations to 0.1
    #to mimic a single, short event.
    events_to_keep = []

    for element in lines:
        keep_it = 0
        if element[0] in event_type:
            keep_it = 1
            excluded_start = 0
            if (stimtype_select is not None) and (element[2] != stimtype_select):
                keep_it = 0
                excluded_start = 1
            if (stimdescrip_select is not None) and (element[3] != stimdescrip_select):
                keep_it = 0
                excluded_start = 1
        if keep_it:
            events_to_keep.append(element)

    #In this case we expect the event types to all be the same, as there are no end timee.

    #Create list of durations
    durations = []
    for i in events_to_keep:
        durations.append(0.1)

    #Create list of start times, shifted for pre-steady-state time
    start_times = []
    for element in events_to_keep:
        start_times.append(float(element[1]) - time_to_ignore)

    return start_times, durations


def __create_fsl_condition(start_type, end_type, lines, time_to_ignore, stimtype_select=None, stimdescrip_select=None):
    
    #lines is a list of lists. Each element of lines has the following:
    #[type, timefromstart, stimtype, stimdescrip]
    
    #This function returns start times and durations for a given condition.
    events_to_keep = []
    
    for element in lines:
        keep_it = 0
        #If the event type is either start_type or end_type, keep it.
        #If it is start_type, also consider the selection arguments.
        #When a start event is excluded, "excluded_start" gets set to
        #also exclude the following end event. This is clunky, but I don't
        #have much time right now.
        if element[0] in start_type:
            keep_it = 1
            excluded_start = 0
            if (stimtype_select is not None) and (element[2] != stimtype_select):
                keep_it = 0
                excluded_start = 1
            if (stimdescrip_select is not None) and (element[3] != stimdescrip_select):
                keep_it = 0
                excluded_start = 1
        elif element[0] in end_type:
            if excluded_start:
                keep_it = 0
                excluded_start = 0
            else:
                keep_it = 1

        if keep_it:
            events_to_keep.append(element)
            
    #The resulting list of lists should be in chronological order and there
    #should not be two start_type events or end_type events in a row (this
    #is dependent on the task code being written to support this).
    for i in range(len(events_to_keep)):
        #If the type values are the same for any sequential entries, something
        #is wrong.
        if events_to_keep[i][0] == events_to_keep[i-1][0]:
            msg = 'Events of identical type found when trying to create condition!'
            print(msg)
            raise ValueError(msg)
    
    #Split the list into two: one for start_type and one for end_type
    start_list = []
    end_list = []
    for element in events_to_keep:
        if element[0] in start_type:
            start_list.append(element)
        elif element[0] in end_type:
            end_list.append(element)
    
    #The two lists need to have the same number of elements
    if len(start_list) != len(end_list):
        msg = 'Number of start_type elements is {} but number of end_type elements is {}!'.format(len(start_list), len(end_list))
        print(msg)
        raise ValueError(msg)
        
    #Create list of durations
    durations = []
    for i in range(len(start_list)):
        durations.append(float(end_list[i][1]) - float(start_list[i][1]))
    
    #Create list of start times
    start_times = []
    for element in start_list:
        start_times.append(float(element[1]) - time_to_ignore)
    
    return start_times, durations

    
def __write_tsv(event_list, output_dir, subid, runid):
    
    #This function writes out an event .tsv file in the BIDS format
    
    output_name = 'sub-{}_ses-day3_task-emoreg_run-{}_events.tsv'.format(subid, runid)
    output_file = os.path.join(output_dir, output_name)
    
    #Don't look to see if the output file already exists; just
    #overwrite it if it does.
    
    header_line = 'onset\tduration\ttrial_type\tstim_info\tresponse_time\n'

    print('Writing file: {}'.format(output_file))

    fid = open(output_file, 'w')
    fid.write(header_line)
    for element in event_list:
        try:
            line_to_write = '{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\n'.format(element[0],element[1],element[2],element[3],element[4])
        except:
            line_to_write = '{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4}\n'.format(element[0],element[1],element[2],element[3],element[4])
        fid.write(line_to_write)
    fid.close()
    
    
def __create_bids_entries(type_label, start_type, end_type, lines, response_type=[None]):
    
    #This function gets called once per condition type, creating BIDS .tsv file
    #entries for one condition at a time. So, there should either be one response entry
    #for each start entry, or none at all.

    #lines is a list of lists. Each element of lines has the following:
    #[type, timefromstart, stimtype, stimdescrip]
    
    #This function returns start times and durations for a given condition.
    events_to_keep = []
    
    for element in lines:
        #If the event type is either start_type or end_type, keep it.
        if (element[0] in start_type) or (element[0] in end_type) or (element[0] in response_type):
            events_to_keep.append(element)
            

    #The resulting list of lists should be in chronological order and there
    #should not be two start_type events or end_type events in a row (this
    #is dependent on the task code being written to support this).
    for i in range(len(events_to_keep)):
        #If the type values are the same for any sequential entries, something
        #is wrong.
        if events_to_keep[i][0] == events_to_keep[i-1][0]:
            msg = 'Events of identical type found when trying to create condition!'
            print(msg)
            raise ValueError(msg)
    
    #Split the list into two: one for start_type and one for end_type
    start_list = []
    end_list = []
    response_list = []
    for element in events_to_keep:
        if element[0] in start_type:
            start_list.append(element)
        elif element[0] in end_type:
            end_list.append(element)
        if None not in response_type:
            if element[0] in response_type:
                response_list.append(element)
    
    #The three lists need to have the same number of elements
    if len(start_list) != len(end_list):
        msg = 'Number of start_type elements is {} but number of end_type elements is {}!'.format(len(start_list), len(end_list))
        print(msg)
        raise ValueError(msg)
    if None not in response_type:
        if (len(start_list) != len(response_list)):
            msg = 'Number of response_type elements is {} but number of end_type elements is {}!'.format(len(response_list),len(start_list))
            print(msg)
            raise ValueError(msg)
        
    #Create list of durations
    durations = []
    for i in range(len(start_list)):
        durations.append(float(end_list[i][1]) - float(start_list[i][1]))
    
    #Create list of start times
    start_times = []
    for element in start_list:
        start_times.append(float(element[1]))

    #Create list of response times
    #If the participant didn't respond to something, the entry will be "None"
    response_times = []
    #If no response type was passed, just make a list of n/a
    if None in response_type:
        for element in start_list:
            response_times.append('n/a')
    else:
        for element in response_list:
            response_times.append(element[3])

    #Create list of descriptions
    descriptions = []
    if None in response_type:
        for element in start_list:
            descriptions.append(element[3].strip())
    else:
        for element in response_list:
            descriptions.append(element[2].strip())

    #Put all the things into a list of lists. Each inner list will be one
    #entry in the output .tsv file.
    event_list = []
    for i in range(len(start_times)):
        event_list.append([start_times[i], durations[i], str(type_label), descriptions[i], response_times[i]])

    return event_list


def csv2bids(input_file=None):
    #This function is made to be run on files created by
    #emerald_emoreg2_task_output2csv.m
    #
    #This function will take a CSV file name and write an event
    #.tsv file compatible with BIDS.
    #
    #Right now the conditions it creates files for are hard-coded
    #to make things easier to call from the command line.
    
    #Check input file
    if os.path.split(input_file)[0] is '':
        input_file = os.path.join(os.getcwd(), input_file)
        output_dir = os.getcwd()
    else:
        output_dir = os.path.split(input_file)[0]
        
    if not os.path.exists(input_file):
        msg = 'Input file cannot be found: {}'.format(input_file)
        print(msg)
        raise ValueError(msg)
        
    #Open input file and read first line as the header
    print('Opening file: {}'.format(input_file))
    fid = open(input_file, 'r')
    header_line = fid.readline()
    #The line shouldn't have a comma at the end, but just in case...
    header_parts = header_line.strip().split(',')
    if header_parts[-1] is '':
        header_parts = header_parts[:-1]
    
    #Make sure the header is as expected
    print('Testing input header...')
    if header_parts[1] != 'timefromstart':
        msg = 'Input file has incorrect header format: {}'.format(input_file)
        print(msg)
        raise ValueError(msg)
    
    #Read in the rest of the file and standardize each line.
    #"all_line_parts" will be a list of lists, where each sub-list
    #contains the parts of a single line. These shouldn't ever get
    #out of order, but even if they do, each line contains time values.
    print('Reading input file...')
    all_line_parts = []
    for line in fid:
        #Remove the line return at the end of each line
        line = line.strip()
        #If there is a comma at the end, don't keep it
        if line[-1] is ',':
            line = line[:-1]
        line_parts = line.split(',')
        all_line_parts.append(line_parts)
    fid.close()
    
    #Extract the subject id from the input file name
    print('Finding subject ID and run ID from file name...')
    input_file_name = os.path.split(input_file)[1]
    subid = input_file_name.split('_')[2] #e.g. EM0019
    runstring = input_file_name.split('_')[3] #e.g. run1
    runid = '0{}'.format(runstring[-1])
    
    #Create lists of:
    #Start times of condition times relative to start of scan
    #Durations of conditions times
    #
    #Sections of scan time that are labeled as a certain condition
    #will be selected by identifying an event type that starts the
    #condition and an event type that ends the condition.
    #Each condition section will be from each occurrence of the start
    #event type to the first subsequent occurrence of the end event
    #type.
    
    all_events = {}

    #Create file lines for the arrow trials
    print('Creating arrow event list...')
    all_events['arrow_event_list'] = __create_bids_entries('arrow', ['negArrowOnset', 'neuArrowOnset'], ['negArrowOffset', 'neuArrowOffset'],
                                                all_line_parts, response_type=['negArrowResponse', 'neuArrowResponse'])

    #Create file lines for negative memory cue words
    print('Creating negative memory cue event list...')
    all_events['neg_mem_event_list'] = __create_bids_entries('negMemCue', ['negMemoryOnset'], ['negMemoryOffset'], all_line_parts)

    #Create file lines for neutral memory cue words
    print('Creating neutral memory cue event list...')
    all_events['neu_mem_event_list'] = __create_bids_entries('neuMemCue', ['neuMemoryOnset'], ['neuMemoryOffset'], all_line_parts)    
    
    #Create file lines for the negative memory strategy words
    print('Creating negative strategy cue event list...')
    all_events['neg_strat_event_list'] = __create_bids_entries('negStratCue', ['negStrategyOnset'], ['negStrategyOffset'], all_line_parts)

    #Create file lines for the neutral memory strategy words
    print('Creating neutral strategy cue event list...')
    all_events['neu_strat_event_list'] = __create_bids_entries('neuStratCue', ['neuStrategyOnset'], ['neuStrategyOffset'], all_line_parts)

    #Create file lines for the negative valence prompts
    print('Creating negative valence rating event list...')
    all_events['neg_vrate_event_list'] = __create_bids_entries('negVRate', ['negValenceOnset'], ['negValenceOffset'], all_line_parts, response_type=['negValenceResponse'])

    #Create file lines for the neutral valence prompts
    print('Creating neutral valence rating event list...')
    all_events['neu_vrate_event_list'] = __create_bids_entries('neuVRate', ['neuValenceOnset'], ['neuValenceOffset'], all_line_parts, response_type=['neuValenceResponse'])

    #Create file lines for the negative arousal prompt
    print('Creating negative arousal rating event list...')
    all_events['neg_arate_event_list'] = __create_bids_entries('negARate', ['negArousalOnset'], ['negArousalOffset'], all_line_parts, response_type=['negArousalResponse'])

    #Create file lines for the neutral arousal prompt
    print('Creating neutral arousal rating event list...')
    all_events['neu_arate_event_list'] = __create_bids_entries('neuARate', ['neuArousalOnset'], ['neuArousalOffset'], all_line_parts, response_type=['neuArousalResponse'])
    
    #Put all the event lists together
    big_list = []
    for key in all_events.keys():
        for element in all_events[key]:
            big_list.append(element)

    #Sort the big list of events
    big_list_sort = sorted(big_list, key=itemgetter(0))

    __write_tsv(big_list_sort, output_dir, subid, runid)

    print('-----Done!-----')


def csv2fsl(input_file=None, output_dir=None):
    #This function will take a CSV file name and write condition
    #files (one file per condition) that can be read into FSL.
    #
    #Right now the conditions it creates files for are hard-coded
    #to make things easier to call from the command line.
    
    #Set the number of seconds that have been removed from the fMRI data
    #to account for approach to steady-state.
    #NOTE: The raw fMRI data include ALL of the data; there are no official
    #"disdaq"s. There is an 8-second fixation cross at the beginning of the
    #task presentation.
    #This needs to be subtracted from the event onset times when using the
    #"Delete volumes" option in FSL.
    time_to_ignore = 8.0
    

    #Check passed output directory, if there was one
    if output_dir is not None:
        if not os.path.exists(output_dir):
            print('Output directory cannot be found! Creating it: {}'.format(output_dir))
            os.makedirs(output_dir)

    #Check input file and extract output directory if none was passed
    if os.path.split(input_file)[0] is '':
        input_file = os.path.join(os.getcwd(), input_file)
        if output_dir is None:
            output_dir = os.getcwd()
    elif output_dir is None:
        output_dir = os.path.split(input_file)[0]
        
    if not os.path.exists(input_file):
        msg = 'Input file cannot be found: {}'.format(input_file)
        print(msg)
        raise ValueError(msg)
        
    
    #Open input file and read first line as the header
    fid = open(input_file, 'r')
    header_line = fid.readline()
    #The line may or may not have a comma at the end,
    #depending on if it has been opened and saved in Excel.
    header_parts = header_line.strip().split(',')
    if header_parts[-1] is '':
        header_parts = header_parts[:-1]
    
    #Make sure the header is as expected
    if header_parts[1] != 'timefromstart':
        msg = 'Input file has incorrect header format: {}'.format(input_file)
        print(msg)
        raise ValueError(msg)
    
    #Read in the rest of the file and standardize each line.
    #"all_line_parts" will be a list of lists, where each sub-list
    #contains the parts of a single line. These shouldn't ever get
    #out of order, but even if they do, each line contains time values.
    all_line_parts = []
    for line in fid:
        #Remove the line return at the end of each line
        line = line.strip()
        #If there is a comma at the end, don't keep it
        if line[-1] is ',':
            line = line[:-1]
        line_parts = line.split(',')
        all_line_parts.append(line_parts)
    fid.close()
    
    #Extract the subject id from the input file name
    input_file_name = os.path.split(input_file)[1]
    subid = input_file_name.split('_')[2] #e.g. EM0019
    runid = input_file_name.split('_')[3] #e.g. run1
    
    #Create lists of:
    #Start times of condition times relative to start of scan
    #Durations of conditions times
    #
    #Sections of scan time that are labeled as a certain condition
    #will be selected by identifying an event type that starts the
    #condition and an event type that ends the condition.
    #Each condition section will be from each occurrence of the start
    #event type to the first subsequent occurrence of the end event
    #type.
    

    #Write a conditoin file for motor events
    start_times, durations = __create_fsl_event_condition(['negArrowResponse', 'neuArrowResponse', 'neuValenceResponse', 'negValenceResponse', 'neuArousalResponse', 'negArousalResponse'], all_line_parts, time_to_ignore)
    __write_fsl('motorresponses', start_times, durations, output_dir, subid, runid)

    #Write a condition file for negative memory cue words
    start_times, durations = __create_fsl_condition(['negMemoryOnset'], ['negMemoryOffset'], all_line_parts, time_to_ignore)
    __write_fsl('negmemorywords', start_times, durations, output_dir, subid, runid)
    
    #Write a condition file for neutral memory cue words
    start_times, durations = __create_fsl_condition(['neuMemoryOnset'], ['neuMemoryOffset'], all_line_parts, time_to_ignore)
    __write_fsl('neumemorywords', start_times, durations, output_dir, subid, runid)

    #Write a condition file for the arrow trials
    start_times, durations = __create_fsl_condition(['negArrowBlockOnset','neuArrowBlockOnset'], ['negArrowBlockOffset','neuArrowBlockOffset'], all_line_parts, time_to_ignore)
    __write_fsl('arrowblocks', start_times, durations, output_dir, subid, runid)
    
    #Write a condition file for the negative strategy cue words
    # start_times, durations = __create_fsl_condition(['negStrategyOnset'], ['negStrategyOffset'], all_line_parts, time_to_ignore)
    # __write_fsl('negstrategycues', start_times, durations, output_dir, subid, runid)

    #Write a condition file for the neutral strategy cue words
    start_times, durations = __create_fsl_condition(['neuStrategyOnset'], ['neuStrategyOffset'], all_line_parts, time_to_ignore)
    __write_fsl('neustrategycues', start_times, durations, output_dir, subid, runid)

    #Write a condition file for the reappraisal strategy cue words
    start_times, durations = __create_fsl_condition(['negStrategyOnset'], ['negStrategyOffset'], all_line_parts, time_to_ignore, stimdescrip_select='REAPPRAISE')
    __write_fsl('reapstrategycues', start_times, durations, output_dir, subid, runid)

    #Write a condition file for the distract strategy cue words
    start_times, durations = __create_fsl_condition(['negStrategyOnset'], ['negStrategyOffset'], all_line_parts, time_to_ignore, stimdescrip_select='DISTRACT')
    __write_fsl('diststrategycues', start_times, durations, output_dir, subid, runid)

    #Write a condition file for the negative flow strategy cue words
    start_times, durations = __create_fsl_condition(['negStrategyOnset'], ['negStrategyOffset'], all_line_parts, time_to_ignore, stimdescrip_select='FLOW')
    __write_fsl('negflowstrategycues', start_times, durations, output_dir, subid, runid)

    #Write a condition file for rating scales
    start_times, durations = __create_fsl_condition(['negValenceOnset', 'neuValenceOnset'], ['negArousalOffset', 'neuArousalOffset'], all_line_parts, time_to_ignore)
    __write_fsl('ratings', start_times, durations, output_dir, subid, runid)

def search_for_files(input_dir, search_string):
    #Look for files in input_dir that contain search_string in their names
    contents = os.listdir(input_dir)
    file_list = []
    for element in contents:
        if (search_string in element) and (element[-4:] == '.csv'):
            file_list.append(os.path.join(input_dir, element))
    #Return the list of files
    return file_list