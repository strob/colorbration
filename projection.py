import cv2
import capture
import numpy

points = []
W, H = (800,600)
# W, H = (1920,1200)
mapto = [(0,0), (W,0), (W, H), (0, H)]

cv2.namedWindow("camera")
cv2.namedWindow("projector")

capt_orig = numpy.asarray(capture.capture())
scale = float(capt_orig.shape[1])/800
aspect = float(capt_orig.shape[1])/capt_orig.shape[0]
capt_scale = cv2.resize(capt_orig, (800, int(800/aspect)))
cv2.imshow("camera", capt_scale)

def addpoint(ev, x, y, button, flags):
    if ev == cv2.EVENT_LBUTTONDOWN:
        points.append((scale*x,scale*y))
        if len(points) > 4:
            points.pop(0)
        if len(points) == 4:
            M = cv2.getPerspectiveTransform(numpy.array(points).astype(numpy.float32),
                                            numpy.array(mapto).astype(numpy.float32))
            dest = cv2.warpPerspective(capt_orig, M, (W, H))
            cv2.imshow("projector", dest)
            cv2.waitKey(5)

        if len(points) > 1:
            capt = capt_scale.copy()
            cv2.polylines(capt, [(numpy.array(points + [points[0]])/scale).astype(numpy.int32)], False, (0, 255, 0))
            cv2.imshow("camera", capt)
            cv2.waitKey(5)

cv2.setMouseCallback("camera", addpoint)

while True:
    if cv2.waitKey( 100 ) == 27 : # escape
        break;
    