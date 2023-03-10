__version__ = '0.1.0'

import os
import numpy

from PIL import Image

from pathlib import Path
from datetime import datetime

decayed_images = {}
images_as_Array = {}
images_decayed = {}

images_processed = []

def decay(idx, imgArray):    
    print(idx)

    sum_decayed = imgArray * 0

    for image_name in images_processed:
        # TODO: replace with actual decay function
        sum_decayed += imgArray // (2 * idx)
        print(image_name)
    
    return sum_decayed

# TODO: pass as command line arguments
fileprefix = 'ct5s_0000'
ct_dir = 'C:\\Users\\Jonathan Schaffner\\FHNW_Projct\MuhRec\\SampleData\\04_ct5s375'
output_base_dir = 'C:\Users\Jonathan Schaffner\FHNW_Projct\MuhRec\GeneratedData'
image_interval_ms = 50

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(os.path.join(output_base_dir, 'AddRecursiveDecay', timestamp))
output_dir.mkdir(parents=True)

files = os.listdir(ct_dir)
files = list(filter(lambda x: x.startswith(fileprefix), files))
images = {}


for idx, file in enumerate(files) :
    images[file] = Image.open(os.path.join(ct_dir, file))
    decayed_images[file] = {}

    # images as raw array
    images_as_Array[file] = numpy.array(images[file])

    images_decayed[file] = decay(idx, images_as_Array[file])

    img = Image.fromarray(images_decayed[file])

    images_processed.append(file)
    img.save(os.path.join(output_dir, file),format='TIFF')

print("Finished!")