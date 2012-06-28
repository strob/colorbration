import projection
import numpy
import cv2

class Neutralize(projection.Correction):
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
        #self.correction = cv2.blur(self.correction, (30,30))
        self.render_projector()

    def converge(self):
        while True:
            self.iterate()
            self.correct()

if __name__=='__main__':
    n = Neutralize(W=1920, H=1200, record = True)
    n.iterate()
    n.run()