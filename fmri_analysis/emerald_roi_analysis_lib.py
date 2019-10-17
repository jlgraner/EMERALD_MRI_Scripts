

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import subprocess
import logging
import os


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
    mean_guess = x_array[np.where(y_array==y_array.max())]
    std_guess = '200'

    opt_params, _ = optimize.curve_fit(gauss_model, x_array, y_array, p0=(height_guess, mean_guess, std_guess))

    return opt_params


def mask_roi(image_file, roi_file, output_file, int_thresh):
    #Create a binary mask of the image_file only where it is above int_thresh.
    #Create another mask that is the union of the new mask and the roi_file.
    #3dcalc -a image_file -b roi_file -float -prefix output_file -exp "equals(ispositive(a-int_thresh), roi_file)"

    call_parts = [
                  '3dcalc',
                  '-a', image_file,
                  '-b', roi_file,
                  '-float',
                  '-prefix', output_file,
                  '-exp', '"equals(ispositive(a-int_thresh), b)"'
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
