__version__ = '0.1.0'

import os
import numpy as np
import shutil
from subprocess import call
from math import fmod
from PIL import Image
from pathlib import Path
from datetime import datetime
import time

start = time.time()

# TODO: pass as command line arguments
prefix_ct = 'wood_'
prefix_dc = 'dc_'
prefix_ob = 'ob_'
prefix_merged='merged_'

recon_filemask = prefix_merged + '####.tif'

# coefficiant range
range_start = 0.1
range_end = 0.5
range_step = 0.1

range_span = np.arange(range_start, range_end + range_step, range_step)

ct_dir = 'C:\\Users\\Jonathan Schaffner\\FHNW_Projct\\IP5\\SampleData\\Wood\\projections'
output_base_dir = 'C:\\Users\Jonathan Schaffner\\FHNW_Projct\\IP5\\GeneratedData'

# setup directories and filenames
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(os.path.join(output_base_dir, 'AddDecay', timestamp))
output_dir.mkdir(parents=True)

# file name of the images
ct_files = []
ob_files = []
dc_files = []

# images as PIL objects
ct_imgs = {}
ob_imgs = {}
dc_imgs = {}

# images as np arrays
ct_imgs_arr = {}
ob_imgs_arr = {}
dc_imgs_arr = {}
ct_imgs_arr_no_dc = {}

# average of all the DC samples as a np array
dc_avr = None

# np array Template
array_temp = None

# file names of alread processed images
processed_files = []


def main():

    load_images()

    get_dc_average()

    prev_Image = np.zeros_like(array_temp)

    # iterate over specified coefficiant range
    for decay_coefficiant in range_span:

        coef_output_dir = os.path.join(output_dir, str(round(decay_coefficiant, 1)))

    # iterate through projections
        for idx, file_name in enumerate(ct_files) :

            img = ct_imgs[file_name]

            # get tiffinfo from current image
            info = img.tag_v2

            # all previously decayed images summed up
            decay_img_arr = (prev_Image - dc_avr) * decay_coefficiant

            # add decay to current image and prevent overflow
            #merged_img_arr = np.empty_like(decay_img_arr, dtype='uint32')
            merged_img_arr = ct_imgs_arr[file_name].astype('uint32') + decay_img_arr.astype('uint32')       
            merged_img = Image.fromarray(np.clip(merged_img_arr, 0, 65535).astype('uint16'))

            # save image with tiffinfo from original image to preserve metadata
            merged_img.save(os.path.join(coef_output_dir , prefix_merged + str(idx).zfill(4) + ".tif"), format='TIFF', tiffinfo=info)

            prev_Image = merged_img_arr

            # add image to the processed list
            processed_files.append(file_name)

        print(f"Coefficient {round(decay_coefficiant, 1)} processed!")

    recon()
    print("Finished!")
    end = time.time()
    print("Time elapsed: " + str(end - start) + " seconds . . .")


# reconstruct using MuhRec with CLI params
def recon():

    recon_dir = os.path.join(output_dir, "Recon")

    for decay_coefficiant in range_span :

        print(f"Starting reconstruction for coefficiant {str(round(decay_coefficiant, 1))}")

        coef_input_dir = os.path.join(output_dir, str(round(decay_coefficiant, 1)))
        coef_input_mask = os.path.join(coef_input_dir, recon_filemask)
        coef_output_dir = os.path.join(recon_dir, str(round(decay_coefficiant, 1)))

        Path(coef_output_dir).mkdir(parents=True)

        # path to the application
        muhrec="C:\\Users\\Jonathan Schaffner\\FHNW_Projct\\IP5\\muhrec\\MuhRec.exe"
        cfgpath="C:\\Users\\Jonathan Schaffner\\FHNW_Projct\\IP5\\woodRecon.xml"

        # first_slice=350
        # last_slice=450
        
        # # select projection sub set
        # first_index="projections:firstindex="+str(first_slice)
        # last_index="projections:lastindex="+str(last_slice)

        file_mask="projections:filemask=" + coef_input_mask

        # set output path for the matrix
        matrix_path="matrix:path=" + coef_output_dir

        # call the reconstruction
        call([muhrec, "-f", cfgpath, file_mask, matrix_path])



# loads all images from the output_dir into global variables
def load_images():

    # load all files
    all_files = os.listdir(ct_dir)

    # get OB images
    global ob_files
    ob_files = list(filter(lambda x: x.startswith(prefix_ob), all_files))

    # Copy to subfolder for each coefficiant    
    for decay_coefficiant in range_span :

        coeff_dir = os.path.join(output_dir, str(round(decay_coefficiant,1)))
        os.mkdir(coeff_dir)

        # copy OB images
        for file in ob_files :
            source = os.path.join(ct_dir, file)
            target = os.path.join(coeff_dir, file)            
            shutil.copyfile(source, target)

            # load images
            ob_imgs[file] = Image.open(source)
            ob_imgs_arr[file] = np.array(ob_imgs[file])

        # get DC images
        global dc_files
        dc_files += list(filter(lambda x: x.startswith(prefix_dc), all_files))

        # copy DC images
        for file in dc_files :
            source = os.path.join(ct_dir, file)
            target = os.path.join(coeff_dir, file)
            shutil.copyfile(source, target)

            # load images
            dc_imgs[file] = Image.open(source)
            dc_imgs_arr[file] = np.array(dc_imgs[file])

    # get projection images
    global ct_files
    ct_files += list(filter(lambda x: x.startswith(prefix_ct), all_files))

    for file in ct_files :
        source = os.path.join(ct_dir, file)

        # load images
        ct_imgs[file] = Image.open(source)
        ct_imgs_arr[file] = np.array(ct_imgs[file])

        # set np array template
        global array_temp
        array_temp = np.empty_like(ct_imgs_arr[file], dtype='uint16')

## calculates the average DC image as a np array from the dc samples
def get_dc_average():
#    dc_avg = arr.mean(axis=0)
    sum = array_temp
    sum *= 0

    for name, arr in dc_imgs_arr.items() :
        sum += arr

    global dc_avr
    dc_avr =  sum // len(dc_imgs_arr)   

    for name, arr in ct_imgs_arr.items() : 
        ct_imgs_arr_no_dc[name] = arr - dc_avr


if __name__ == "__main__":
    main()