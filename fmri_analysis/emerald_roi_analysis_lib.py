

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import subprocess
import logging
import os
import nibabel as nb

this_code = 'emerald_roi_analysis_lib.py'

def run_mean(output_file, input_list):
    #Run AFNI's 3dMean

    #Check output file
    if os.path.exists(output_file):
        print('Output file already exists: {}'.format(output_file))
        print('Returning None! -- {}.run_mean()'.format(this_code))
        return None

    call_parts = [
                  '3dMean',
                  '-sum',
                  '-prefix', output_file
                  ]

    #Add the elemenents of the input list to the call parts
    for element in input_list:
        call_parts.append(str(element))

    print('Calling: {}'.format(' '.join(call_parts)))
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('Something went wrong with 3dMean call! -- {}.run_mean()'.format(this_code))
        return None
    return output_file
    

def run_undump(output_dir, master, peak_file, rad, mask):
    #Run AFNI's 3dUndump

    #Create output file name
    mask_file = os.path.split(mask)[-1]
    if mask_file[-7:] == '.nii.gz':
        mask_prefix = mask_file.split('.nii.gz')[0]
    else:
        mask_prefix = os.path.splitext(mask_file)[0]
    prefix = os.path.join(output_dir, '{}_peak_sphere.nii.gz'.format(mask_prefix))

    call_parts = [
                  '3dUndump',
                  '-master', master,
                  '-prefix', prefix,
                  '-datum', 'float',
                  '-ijk',
                  '-srad', rad,
                  '-mask', mask,
                  peak_file
                 ]

    print('Calling: {}'.format(' '.join(call_parts)))
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('Something went wrong with 3dUndump call!')
        return None
    return prefix

def run_featquery(cope_dir, output_dir, roi_file):
    #Run FSL's featquery

    call_parts = [
                  'featquery',
                  '1',
                  cope_dir,
                  '1',
                  'stats/cope1',
                  output_dir,
                  '-p',
                  # '-b',
                  roi_file
                  ]
    #Call featquery
    print('Calling: {}'.format(' '.join(call_parts)))
    error_flag = subprocess.call(call_parts)
    if error_flag:
        print('Something went wrong with featquery call!')
        return None
    #Save the ROI mean, as a string, into the dictionary
    report_file = os.path.join(cope_dir, output_dir, 'report.txt')
    return report_file

def gauss_model(x, height, mean, std):
    return height*np.exp(-((x-mean)/(4.0*std))**2)


def create_histo(input_file, bins=122, minimum=0, maximum=None):
    #Create a histogram of the input image with 122 bins.
    #Set max equal to the maximum of the image and the minimum to 0.
    #Also create an ordinate array that has values at the centers of the bins.
    
    #Check the input file
    if not os.path.exists(input_file):
        logging.error('input_file not found: {}'.format(input_file))
        return None

    #Create name for temporary histogram file
    histo_file = os.path.join(os.path.split(input_file)[0], 'temp_histogram.txt')

    #Create strings of bins, min and max
    bins = str(bins)
    minimum = str(minimum)
    if maximum is not None:
        maximum = str(maximum)
    else:
        #Find maximum intensity from image
        call_parts = [
                    'fslstats',
                    input_file,
                    '-R'
                   ]
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()
        maximum = call_output.decode("utf-8").split()[-1]

    #Create histogram bin values
    call_parts = [
                  'fslstats',
                  input_file,
                  '-H', bins, minimum, maximum
                 ]
    proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
    call_output, stderr = proc.communicate()
    y_string = call_output.decode("utf-8")
    y_list = y_string.split()
    y_array = np.array(y_list)
    y_array = y_array.astype(np.float)

    #Create histogram bin values
    index_list = range(int(bins))
    factor = float(maximum)/int(bins)
    x_list = []
    for element in index_list:
        x_list.append((element*factor)+(0.5*factor))
    x_array = np.array(x_list)

    return x_array, y_array


def split_histo(x_array, y_array):
    #Find roughly where the histogram breaks into two gaussians
    #Return the x and y values for each section
    y_diff = np.diff(y_array)
    cut_point = np.where(y_diff>0)[0][0]

    x_first = x_array[:cut_point]
    x_last = x_array[cut_point:]
    y_first = y_array[:cut_point]
    y_last = y_array[cut_point:]

    return x_first, y_first, x_last, y_last


def fit_gauss(x_array, y_array):
    #Fit a gaussian to the passed data, using optimize.curve_fit
    #Set initial parameters based on the passed data
    height_guess = y_array.max()
    mean_guess = x_array[np.where(y_array==y_array.max())][-1]
    std_guess = 200

    opt_params, _ = optimize.curve_fit(gauss_model, x_array, y_array, p0=(height_guess, mean_guess, std_guess))

    return opt_params


def mask_roi(image_file, roi_file, output_file, int_thresh):
    #Create a binary mask of the image_file only where it is above int_thresh.
    #Create another mask that is the union of the new mask and the roi_file.

    call_parts = [
                  '3dcalc',
                  '-a', image_file,
                  '-b', roi_file,
                  '-float',
                  '-prefix', output_file,
                  '-exp', 'ispositive(a-{})*b'.format(int_thresh)
                  ]
    proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
    call_output, stderr = proc.communicate()

    return output_file


def mean_image(image_file, output_image):
    #Create a mean of the passed image

    #If the output image is already there, delete it
    if os.path.exists(output_image):
        os.remove(output_image)

    call_parts = [
                  '3dTstat',
                  '-mean',
                  '-prefix', output_image,
                  image_file
                  ]

    proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
    call_output, stderr = proc.communicate()

    return output_image

def save_plot(x_arr_list, y_arr_list, output_file, sub, run):
    #Create a plot of some data and save it to a file
    plt.figure(num='save_plot_temp')
    for element in zip(x_arr_list, y_arr_list):
        plt.plot(element[0], element[1])
    plt.xlabel('Intensity')
    plt.ylabel('# of Voxels in Bin')
    plt.title('Sub {}, Run {}'.format(sub, run))
    plt.savefig(output_file)
    plt.close(fig='save_plot_temp')


def count_mask(input_mask):
    #Count the number of voxels included in the passed mask
    mask_vol = nb.load(input_mask)
    mask_data = mask_vol.get_data()

    return mask_data.sum()


def _create_html_part(sub, run, histo_png, fit_png, int_thresh):

    histo_png_short = '.\{}\{}'.format(histo_png.split('/')[-2], histo_png.split('/')[-1])
    fit_png_short = '.\{}\{}'.format(fit_png.split('/')[-2], fit_png.split('/')[-1])

    line_list = [
    '<H2>{sub}, Run {run}'.format(sub=sub, run=run),
    '<H3>Intensity Threshold: {:.2f}'.format(int_thresh),
    '<br>',
    '<IMAGE SRC="{histo}" HEIGHT=300 ALT="histo_png">'.format(histo=histo_png_short),
    '<IMAGE SRC="{fit}" HEIGHT=300 ALT="fit_png">'.format(fit=fit_png_short),
    '<br>'
                ]
    return line_list


def write_html(info_dict, output_dir):
    #Write an html file linking all the created png files
    #for visual qa ofthe fitting process.
    html_lines = []
    first_lines = [
    '<HTML>',
    '<HEAD>',
    '<TITLE>ROI Intensity Masking Fit Plots</TITLE>',
    '</HEAD>',
    '<BODY>'
                 ]

    last_lines = [
    '</BODY>',
    '</HTML>'
                 ]

    html_lines = html_lines + first_lines
    for sub in info_dict.keys():
        for run in info_dict[sub].keys():
            if 'histo_png' in info_dict[sub][run]:
                histo_png = info_dict[sub][run]['histo_png']
                fit_png = info_dict[sub][run]['fit_png']
                int_thresh = info_dict[sub][run]['int_thresh']
                new_lines = _create_html_part(sub, run, histo_png, fit_png, int_thresh)
                html_lines = html_lines + new_lines
    html_lines = html_lines + last_lines

    output_file = os.path.join(output_dir, 'IntensityMasking_Plots.html')
    with open(output_file, 'w') as fo:
        for line in html_lines:
            fo.write('{}\n'.format(line))

    return output_file


def write_csv(info_dict, roi_list, output_dir):
    #Write a csv file containing information on how many voxels were
    #excluded from each participant's mask.
    lines_to_write = []
    header_line = 'SubID,ROI,MaskVox,DiffFromOrig'
    lines_to_write.append(header_line)
    for sub in info_dict.keys():
        for roi in roi_list:
            mask_count = info_dict[sub][roi]['final_mask_count']
            diff_count = info_dict[sub][roi]['final_mask_diff']
            this_line = '{},{},{},{}'.format(sub,roi,mask_count,diff_count)
            lines_to_write.append(this_line)

    output_file = os.path.join(output_dir, 'IntensityMasked_ROI_Counts.csv')

    with open(output_file, 'w') as fo:
        for line in lines_to_write:
            fo.write('{}\n'.format(line))

    return output_file