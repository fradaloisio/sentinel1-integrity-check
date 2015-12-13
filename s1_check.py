import hashlib
import libxml2
import sys
import os.path

from Queue import Queue
from threading import Thread
import time

verbose = False
error = False
filesQ = Queue()

num_threads = 2

try:
    if str(sys.argv[1]) == "-v":
        product = str(sys.argv[2])
        verbose = True
    else:
        product = str(sys.argv[1])
except IndexError:
    print "Product is missing\n" \
          "USAGE:\n" \
          "python2.7 s1_check.py PRODUCT_NAME.SAFE\n" \
          "Options:\n" \
          "-v : Verbose"
    exit()

def report(message):
    if verbose:
        print message


def checkMD5(q):
    global error
    while error != True:
        file = q.get()
        #print(file)

        full_path =file['filename']
        filename_checksum = file['checksum']

        if not os.path.isfile(full_path):
            report( "[ERROR] " + full_path + " NOT EXIST" )
            error = True
            print "False"
        else:
            checksum = hashlib.md5(open(full_path, 'rb').read()).hexdigest()

            if checksum != filename_checksum:
                report( "[ERROR]" + full_path + " NOT VALID" )
                error = True
                print "False"
        q.task_done()


if not os.path.isdir(product):
    report( "[ERROR] " + product + " isn't a folder")
    print "False"
    exit()

if not os.path.isfile(product+"/manifest.safe"):
    report( "[ERROR] " + product+"/manifest.safe" + " NOT EXIST" )
    print "False"
    exit()


#set thread pool
for i in range(num_threads):
    worker = Thread(target=checkMD5, args=(filesQ,))
    worker.setDaemon(True)
    worker.start()


try:
    doc = libxml2.parseFile(product + "/manifest.safe")

    manifest = doc.xpathNewContext()

    manifest.xpathRegisterNs("xfdu","urn:ccsds:schema:xfdu:1")

    nodes = manifest.xpathEval('/xfdu:XFDU/dataObjectSection/dataObject')

    error = False

    for node in nodes:
        manifest.setContextNode(node)

        filename = str(manifest.xpathEval('byteStream/fileLocation/@href')[0].children)
        filename_checksum = str(manifest.xpathEval('byteStream/checksum')[0].content)
        full_path = product+filename[1:]

        prod = {}
        prod['filename'] = full_path
        prod['checksum'] = filename_checksum

        filesQ.put(prod)
        #print("push %s" %(full_path,))

    if error:
        report( "[ERROR] " + product + " NOT OK" )
        print "False"
        exit()
    else:
        report( product + " OK" )
        print "True"
        exit()

    filesQ.join()

except libxml2.parserError:
    report("manifest not valid ... ")
    exit()
