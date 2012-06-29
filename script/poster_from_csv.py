import numpy
from random import choice as randomchoice
import cv2

import grids_n_lines
import density_n_linewidth

def get_density(measured):
    return 1.0 - measured       # naive

if __name__=='__main__':
    import csv

    def rawdefault(prompt, fn, default):
        x = raw_input(prompt + '[' + default + '] $ ')
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
    width = rawdefault("Poster width in inches", float, "91.0")
    w_pixels = int(width*DPI)

    csvpath = rawdefault("Path to CSV", str, "grid.csv")
    data = [x for x in csv.reader(open(csvpath))]#, delimiter=";")]
    data = [[float(c) for c in r] for r in data]

    # normalize data between 0 and 1
    data = numpy.array(data)
    data -= data.min()
    data /= data.max()

    BW = int(w_pixels / len(data[0]))

    h_pixels = BW * len(data)

    print 'new %dx%d poster to be generated' % (w_pixels, h_pixels)

    linewidth = rawdefault("Line width in pixels", int, "20")
    fn = rawdefault("Dithering method (grid|lines|random|randomfn)", eval, "randomfn")

    out = 255*numpy.ones((h_pixels, w_pixels), dtype=numpy.uint8)
    for r in range(len(data)):
        for c in range(len(data[0])):
            print r,c,data[r][c]
            out[r*BW:(r+1)*BW, c*BW:(c+1)*BW] = 255*fn(linewidth, get_density(float(data[r][c])), box_width=BW)

    cv2.imwrite('poster.tif', out)