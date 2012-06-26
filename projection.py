import cv2
import capture
import numpy

class Projection:
    def __init__(self, W=800,H=600):
        self.points = []
        self.W, self.H = (W, H)
        self.mapto = [(0,0), (W,0), (W, H), (0, H)]

        cv2.namedWindow("camera")
        cv2.namedWindow("projector")

        cv2.setMouseCallback("camera", self._addpoint)

    def iterate(self):
        self.capt_orig = numpy.asarray(capture.capture())
        self.scale = float(self.capt_orig.shape[1])/800
        aspect = float(self.capt_orig.shape[1])/self.capt_orig.shape[0]
        self.capt_scale = cv2.resize(self.capt_orig, (800, int(800/aspect)))
        self.draw_points()

    def draw_points(self):
        csp = self.capt_scale.copy()

        for pt in self.points:
            cv2.circle(csp, (int(pt[0]/self.scale), int(pt[1]/self.scale)), 5, (0,255,0))

        if len(self.points) == 4:
            pts = self.points + [self.points[0]]
            
        else:
            pts = self.points

        if len(pts) > 1:
            cv2.polylines(csp, [(numpy.array(pts)/self.scale).astype(numpy.int32)], False, (0, 255, 0))
        cv2.imshow("camera", csp)
        cv2.waitKey(5)
        
    def _addpoint(self, ev, x, y, button, flags):
        if ev == cv2.EVENT_LBUTTONDOWN:
            pt = [self.scale*x, self.scale*y]
            if len(self.points) < 4:
                self.points.append(pt)
            else:
                # replace closest
                dists = (abs(numpy.array(self.points) - pt)).mean(axis=1)
                self.points[dists.argmin()] = pt
            self.draw_points()

            if len(self.points) == 4:
                M = cv2.getPerspectiveTransform(numpy.array(self.points).astype(numpy.float32),
                                            numpy.array(self.mapto).astype(numpy.float32))
                dest = cv2.warpPerspective(self.capt_orig, M, (self.W, self.H))
                cv2.imshow("projector", dest)
                cv2.waitKey(5)

if __name__=='__main__':
    p = Projection()
    p.iterate()
    while True:
        if cv2.waitKey( 100 ) == 27 : # escape
            break;
    