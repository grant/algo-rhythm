import cPickle as pickle
from midi_to_statematrix import *
import model, multi_training
import sys


def modelFromFile(filename):
  learned_list = pickle.load(open(filename, 'rb'))
  mod = model.Model()
  mod.learned_config = learned_list
  return mod

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "Needs exactly one arg..."
    exit(1)

  paramfile = sys.argv[1]
  mod = modelFromFile(paramfile)

  noteStateMatrixToMidi(numpy.concatenate((numpy.expand_dims(xOpt[0], 0), model.predict_fun(batch_len, 1, xIpt[0])), axis=0),'output/generated'.format(i))
