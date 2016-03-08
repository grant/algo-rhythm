import cPickle as pickle
import gzip
import numpy
from midi_to_statematrix import *

import multi_training
import model


if len(sys.argv) != 4:
  print "Need 3 arguments, one specifying output file, a single argument with a list of training files, and a number of training iterations"
  exit(1)

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



def gen_adaptive(m,pcs,times,keep_thoughts=False,name="final"):
	xIpt, xOpt = map(lambda x: numpy.array(x, dtype='int8'), multi_training.getPieceSegment(pcs))
	all_outputs = [xOpt[0]]
	if keep_thoughts:
		all_thoughts = []
	m.start_slow_walk(xIpt[0])
	cons = 1
	for time in range(multi_training.batch_len*times):
		resdata = m.slow_walk_fun( cons )
		nnotes = numpy.sum(resdata[-1][:,0])
		if nnotes < 2:
			if cons > 1:
				cons = 1
			cons -= 0.02
		else:
			cons += (1 - cons)*0.3
		all_outputs.append(resdata[-1])
		if keep_thoughts:
			all_thoughts.append(resdata)
	noteStateMatrixToMidi(numpy.array(all_outputs),'output/'+name)
	if keep_thoughts:
		pickle.dump(all_thoughts, open('output/'+name+'.p','wb'))

def fetch_train_thoughts(m,pcs,batches,name="trainthoughts"):
	all_thoughts = []
	for i in range(batches):
		ipt, opt = multi_training.getPieceBatch(pcs)
		thoughts = m.update_thought_fun(ipt,opt)
		all_thoughts.append((ipt,opt,thoughts))
	pickle.dump(all_thoughts, open('output/'+name+'.p','wb'))

if __name__ == '__main__':

	pcs = loadPiecesFromFileList(xmlfiles)

	m = model.Model([300,300],[100,50], dropout=0.5)

        def handleEpochStart(epoch):
          percentage = int(100 * float(epoch)/float(numiterations))
          print "PERCENT: {}".format(percentage)

	multi_training.trainPiece(m, pcs, numiterations, handleEpochStart)

	pickle.dump( m.learned_config, open( outfile, "wb" ) 
)


