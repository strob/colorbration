import projection
import numpy
import cv2

class NewOutput(projection.Projection):
    def __init__(self, **kw):
        projection.Projection.__init__(self, **kw)
        self.correction = 255*numpy.zeros((self.H,self.W,3), dtype=numpy.uint8)

    def iterate(self):
        projection.Projection.iterate(self)
        self.render_projector()

    def filter(self, im):
        return cv2.blur(im[:,:,1].astype(numpy.uint8), (1,1))#im.mean(axis=2), (5,5))

    def correct(self, factor=None, target=None):
        pass

    def render_projector(self):
        cv2.imshow("projector", self.correction)
        cv2.waitKey(5)

    def run(self):
        while True:
            code = cv2.waitKey( 100 )
            if code == 27 : # escape
                break;
            elif code > 0 and code < 255:
                key = chr(code)
                if key == 'c':
                    self.calibrate()
                    import pickle
                    pickle.dump(self.points, open('calibration.pkl', 'w'))
                if key == 'l':
                    import pickle
                    self.points = pickle.load(open('calibration.pkl'))
                    self.draw_points()
                    self.calibrated = True
                if key == 'r':
                    self.loop()
                    break

    def loop(self):
        while True:
            code = cv2.waitKey( 100 )
            if code == 27 : # escape
                break;
            elif code > 0 and code < 255:
                key = chr(code)
                if key == 'i':
                    self.iterate()
                if key == 'o':
                    self.iterate()
                    self.correct()
                if key == 'c':
                    self.calibrate()
                    self.correction *= 0 # reset
                elif key == 's':
                    self.correct()
                elif key == 'm':
                    self.correct(5)
                elif key == 't':
                    self.correct(.1)
                elif key == 'r':
                    self.correction *= 0
                    self.render_projector()
                elif key == 'e':
                    self.show_error()

class Neutralize(NewOutput):
    def correct(self, factor=None, target=None):
        if not self.calibrated:
            return
        intensities = self.filter(self.transformed)
        if target is None:
            target = intensities.mean()
        error = intensities - target

        # if factor is None:
        #     factor = abs(error).mean()# / 5.0
        #     print 'error factor', factor, 'min', error.min(), 'max', error.max()
        factor = 1

        self.correction[:] = (self.correction - factor*error.reshape((self.H,self.W,1))).clip(0,255)
        self.render_projector()

    def converge(self):
        while True:
            self.iterate()
            self.correct()

if __name__=='__main__':
    n = Neutralize(W=1920, H=1200, record = True)
    n.iterate()
    n.run()