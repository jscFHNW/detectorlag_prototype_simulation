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


def decay(seqNum, imgArray):

    sum_decayed = imgArray * 0

    img_count = len(images_processed)

    for idx, image_name in reversed(list(enumerate(images_processed))):
        # TODO: replace with actual decay function using an increasing index instead of a function 
        sum_decayed += images_as_Array[image_name] // (10 * (img_count - idx)) 
    return sum_decayed

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(os.path.join(output_base_dir, 'AddRecursiveDecay', timestamp))
output_decayed = Path(os.path.join(output_dir, 'Decay'))
output_dir.mkdir(parents=True)
output_decayed.mkdir(parents=True)

files = os.listdir(ct_dir)
files = list(filter(lambda x: x.startswith(fileprefix), files))
images = {}

#file = "wood_000.tif"

for idx, file_name in enumerate(files) :
#for idx in range (1,10):
    #print(file)
    raw_img = Image.open(os.path.join(ct_dir, file_name))

    # images as raw array
    images_as_Array[file_name] = numpy.array(raw_img)

    decayed_array = decay(idx, images_as_Array[file_name])
    img_decayed = Image.fromarray(decayed_array)
    img_added = Image.fromarray(decayed_array + images_as_Array[file_name])

    img_decayed.save(os.path.join(output_decayed, "decay_" + str(idx).zfill(4) + ".tif"), format='TIFF')
    img_added.save(os.path.join(output_dir, "added_" + str(idx).zfill(4) + ".tif"), format='TIFF')
    #raw_img.save(os.path.join(output_dir, "raw_" + str(idx).zfill(4) + ".tif"), format='TIFF')

    print(file_name + " processed!")

    images_processed.append(file_name)

files = os.listdir(ct_dir)
files = list(filter(lambda x: x.startswith(fileprefix) == False, files))

# for file in files :
#     source = os.path.join(ct_dir, file)
#     target = os.path.join(output_dir, file)
#     shutil.copyfile(source, target)

print("Finished!")
end = time.time()
print("Time elapsed: " + str(end - start) + " seconds . . .")