import cv2
import csv
import numpy

def imgToCSV(imgpath, csvpath):
    im = cv2.imread(imgpath, -1) # load as-is: this allows for 16-bit images to import correctly
    writer = csv.writer(open(csvpath, 'w'), delimiter=';')

    for row in im:
        if len(row.shape) > 1:
            row = numpy.concatenate(row)
        writer.writerow(row.tolist())

if __name__=='__main__':
    filename = raw_input('filename > ')
    imgToCSV(filename, filename + '.csv')
