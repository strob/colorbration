import cv2
from capture import captureJPG as capture
import numpy
import Image

def get_diff_rect(low, high):
    # try to find edges automatically
    diff = (255*((high - low) > 40)).astype(numpy.uint8)
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

class Projection:
    def __init__(self, W=800,H=600,record=False):
        self.points = []
        self.W, self.H = (W, H)
        self.mapto = [(0,0), (W,0), (W, H), (0, H)]
        self.transformed = 255*numpy.zeros((H,W,3), numpy.uint8)
        self.calibrated = False
        self.recording = record
        self.idx = 0

        cv2.namedWindow("camera")
        cv2.namedWindow("projector")

    def iterate(self):
        im = capture()
        self.capt_orig = numpy.asarray(im)

        if len(self.points) == 0:
            CH, CW, _cd = self.capt_orig.shape
            self.points = [(0,0), (CW,0), (CW,CH), (0,CH)]

        self.scale = float(self.capt_orig.shape[1])/800
        aspect = float(self.capt_orig.shape[1])/self.capt_orig.shape[0]
        self.capt_scale = cv2.resize(self.capt_orig, (800, int(800/aspect)))

        self.transform()
        if self.recording:
            im = Image.fromarray(self.transformed, mode='RGB')
            im.save('rec-%06d.png' % (self.idx))
            self.idx += 1

        self.render_camera()
        self.render_projector()

    def calibrate(self):
        off = numpy.zeros((self.H,self.W,3), dtype=numpy.uint8)
        cv2.imshow("projector", off)
        cv2.waitKey(100)
        self.minimums = cv2.blur(numpy.asarray(capture()).mean(axis=2), (1,1))

        on = 255*numpy.ones((self.H,self.W,3), dtype=numpy.uint8)
        cv2.imshow("projector", on)
        cv2.waitKey(100)
        cv2.waitKey(100)
        self.maximums = cv2.blur(numpy.asarray(capture()).mean(axis=2), (1,1))

        self.points = get_diff_rect(self.minimums, self.maximums)
        self.draw_points()

        self.calibrated = True

    def render_camera(self):
        self.draw_points()

    def transform(self):
        M = cv2.getPerspectiveTransform(numpy.array(self.points).astype(numpy.float32),
                                        numpy.array(self.mapto).astype(numpy.float32))
        cv2.warpPerspective(self.capt_orig, M, (self.W, self.H), self.transformed)

    def show_error(self):
        heatmap = numpy.zeros((self.H,self.W,3), dtype=numpy.uint8)
        intensities = self.transformed.mean(axis=2)
        heatmap[:,:,0][intensities > 128] = 2*(intensities[intensities > 128] - 128)
        heatmap[:,:,2][intensities < 128] = 2*(128 - intensities[intensities < 128])
        cv2.imshow("projector", heatmap)
        cv2.waitKey(100)

    def render_projector(self):
        self.show_error()

    def draw_points(self):
        csp = self.capt_scale.copy()
        csp[:,:,0] = csp[:,:,1] # only show Y value
        csp[:,:,2] = csp[:,:,1]

        for pt in self.points:
            cv2.circle(csp, (int(pt[0]/self.scale), int(pt[1]/self.scale)), 5, (0,255,0))

        pts = self.points + [self.points[0]]

        if len(pts) > 1:
            cv2.polylines(csp, [(numpy.array(pts)/self.scale).astype(numpy.int32)], False, (0, 255, 0))
        cv2.imshow("camera", csp)
        cv2.waitKey(5)

class Correction(Projection):
    def __init__(self, **kw):
        Projection.__init__(self, **kw)
        self.gen_correction()
    def gen_correction(self):
        #self.correction = (255*numpy.random.random((self.H,self.W,3))).astype(numpy.uint8)
        self.correction = numpy.zeros((self.H,self.W,3)).astype(numpy.uint8)
    def calibrate(self):
        Projection.calibrate(self)
        self.gen_correction()
        self.render_projector()

    def iterate(self):
        Projection.iterate(self)
        self.render_projector()

    def filter(self, im):
        return cv2.blur(im.mean(axis=2), (5,5))

    def correct(self, factor=None, target=None):
        pass

    def render_projector(self):
        cv2.imshow("projector", self.correction)
        cv2.waitKey(5)

    def converge(self):
        while True:
            self.iterate()
            self.correct()

    def run(self):
        while True:
            code = cv2.waitKey( 100 )
            if code == 27 : # escape
                break;
            elif code > 0 and code < 255:
                key = chr(code)
                self.onkey(key)

    def onkey(self, key):
        if key == 'c':
            self.calibrate()
            import pickle
            pickle.dump(self.points, open('calibration.pkl', 'w'))
        elif key == 'l':
            import pickle
            self.points = pickle.load(open('calibration.pkl'))
            self.draw_points()
            self.calibrated = True
        elif key == 'i':
            self.iterate()
        elif key == 'o':
            self.iterate()
            self.correct()
        elif key == 'w':
            self.converge()
        elif key == 's':
            self.correct()
        elif key == 'r':
            self.correction *= 0
            self.render_projector()


if __name__=='__main__':
    p = Projection(W=1920, H=1200)
    p.iterate()
    while True:
        code = cv2.waitKey( 100 )
        if code == 27 : # escape
            break;
        elif code > 0 and code < 255:
            key = chr(code)
            if key == 'c':
                p.calibrate()
            if key == 'i':
                p.iterate()