from projection import Correction
from pyramid_constraint import Pyramid, Constraint
import numpy
import cv2

class PyrCorrect(Correction):
    def __init__(self, **kw):
        Correction.__init__(self, **kw)
        #self.full_target = 50*numpy.ones((self.H, self.W, 3), dtype=numpy.uint8)
        self.set_pyr_level(7)

        self.coeff = 0.5

        cv2.namedWindow("error")
        cv2.namedWindow("correction")

        cv2.createTrackbar("coeff", "correction", 5, 100, lambda x: self.set_coeff(x/10.0))
        cv2.createTrackbar("pyr level", "correction", 7, 10, self.set_pyr_level)

    def set_coeff(self, newval):
        self.uncorrect()
        self.coeff = newval
        self.correct()

    def onkey(self, key):
        Correction.onkey(self, key)
        if key == 'p':
            self.constraint.next()
            self.p_correction = None
            if key == 'a':
                for i in range(5):
                    self.constraint.next()
                    self.p_correction = None

    def set_pyr_level(self, level):
        self.pyr = Pyramid(level=level, size=(self.W, self.H))
        #self.target = self.pyr.down(self.full_target)

        self.measured = None
        self.d_measured = None

        self.error = None
        self.d_error = None

        self.p_correction = None
        self.d_correction = None

        self.errorlog = []

        self.constraint = Constraint(size=self.pyr.down_size())

    def filter(self, im):
        im = im.mean(axis=2).astype(numpy.uint8) # grayscale

        new_measured = self.pyr.down(im)
        if self.measured is not None:
            self.d_measured = new_measured - self.measured
        self.measured = new_measured

        return im

    def get_error(self):
        new_error = self.measured - self.target
        if self.error is not None:
            self.d_error = new_error - self.error
            total_d_error = numpy.sum(self.d_error)
            print 'change in error', total_d_error
        return new_error

    def get_target(self):
        return self.measured.mean().clip(50,200) * numpy.ones(self.measured.shape, dtype=numpy.uint8)        

    def update_level(self):
        # total_error = numpy.sum(numpy.abs(self.error))
        # maxerr = numpy.abs(self.error).max()
        # self.errorlog.append(total_error)
        # print 'total error', total_error, 'max_error', maxerr

        # if len(self.errorlog) > 5:
        #     print 'errorlog', self.errorlog
        #     if self.errorlog[-1] >= 1.05*self.errorlog[-2]:
        #         print 'increase in error -- going back'
        #         return self.pyr.level + 1
        #     elif self.errorlog[-1] >= 0.95*self.errorlog[-2]:
        #         print 'pretty good! moving on'
        #         return self.pyr.level - 1
        pass

    def get_correction(self):
        self.p_d_correction = self.d_correction
        self.d_correction = numpy.zeros(self.error.shape)
        constraint = self.constraint.next()
        self.d_correction[constraint] = - self.error[constraint]

        # # normalize
        # self.d_correction *= 128 / max(1, abs(self.d_correction).max())

        self.d_correction = (self.d_correction.astype(int) * self.coeff).clip(-128,127)

        # center on 128 & convert to uint
        self.d_correction += 128
        self.d_correction = self.d_correction.astype(numpy.uint8)

        d_correction_full = self.pyr.up(self.d_correction)

        return (self.correction.astype(int) + d_correction_full.reshape((self.correction.shape[0], self.correction.shape[1], -1)) - 128).clip(0, 255).astype(numpy.uint8)


    def correct(self):
        self.raw_transformed = self.filter(self.transformed)
        self.target = self.get_target()
        self.error = self.get_error()

        cv2.imshow("error", 
                   cv2.resize(self.error, (400,300)))

        newlevel = self.update_level()
        if newlevel is not None:
            self.set_pyr_level(newlevel)
            return self.correct()

        self.p_correction = self.correction
        self.correction = self.get_correction()

        cv2.imshow("correction",
                   cv2.resize(self.d_correction,
                              (400,300)))

        self.render_projector()

    def uncorrect(self):
        self.constraint.prev()
        if self.p_correction is not None:
            self.correction = self.p_correction
            self.render_projector()

if __name__=='__main__':
    p = PyrCorrect(W=1920, H=1200, record = True)
    # p = PyrCorrect(W=600, H=400, record = True)
    p.iterate()
    p.run()