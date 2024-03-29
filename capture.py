import subprocess
import tempfile
import Image
import StringIO

def capture():
    "assumes camera set to capture in RAW mode; returns decoded Image"
    with tempfile.NamedTemporaryFile(suffix='cr2') as tmp:
        cmd = ['gphoto2',
               '--force-overwrite',
               '--capture-image-and-download', 
               '--filename', tmp.name]
        print cmd

        # XXX: error handling

        p = subprocess.Popen(cmd)
        out = p.wait()
        if out != 0:
            print "capture failed, returning test image"
            import calibration
            from numpy import uint8
            im = Image.fromarray((255*calibration.grid(20)).astype(uint8), mode='L').convert('RGB')
            return im

        # XXX: white balance calibration
        # dcraw -c -o 5 -4 -w -T
        cmd = ['dcraw',
               '-c',

               #'-4',            # linear 16-bit

               '-W',            # fixed white level
               "-g", "1", "1",  # linear
               '-o', '1',       # raw

               '-T',            # TIFF (with metadata)
               tmp.name]
        print cmd
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()

        sim = StringIO.StringIO(stdout)

        return Image.open(sim)

def captureJPG():
    "assumes camera set to capture in JPG mode; returns decoded Image"
    cmd = ['gphoto2',
           '--stdout',
           '--capture-image-and-download']
    print cmd

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    sim = StringIO.StringIO(stdout)
    return Image.open(sim)
