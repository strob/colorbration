import cv2
import numpy

imgpath = raw_input("calibration image> ")
im = cv2.imread(imgpath, -1) # load as-is: this allows for 16-bit images to import correctly

target = im.mean(axis=0).mean(axis=0)

multipliers = target / im

# don't lose data
multipliers[multipliers==0] = 1
multipliers[multipliers==numpy.inf] = 1

numpy.save('CALIBRATION.npy', multipliers)
