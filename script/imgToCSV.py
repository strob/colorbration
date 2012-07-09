import cv2
import csv
import numpy

def imgToCSV(imgpath, csvpath):
    im = cv2.imread(imgpath, -1) # load as-is: this allows for 16-bit images to import correctly
    writer = csv.writer(open(csvpath, 'w'), delimiter=';')

    for row in im:
        writer.writerow(numpy.concatenate(row).tolist())

if __name__=='__main__':
    import sys
    for p in sys.argv[1:]:
        imgToCSV(p, p + '.csv')
