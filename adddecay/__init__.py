__version__ = '0.1.0'

import os
import numpy
import shutil
import matplotlib

from PIL import Image, ImageOps

from pathlib import Path
from datetime import datetime
import time

start = time.time()

# TODO: pass as command line arguments
prefix_ct = 'wood_'
prefix_dc = 'dc_'
prefix_ob = 'ob_'

ct_dir = 'C:\\Users\\Jonathan Schaffner\\FHNW_Projct\\IP5\\SampleData\\Wood\\projections'
output_base_dir = 'C:\\Users\Jonathan Schaffner\\FHNW_Projct\\IP5\\GeneratedData'
image_interval_ms = 50

# setup directories and filenames
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(os.path.join(output_base_dir, 'AddDecay', timestamp))
output_decayed = Path(os.path.join(output_dir, 'Decay'))
output_dir.mkdir(parents=True)
output_decayed.mkdir(parents=True)

# file name of the images
ct_files = []
ob_files = []
dc_files = []

# images as PIL objects
ct_imgs = {}
ob_imgs = {}
dc_imgs = {}

# images as numpy arrays
ct_imgs_arr = {}
ob_imgs_arr = {}
dc_imgs_arr = {}
ct_imgs_arr_no_dc = {}

# average of all the DC samples as a numpy array
dc_avr = None

# numpy array Template
array_temp = None

# file names of alread processed images
processed_files = []

def main():    

    load_images()  

    get_dc_average();  

    # iterate through projections
    for idx, file_name in enumerate(ct_files) :

        img = ct_imgs[file_name]

        # get tiffinfo from current image
        info = img.tag_v2

        # all previously decayed images summed up
        decay_img_arr = decay()
        decay_img = Image.fromarray(decay_img_arr)

        # add decay to current image and prevent overflow
        merged_img_arr = numpy.empty_like(decay_img_arr, dtype='uint32')
        merged_img_arr = ct_imgs_arr[file_name].astype('uint32') + decay_img_arr.astype('uint32')       
        merged_img = Image.fromarray(numpy.clip(merged_img_arr, 0, 65535).astype('uint16'))

        # save images with tiffinfo from original image to preserve metadata
        decay_img.save(os.path.join(output_decayed, "decay_" + str(idx).zfill(4) + ".tif"), format='TIFF', tiffinfo=info)
        merged_img.save(os.path.join(output_dir, "added_" + str(idx).zfill(4) + ".tif"), format='TIFF', tiffinfo=info)

        # add image to the processed list
        processed_files.append(file_name)

        print(file_name + " processed!")
        

    print("Finished!")
    end = time.time()
    print("Time elapsed: " + str(end - start) + " seconds . . .")


def load_images():

    # load all files
    all_files = os.listdir(ct_dir)

    # get OB images
    global ob_files
    ob_files = list(filter(lambda x: x.startswith(prefix_ob), all_files))

    # copy OB images
    for file in ob_files :
        source = os.path.join(ct_dir, file)
        target = os.path.join(output_dir, file)
        shutil.copyfile(source, target)

        # load images
        ob_imgs[file] = Image.open(target)
        ob_imgs_arr[file] = numpy.array(ob_imgs[file])

    # get DC images
    global dc_files
    dc_files += list(filter(lambda x: x.startswith(prefix_dc), all_files))

    # copy DC images
    for file in dc_files :
        source = os.path.join(ct_dir, file)
        target = os.path.join(output_dir, file)
        shutil.copyfile(source, target)

        # load images
        dc_imgs[file] = Image.open(target)
        dc_imgs_arr[file] = numpy.array(dc_imgs[file])

    # get projection images
    global ct_files
    ct_files += list(filter(lambda x: x.startswith(prefix_ct), all_files))

    for file in ct_files :
        source = os.path.join(ct_dir, file)

        # load images
        ct_imgs[file] = Image.open(source)
        ct_imgs_arr[file] = numpy.array(ct_imgs[file])

        # set numpy array template
        global array_temp
        array_temp = numpy.empty_like(ct_imgs_arr[file], dtype='uint16')


## calculates the average DC image as a numpy array from the dc samples
def get_dc_average():

    sum = array_temp
    sum *= 0

    for name, arr in dc_imgs_arr.items() :
        sum += arr

    global dc_avr
    dc_avr =  sum // len(dc_imgs_arr)   

    for name, arr in ct_imgs_arr.items() : 
        ct_imgs_arr_no_dc[name] = arr - dc_avr


## sums up and returns the renmants of the decayed afterimages in a numpy array
def decay():

    sum_decayed = array_temp
    sum_decayed *= 0

    img_count = len(processed_files)

    for idx, image_name in reversed(list(enumerate(processed_files))):
        # TODO: replace with actual decay function 
        # using an increasing index instead of a time based function 
        # sum_decayed += (ct_imgs_arr[image_name]) // (20 * (img_count - idx)) 
        sum_decayed += ct_imgs_arr_no_dc[image_name] // (3 * (img_count - idx)) 

    return sum_decayed

if __name__ == "__main__":
    main()