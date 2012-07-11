import cv2
import numpy

multipliers = numpy.load('CALIBRATION.npy')

imgpath = raw_input("image to calibrate> ")
im = cv2.imread(imgpath, -1)

im *= multipliers

print im.shape, im.dtype, im.max()
cv2.imwrite(imgpath + '.calib.tif', im)#, -1)
