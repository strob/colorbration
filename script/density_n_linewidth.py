from grids_n_lines import grid, lines, BOX_WIDTH
import cairo
import pango
import pangocairo
import cv2
import numpy

LABEL_HEIGHT = BOX_WIDTH

def random(width, density):
    smw = BOX_WIDTH/width
    sm = numpy.zeros((smw, smw))
    npix = smw*smw
    nwht = density * npix
    print npix, nwht
    err = (nwht % 1) / npix
    print "ERROR: %.2f%%" % (100*err)
    nwht = int(nwht)
    sm.flat[:nwht] = 1
    numpy.random.shuffle(sm.reshape(numpy.product(sm.shape)))
    print sm.shape

    #resize to BOX WIDTH
    out = numpy.zeros((BOX_WIDTH, BOX_WIDTH), numpy.bool)
    idxes = numpy.linspace(0, smw-1, BOX_WIDTH).astype(int)
    out[:] = sm[idxes.reshape((-1,1)),idxes]
    return out


def label(txt, width=BOX_WIDTH, height=LABEL_HEIGHT):
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    ctx = pangocairo.CairoContext(cairo.Context(surface))

    ctx.set_source_rgb(255,255,255)
    ctx.rectangle(0,0,width,height)
    ctx.fill()

    ctx.set_source_rgb(0,0,0)

    font = pango.FontDescription()
    font.set_size(72 * pango.SCALE)
        
    layout = ctx.create_layout()
    layout.set_text(txt)
    layout.set_font_description(font)
    ctx.move_to(0, 0)
    ctx.show_layout(layout)

    return numpy.frombuffer(surface, numpy.uint8).reshape((height,width,-1))[:,:,:3]

def edge_weight(np):
    return numpy.sum(cv2.Laplacian(np, 8)) / float(numpy.product(np.shape))

if __name__=='__main__':
    # type, linewidth, density
    spec = [[grid, 5, 0.5],
            [lines, 5, 0.5],
            [random, 20, 0.5],
            [lines, 20, 0.5],
            [lines, 12, .1]]

    PAD = BOX_WIDTH/8

    out = 255*numpy.ones((len(spec)*BOX_WIDTH, 2*BOX_WIDTH+PAD,3), numpy.uint8)

    def _desc(lw, d, edges):
        return "%d%% white\nthickn.: %d\nedges: %.2f" % (d*100, lw, edges)

    for idx, (fn, linewidth, density) in enumerate(spec):
        y = idx * BOX_WIDTH
        out[y:y+BOX_WIDTH,:BOX_WIDTH] = 255*fn(linewidth, density).reshape((BOX_WIDTH,BOX_WIDTH,-1))
        weight = edge_weight(out[y:y+BOX_WIDTH,:BOX_WIDTH])
        out[y:y+BOX_WIDTH,BOX_WIDTH+PAD:] = label(_desc(linewidth, density, weight))

    cv2.imwrite('out.tif', out)