import Image
import csv

def imgToCSV(imgpath, csvpath):
    im = Image.open(imgpath)
    writer = csv.writer(open(csvpath, 'w'))

    for row in range(im.size[1]):
        writer.writerow(reduce(lambda x,y: x+list(im.getpixel((y,row))), range(im.size[0]), []))

if __name__=='__main__':
    import sys
    for p in sys.argv[1:]:
        imgToCSV(p, p + '.csv')