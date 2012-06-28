from projection import Correction
from pyramid_constraint import Pyramid, Constraint

import numpy
import cv2

class PyrCorrect(Correction):
    def __init__(self, **kw):
        Correction.__init__(self, **kw)
        #self.full_target = 50*numpy.ones((self.H, self.W, 3), dtype=numpy.uint8)

        self.set_pyr_level(7)

        cv2.namedWindow("error")
        cv2.namedWindow("correction")

    def set_pyr_level(self, level):
        self.pyr = Pyramid(level=level, size=(self.W, self.H))
        #self.target = self.pyr.down(self.full_target)

        self.measured = None
        self.d_measured = None

        self.error = None
        self.d_error = None

        self.constraint = Constraint(size=self.pyr.down_size())

    def filter(self, im):
        new_measured = self.pyr.down(im)
        if self.measured is not None:
            self.d_measured = new_measured - self.measured
        self.measured = new_measured

        return im               # apparent pass through (but with side effects)

    def correct(self, coeff=0.1):
        self.raw_transformed = self.filter(self.transformed)

        self.target = self.measured.mean() * numpy.ones(self.measured.shape, dtype=numpy.uint8)

        new_error = self.measured - self.target
        if self.error is not None:
            self.d_error = new_error - self.error
            total_d_error = numpy.sum(self.d_error)
            print 'change in error', total_d_error
        self.error = new_error
        cv2.imshow("error", 
                   cv2.resize(
                       (128 + 10*self.error).astype(numpy.uint8),
                       (400,300)))

        total_error = numpy.sum(numpy.abs(self.error))
        print 'total error', total_error

        self.d_correction = numpy.zeros(self.error.shape)
        constraint = self.constraint.next()
        self.d_correction[constraint] = coeff * self.error[constraint]
        cv2.imshow("correction", 
                   cv2.resize(
                       (128 + 50*self.d_correction).astype(numpy.uint8),
                       (400,300)))

        d_correction_full = self.pyr.up(self.d_correction.astype(numpy.uint8))

        self.correction[:] = (self.correction + d_correction_full).clip(0, 255)
        self.render_projector()

if __name__=='__main__':
    p = PyrCorrect(W=1920, H=1200, record = False)
    p.iterate()
    p.run()