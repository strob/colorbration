import numpy
from random import choice as randomchoice
import cv2

import grids_n_lines
import density_n_linewidth

def csvnorm(csvpath):
    "; -> ,"
    f = open(csvpath).read()
    if ';' in f:
        # who can work with the french ...
        f = f.replace(',', '.')
        f = f.replace(';', ',')
    return f.strip().split('\n')

def get_density(measured, lightest=1, darkest=0):
    return darkest + (1.0 - measured) * (lightest - darkest) # naive

def fail(msg):
    print msg
    import pdb; pdb.set_trace()
    import sys; sys.exit(1)


if __name__=='__main__':
    import csv

    def rawdefault(prompt, fn, default):
        x = raw_input(prompt + '[' + default + '] $ ')
        if x == 'prompt':
            import pdb; pdb.set_trace()
        if len(x) > 0:
            try:
                return fn(x)
            except:
                print 'invalid input'
                return rawdefault(prompt, fn, default)
        return fn(default)

    grid = grids_n_lines.grid
    lines = grids_n_lines.lines
    random = density_n_linewidth.random
    randomfn = lambda x,y,**kw: randomchoice([grid,lines,random])(x,y,**kw)

    DPI = rawdefault("DPI", int, "600")
    w_cm = rawdefault("Poster width in CM", float, "91.0")
    width = w_cm / 2.54
    w_pixels = int(width*DPI)

    csvpath = rawdefault("Path to CSV", str, "grid.csv")
    data = [x for x in csv.reader(csvnorm(csvpath))]
    data = [numpy.array([float(c) for c in r]) for r in data]
    data = numpy.array(data)
    if data.min() < 0 or data.max() > 1:
        fail('values not normalized')

    rot90 = rawdefault("Rotate 90 degrees?", bool, "")
    if rot90:
        print "rotating 90 degrees"
        data = numpy.rot90(data)

    BW = int(w_pixels / len(data[0]))

    h_pixels = BW * len(data)

    print 'new %dx%d poster to be generated' % (w_pixels, h_pixels)

    linewidth = rawdefault("Line width in pixels", int, "20")
    fn = rawdefault("Dithering method (grid|lines|random|randomfn)", eval, "randomfn")

    out = 255*numpy.ones((h_pixels, w_pixels), dtype=numpy.uint8)
    for r in range(len(data)):
        for c in range(len(data[0])):
            print r,c,data[r][c]
            out[r*BW:(r+1)*BW, c*BW:(c+1)*BW] = 255*fn(linewidth, data[r,c], box_width=BW)

    cv2.imwrite('poster.tif', out)