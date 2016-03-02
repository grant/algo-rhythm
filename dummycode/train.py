import sys, time, os
from time import sleep

#print "Argv: {}".format(sys.argv)

if len(sys.argv) != 4:
  print "Need 3 arguments, one specifying output file, a single argument with a list of training files, and a number of training iterations"
  exit(1)

#if len(sys.argv) > 3:
#  print "No more than two arguments allowed"
#  exit(1)

outfile = sys.argv[1]
if os.path.isfile(outfile):
  print "file {} already exists.".format(outfile)
  exit(1)

xmlfiles = sys.argv[2].split()

for xmlfile in xmlfiles:
  if not os.path.isfile(xmlfile):
    print "xml file {} does not exist.".format(xmlfile)
    exit(1)

for xmlfile in xmlfiles:
  print "Loading XML file {}".format(xmlfile)
  sys.stdout.flush()
  sleep(1)

numiterations = int(sys.argv[3])

#user can provide a previous training
#config to continue from
#previousConfig = None
#if len(sys.argv) == 3:
#  previousConfig = sys.argv[2]
#  if not os.path.isfile(previousConfig):
#    print "file {} doesn't exist, but it should".format(previousConfig)
#    exit(1)

#load config here...
#if previousConfig != None:
#  print "Using initial config {}".format(previousConfig)

print "Starting training, using {} iterations".format(numiterations)
sys.stdout.flush()
sleep(1.0)
print "Doing a lot of rounds of training..."
sys.stdout.flush()
sleep(3.0)
print "Doing more rounds of training..."
sys.stdout.flush()
sleep(3.0)
print "Almost done..."
sys.stdout.flush()
sleep(3.0)
print "Complete!!!!"
sys.stdout.flush()

outfile = open(outfile, 'w')
outfile.write("TRAINED CONFIG\n")
outfile.flush()
outfile.close()

