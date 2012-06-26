import Image
import numpy

# 4x4cm
BOX_WIDTH = 600*2

# lines & checkerboard

def lines(width, density=0.5):
    period = width / density

    rem = period % 1.0
    print 'ERROR: %.2f%%' % (100*rem/period)

    period = int(period)

    out = numpy.zeros((BOX_WIDTH,BOX_WIDTH), dtype=numpy.bool)
    curx = 0
    while curx<BOX_WIDTH-width:
        out[:,curx:curx+width] = True
        curx += period
    return out

def grid(width, density=0.5):
    period = width * ((1 + numpy.sqrt(1-density))/density)

    rem = period % 1.0
    print 'ERROR: %.2f%%' % (100*rem/period)

    period = int(period)

    out = numpy.zeros((BOX_WIDTH,BOX_WIDTH), dtype=numpy.bool)
    curx = 0
    while curx<BOX_WIDTH-width:
        out[:,curx:curx+width] = True
        curx += period
    cury = 0
    while cury<BOX_WIDTH-width:
        out[cury:cury+width] = True
        cury += period
    return out

if __name__=='__main__':

    linewidth = int(raw_input("linewidth (int) >"))
    density = float(raw_input("density (float 0-1) >"))
    mode = globals()[raw_input("mode (lines | grid) >")]
    outfile = raw_input("filename >")

    im = Image.fromarray((255*mode(linewidth, density)).astype(numpy.uint8), mode='L')
    im.save(outfile)