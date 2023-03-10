__version__ = '0.1.0'

import os
import numpy

from PIL import Image

from pathlib import Path
from datetime import datetime


# TODO: pass as command line arguments
fileprefix = 'ct5s_0000'
ct_dir = 'C:\\Users\\Jonathan Schaffner\\FHNW_Projct\MuhRec\\SampleData\\04_ct5s375'
output_base_dir = 'C:\\Users\\Jonathan Schaffner\\FHNW_Projct\MuhRec\GeneratedData'

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(os.path.join(output_base_dir, 'AddRecursiveDecay', timestamp))
output_dir.mkdir(parents=True)

files = os.listdir(ct_dir)
files = list(filter(lambda x: x.startswith(fileprefix), files))
images = {}
imagesAsArray = {}

for file in files :
    images[file] = Image.open(os.path.join(ct_dir, file))

    # images as raw array
    imagesAsArray[file] = numpy.array(images[file])

print(images)
print(imagesAsArray)