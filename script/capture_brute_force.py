from capture import captureJPG as capture
import numpy
import cv2
import time

W,H = (1920,1200)

cv2.namedWindow("brute")
out = numpy.ones((H,W,3), numpy.uint8)

cv2.imshow("brute", out)
cv2.waitKey(5)

cv2.waitKey()
cv2.waitKey()
cv2.waitKey()

for i in range(0,255,5):
    show = out * i
    cv2.imshow("brute", show)
    cv2.waitKey(5)

    im = capture()
    im.save('brute-%d.png' % (i))
    cv2.waitKey(5)