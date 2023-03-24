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

decayed_images = {}
images_as_Array = {}
images_decayed = {}

images_processed = []

# TODO: pass as command line arguments
fileprefix = 'wood_'
ct_dir = 'C:\\Users\\Jonathan Schaffner\\FHNW_Projct\\IP5\\SampleData\\Wood\\projections'
output_base_dir = 'C:\\Users\Jonathan Schaffner\\FHNW_Projct\\IP5\\GeneratedData'
image_interval_ms = 50


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(os.path.join(output_base_dir, 'AddDecay', timestamp))
    output_decayed = Path(os.path.join(output_dir, 'Decay'))
    output_dir.mkdir(parents=True)
    output_decayed.mkdir(parents=True)

    # get DC and OB images
    files = os.listdir(ct_dir)
    files = list(filter(lambda x: x.startswith(fileprefix) == False, files))

    # copy DC and OB images
    for file in files :
        source = os.path.join(ct_dir, file)
        target = os.path.join(output_dir, file)
        shutil.copyfile(source, target)


    # get projection images
    files = os.listdir(ct_dir)
    files = list(filter(lambda x: x.startswith(fileprefix), files))
    images = {}

    # iterate through projections
    for idx, file_name in enumerate(files) :

        # open projection image
        raw_img = Image.open(os.path.join(ct_dir, file_name))

        # get tiffinfo from current image
        info = raw_img.tag_v2

        # images as raw array
        images_as_Array[file_name] = numpy.array(raw_img)

        # all previously decayed images summed up
        decayed_array = decay(images_as_Array[file_name])
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


def decay(imgArray):

    sum_decayed = imgArray * 0

    img_count = len(images_processed)

    for idx, image_name in reversed(list(enumerate(images_processed))):
        # TODO: replace with actual decay function 
        # using an increasing index instead of a function 
        sum_decayed += images_as_Array[image_name] // (5 * (img_count - idx)) 
    return sum_decayed


if __name__ == "__main__":
    main()