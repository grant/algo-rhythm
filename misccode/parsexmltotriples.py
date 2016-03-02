import readxml, sys, os


if __name__ == '__main__':

  if len(sys.argv) != 2:
    print "Requires exactly one arg, input XML file"
    exit(1)

  inputFile = sys.argv[1]

  if not os.path.isfile(inputFile):
    print "file {} does not exist.".format(outfile)
    exit(1)

  def handleNoteDetection(time, pitch, duration):
    print time, pitch, duration

  readxml.parseXMLFileToSomething(inputFile, handleNoteDetection)

  

