import cPickle as pickle
from midi_to_statematrix import *
import model, multi_training
import sys


def modelFromFile(filename):
  learned_list = pickle.load(open(filename, 'rb'))
  mod = Model()
  mod.learned_config(learned_list)


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "Needs exactly one arg..."
    exit(1)

  paramfile = sys.argv[1]
  mod = modelFromFile(paramfile)


