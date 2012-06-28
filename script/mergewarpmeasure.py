import numpy
import cv2

# XXX: much code lifted from ../projection.py -- refactor into a util.py?

def get_diff_rect(diff):
    # try to find edges automatically
    contours, _h = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # assume that the contour with the largest area is our projection
    area = numpy.array([cv2.contourArea(X) for X in contours])

    print '%d contours, mean %.2f, max %d' % (len(area), area.mean(), area.max())
    contour = contours[area.argmax()].reshape(-1,2)
        
    # to approximate a polygon, first we find a bounding rect, and
    # then take the points closest to each edge.
    
    # XXX: proper camera/projector (combined?) calibration would be nice
    # http://opencv.itseez.com/doc/tutorials/calib3d/camera_calibration/camera_calibration.html

    bx0 = contour[:,0].min()
    bx1 = contour[:,0].max()
    
    by0 = contour[:,1].min()
    by1 = contour[:,1].max()

    def closest(x,y):
        dist = abs(contour - [x,y]).mean(axis=1) # xxx: euclidian
        return contour[dist.argmin()]

    return [closest(bx0,by0), closest(bx1,by0), closest(bx1,by1), closest(bx0,by1)]

def transform(src, points, mapto, size):
    M = cv2.getPerspectiveTransform(numpy.array(points).astype(numpy.float32),
                                    numpy.array(mapto).astype(numpy.float32))
    return cv2.warpPerspective(src, M, size)

if __name__=='__main__':
    import sys

    IM = None
    ACC = None
    WRPS = []
    PTS = []
    SCALE = 5
    THRESHOLD = 60
    GRID = (49,24)
    SIZE = (GRID[0]*20, GRID[1]*20)
    MAPTO = [(0,0), (SIZE[0], 0), (SIZE[0], SIZE[1]), (0, SIZE[1])]

    cv2.namedWindow("image")
    cv2.namedWindow("merged")

    def preview():
        im_preview = cv2.resize(IM, (IM.shape[1]/SCALE, IM.shape[0]/SCALE))
        pts_preview = [(numpy.array(PTS + [PTS[0]]) / SCALE).astype(numpy.int32)]
        cv2.polylines(im_preview, pts_preview, False, (0, 255, 0))
        cv2.imshow("image", im_preview)
    def preview_acc():
        acc = (ACC / float(len(WRPS))).astype(numpy.uint8)
        acc_preview = cv2.resize(acc, (IM.shape[1]/SCALE, IM.shape[0]/SCALE))
        cv2.imshow("merged", acc_preview)

    def compute():
        global PTS
        bw = cv2.blur(IM.mean(axis=2), (5,5))
        diff = 255 * (bw > THRESHOLD).astype(numpy.uint8)
        PTS = get_diff_rect(diff)
        preview()

    def dotransform():
        print 'warp', 'transform(',IM.shape, IM.dtype, PTS, MAPTO, SIZE
        warp = transform(IM, PTS, MAPTO, SIZE)
        return warp

    def setthreshold(val):
        global THRESHOLD
        THRESHOLD = val
        compute()

    def save():
        # normalize
        acc = ACC - ACC.min()
        acc = 255.0 * (acc.astype(numpy.float32) / ACC.max())

        print 'ACC', acc.min(), acc.max(), acc.dtype

        # acc = acc.astype(numpy.float32)
        grid = cv2.resize(acc, GRID, interpolation=cv2.INTER_AREA)
        # XXX: -> XYZ (?)

        grid = grid.mean(axis=2)
        # renormalize
        grid = grid - grid.min()
        grid /= grid.max()

        import csv
        writer = csv.writer(open('grid.csv', 'w'), delimiter=';')
        writer.writerows(grid.tolist())

        print 'saved to `grid.csv`'

    def tweak(ev, x, y, button, flags):
        if ev == cv2.EVENT_LBUTTONDOWN:
            pt = [SCALE*x, SCALE*y]
            # replace closest
            # XXX: use hypot!
            dists = (abs(numpy.array(PTS) - pt)).mean(axis=1)
            PTS[dists.argmin()] = pt
            preview()

    cv2.createTrackbar("threshold", "image", THRESHOLD, 255, setthreshold)
    cv2.setMouseCallback("image", tweak)
    for path in sys.argv[1:]:
        IM = cv2.imread(path)
        compute()
        while True:
            k = cv2.waitKey(100)
            if k == 27:
                import sys
                sys.exit(1)
            elif k>0 and k<255:
                key = chr(k)
                if key == 'y':
                    warp = dotransform()
                    WRPS.append(warp)
                    if ACC is None:
                        ACC = warp.astype(int)
                    else:
                        ACC += warp
                    preview_acc()
                    break
                elif key == 'n':
                    print 'skipping this image'
                    break
                elif key == 's':
                    save()
    # save results
    save()