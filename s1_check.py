import hashlib
import libxml2
import sys
import os.path

try:
    product = str(sys.argv[1])
except IndexError:
    print "Product is missing\n" \
          "USAGE:\n" \
          "python2.7 s1_check.py PRODUCT_NAME.SAFE"
    exit()

if not os.path.isdir(product):
    print "[ERROR] " + product + " isn't a folder"
    exit()

if not os.path.isfile(product+"/manifest.safe"):
    print "[ERROR] " + product+"/manifest.safe" + " NOT EXIST"
    exit()

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

        checksum = hashlib.md5(open(full_path, 'rb').read()).hexdigest()

        if checksum != filename_checksum:
            print "[ERROR]" + product+filename[1:] + " not valid"
            error = True

    if error:
        print "[ERROR] " + product + " NOT OK"
    else:
        print product + " OK"

except libxml2.parserError:
    print "manifest not valid ... "
