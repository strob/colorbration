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

def lines(linewidth, density=0.5):
    lineperiod = linewidth / density
    out = numpy.zeros((BOX_WIDTH,BOX_WIDTH), dtype=numpy.bool)
    curx = 0
    while curx<BOX_WIDTH-linewidth:
        out[:,curx:curx+linewidth] = True
        curx += lineperiod
    return out

def grid(linewidth, density=0.5):
    lineperiod = linewidth * ((1 + numpy.sqrt(1-density))/density)
    print lineperiod
    out = numpy.ones((BOX_WIDTH,BOX_WIDTH), dtype=numpy.bool)
    curx = 0
    while curx<BOX_WIDTH-linewidth:
        out[:,int(curx):int(curx)+linewidth] = False
        curx += lineperiod
    cury = 0
    while cury<BOX_WIDTH-linewidth:
        out[int(cury):int(cury)+linewidth] = False
        cury += lineperiod
    return out

a4 = numpy.zeros((HEIGHT,WIDTH), numpy.bool)
fns = [lines, grid]

for l_idx,numlines in enumerate(numpy.arange(1,9)*10):

    cury = (l_idx % 4)*(BOX_WIDTH+PADDING)

    for f_idx, fn in enumerate(fns):

        curx = int(l_idx / 4 + 2*f_idx)*(BOX_WIDTH+PADDING)

        linewidth = BOX_WIDTH/float(2*numlines)
        print linewidth

        a4[int(cury):int(cury)+BOX_WIDTH,int(curx):int(curx)+BOX_WIDTH] = fn(linewidth)


im = Image.fromarray((255*a4).astype(numpy.uint8), mode='L')
im.save('calib.tif')