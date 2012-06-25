import Image
import numpy

# A4: 11.7 x 8.3 in
# 8.1x8.1

WIDTH = 600*8.1
HEIGHT= 600*8.1
PADDING=.1/4

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

    out = numpy.ones((BOX_WIDTH,BOX_WIDTH), dtype=numpy.bool)
    curx = 0
    while curx<BOX_WIDTH-width:
        out[:,curx:curx+width] = False
        curx += period
    cury = 0
    while cury<BOX_WIDTH-width:
        out[cury:cury+width] = False
        cury += period
    return out

a4 = numpy.zeros((HEIGHT,WIDTH), numpy.bool)
fns = [lines, grid]

linewidths = [5,10,15,20,30,40,50,60]

for l_idx,linewidth in enumerate(linewidths):
    print linewidth

    cury = (l_idx % 4)*(BOX_WIDTH+PADDING)

    for f_idx, fn in enumerate(fns):

        curx = int(l_idx / 4 + 2*f_idx)*(BOX_WIDTH+PADDING)

        # linewidth = BOX_WIDTH/float(2*numlines)
        # print linewidth

        a4[int(cury):int(cury)+BOX_WIDTH,int(curx):int(curx)+BOX_WIDTH] = fn(linewidth)


im = Image.fromarray((255*a4).astype(numpy.uint8), mode='L')
im.save('calib2.tif')