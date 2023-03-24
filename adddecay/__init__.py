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

# images as PIL objects
ct_imgs = {}
ob_imgs = {}
dc_imgs = {}

# images as PIL objects
ct_imgs_arr = {}
ob_imgs_arr = {}
dc_imgs_arr = {}

# average of all the DC samples as a numpy array
dc_avr = []

imgs_processed = []

def main():    

    load_images()  

    dc_avr = get_dc_average();  

    # iterate through projections
    for idx, img in enumerate(ct_imgs) :

        # open projection image
        #img = Image.open(os.path.join(ct_dir, file_name))

        # get tiffinfo from current image
        info = img.tag_v2

        # images as raw array
        #images_as_Array[file_name] = numpy.array(raw_img)

        # all previously decayed images summed up
        decayed_array = decay()
        img_decayed = Image.fromarray(decayed_array)

        # add decay to current image
        img_added = Image.fromarray(images_as_Array[file_name] + decayed_array)

        # save images with tiffinfo from original image to preserve metadata
        img_decayed.save(os.path.join(output_decayed, "decay_" + str(idx).zfill(4) + ".tif"), format='TIFF', tiffinfo=info)
        img_added.save(os.path.join(output_dir, "added_" + str(idx).zfill(4) + ".tif"), format='TIFF', tiffinfo=info)

        # add image to the processed list
        images_processed.append(file_name)

        print(file_name + " processed!")
        

    print("Finished!")
    end = time.time()
    print("Time elapsed: " + str(end - start) + " seconds . . .")


def load_images():

    # load all files
    all_files = os.listdir(ct_dir)

    # get OB images
    ob_files = list(filter(lambda x: x.startswith(prefix_ob) == False, all_files))

    # copy OB images
    for file in ob_files :
        source = os.path.join(ct_dir, file)
        target = os.path.join(output_dir, file)
        shutil.copyfile(source, target)

        # load images
        ob_imgs[file] = Image.open(os.path.join(output_dir, file))

    # get DC images
    dc_files = list(filter(lambda x: x.startswith(prefix_dc) == False, all_files))

    # copy DC images
    for file in dc_files :
        source = os.path.join(ct_dir, file)
        target = os.path.join(output_dir, file)
        shutil.copyfile(source, target)

        # load images
        dc_imgs[file] = Image.open(os.path.join(output_dir, file))
        dc_imgs_arr[file] = numpy.array(dc_imgs[file])

    # get projection images
    ct_files = list(filter(lambda x: x.startswith(prefix_ct), all_files))

    for file in ct_files :
        source = os.path.join(ct_dir, file)

        # load images
        ct_imgs[file] = Image.open(os.path.join(source, file))
        ct_imgs_arr[file] = numpy.array(dc_imgs[file])


def get_dc_average():

    sum = []

    for img_arr in dc_imgs_arr :
        sum += img_arr

    return sum / len(dc_imgs_arr)


def decay(imgArray):

    sum_decayed = imgArray * 0

    img_count = len(imgs_processed)

    for idx, image_name in reversed(list(enumerate(imgs_processed))):
        # TODO: replace with actual decay function 
        # using an increasing index instead of a function 
        # subtract dc_avr from image
        sum_decayed += (ct_imgs_arr[image_name] - dc_avr) // (5 * (img_count - idx)) 
        
    return sum_decayed


if __name__ == "__main__":
    main()