import cv2
import numpy

class Pyramid:
    "gaussian pyramid de- and re-construction"
    def __init__(self, level=7, size=(1920,1200)):
        self.level = level
        self.size = size

    def down(self, im):
        "reduce `im' to self.level"
        for iteration in range(self.level):
            im = cv2.pyrDown(im)
        return im

    def up(self, im):
        "assume `im' is at self.level & restore"
        for level in reversed(range(self.level)):
            # make sure we get back to the original size exactly
            divisor = float(pow(2, level))
            w = int(numpy.ceil(self.size[0] / divisor))
            h = int(numpy.ceil(self.size[1] / divisor))
            z = numpy.zeros((h,w,3), dtype=numpy.uint8)
            cv2.pyrUp(im, z, (w,h))
            im = z
        return im

class Constraint:
    "constraint generation & iteration s.t. no pixel has two ``on'' edges"
    def __init__(self, size=(15,10)):
        self.size = size

        self._modidx = 0

    def next(self):
        "return a constraint that should limit deltaCorrection"

        c = numpy.zeros((self.size[1], self.size[0]), dtype=numpy.bool)
        for idx in range(self.size[1]):
            i = (2*idx + self._modidx) % 5
            c[idx,i::5] = True

        self._modidx = (self._modidx + 1) % 5

        return c