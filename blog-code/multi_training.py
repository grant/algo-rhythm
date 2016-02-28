import os, random, sys
from midi_to_statematrix import *
from data import *
import cPickle as pickle
import readxml

import signal
import time

batch_width = 10 # number of sequences in a batch
batch_len = 16*8 # length of each sequence
division_len = 16 # interval between possible start locations

def loadPieces(dirpath):

    pieces = {}

#    for fname in os.listdir(dirpath):
#        if fname[-4:] not in ('.mid','.MID'):
#            continue

#        name = fname[:-4]

#        outMatrix = midiToNoteStateMatrix(os.path.join(dirpath, fname))
        
#        if len(outMatrix) < batch_len:
#            continue

#        pieces[name] = outMatrix
#        print "Loaded {}".format(name)
#        sys.stdout.flush()

#    return pieces

    tmp = readxml.createStateMatrices('../musicxml', batch_len)
    for key in tmp:
      pieces[key] = tmp[key][1]
    return pieces

def makeSegInSegOutFromStateMatrix(stateMatrix):
    seg_out = stateMatrix[start:start+batch_len]
    seg_in = noteStateMatrixToInputForm(seg_out)
    return seg_in, seg_out


def getPieceSegment(pieces):
    piece_output = random.choice(pieces.values())
    piecelen = len(piece_output)
    if piecelen == batch_len:
      start = 0
    elif piecelen < batch_len:
      raise ValueError("Found piece which was too short...")
    else:
      start = random.randrange(0, piecelen - batch_len, division_len)
      
    # print "Range is {} {} {} -> {}".format(0,len(piece_output)-batch_len,division_len, start)

    #seg_out = piece_output[start:start+batch_len]
    #seg_in = noteStateMatrixToInputForm(seg_out)

    #return seg_in, seg_out

    return makeSegInSegOutFromStateMatrix(piece_output)

def getPieceBatch(pieces):
    i,o = zip(*[getPieceSegment(pieces) for _ in range(batch_width)])
    return numpy.array(i), numpy.array(o)

def trainPiece(model,pieces,epochs,start=0):
    stopflag = [False]
    def signal_handler(signame, sf):
        stopflag[0] = True
    old_handler = signal.signal(signal.SIGINT, signal_handler)
    for i in range(start,start+epochs):
        if stopflag[0]:
            break
        error = model.update_fun(*getPieceBatch(pieces))
        if i % 100 == 0:
            print "{}: epoch {}, error={}".format(time.strftime("%c"), i, error)
            sys.stdout.flush()
        if i % 500 == 0 or (i % 100 == 0 and i < 1000):
            xIpt, xOpt = map(numpy.array, getPieceSegment(pieces))
            noteStateMatrixToMidi(numpy.concatenate((numpy.expand_dims(xOpt[0], 0), model.predict_fun(batch_len, 1, xIpt[0])), axis=0),'output/sample{}'.format(i))
            pickle.dump(model.learned_config,open('output/params{}.p'.format(i), 'wb'))
    signal.signal(signal.SIGINT, old_handler)


