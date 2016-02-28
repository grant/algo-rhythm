import cPickle as pickle
from midi_to_statematrix import *
import model, multi_training, midi_to_statematrix
import sys, random, data, time


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

  print "{}: Loading model from file {}".format(time.strftime("%c"), paramfile)
  sys.stdout.flush()
  mod = modelFromFile(paramfile)
  print "{}: Done loading model.".format(time.strftime("%c"))


  pitchrange = midi_to_statematrix.upperBound - midi_to_statematrix.lowerBound
  #We need to construct one slice to initialize the music generation
  firstSlice = []
  for i in range(0, pitchrange):
    pair = [0, 0]
    #if random.randrange(10) > 7:
    #  pair[0] = 1
    #  if random.randrange(10) > 5:
    #    pair[1] = 1
    firstSlice.append(pair)
  firstSlice = [firstSlice]

  xOpt = firstSlice
  xIpt = data.noteStateMatrixToInputForm(firstSlice)

  slices_to_generate = 128*16
  print "{}: Generating music to output/generated...".format(time.strftime("%c"))
  noteStateMatrixToMidi(numpy.concatenate((numpy.expand_dims(xOpt[0], 0), mod.predict_fun(slices_to_generate, 1, xIpt[0])), axis=0), 'output/generated')
  print "{}: Done.".format(time.strftime("%c"))

