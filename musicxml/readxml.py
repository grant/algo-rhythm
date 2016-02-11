import xml.etree.ElementTree
import fractions

import collections
from collections import defaultdict

import midi_to_statematrix

lowerBound = 24
upperBound = 102

numPitches = upperBound - lowerBound

#get the "divisions" which is the number of time
#units per beat
def getDivisions(e):
  divisions_val = None
  retval  = {}
  for part in e:
    if part.tag == 'part':
      partName = part.attrib['id']
      for measure in part:
        if measure.tag == 'measure':
          for attributes in measure:
            if attributes.tag == 'attributes':
              for divisions in attributes:
                if divisions.tag == 'divisions':
                  divs = int(divisions.text)
                  retval[partName] = divs
                  if divisions_val == None:
                    divisions_val = divs
#                  else:
                    #let's just check to see that there is
                    #always agreement
                    #nvm, doesn't matter
                    #if divisions_val != divs:
                      #print "Divisions don't agree: {0} != {1}".format(divisions_val, divisions.text)
#  return divisions_val
  return retval

#if it's a rest, return the
#duration, otherwise return none
def getRestLength(note):
  duration = None
  isRest = False
  for el in note:
    if el.tag == 'rest':
      isRest = True
    elif el.tag == 'duration':
      if duration == None:
        duration = int(el.text)        
      else:
        #found duration tag twice
        print "Duration tag found twice for note..."
  if isRest:
    if duration == None:
      #problem...
      print "Rest with no duration found"
    else:
      return duration
  else:
    #it's not a rest; return none
    return None

#return the duration for a backup element
def getBackupLength(backup):
  duration = None
  for el in backup:
    if el.tag == 'duration':
      if duration == None:
        duration = int(el.text)        
      else:
        #found duration tag twice
        print "Duration tag found twice for note..."
  return duration

def xmlPitchToMidiPitch(letter, octave, alter):
  table = {
    "C" : 0,
    "D" : 2,
    "E" : 4,
    "F" : 5,
    "G" : 7,
    "A" : 9,
    "B" : 11,
  }
  if not letter in table.keys():
    print "Letter {0} is not a valid letter A-G".format(letter)
  return 12 + table[letter] + 12 * octave + alter


#get pitch, and duration for a note
def getNoteInfo(note, measureNum):
  duration = None
  step = None
  octave = None
  alter = None
  isRest = False
  isChord = False
  tieType = None
  for el in note:
    if el.tag == 'rest':
      isRest = True
    elif el.tag == 'duration':
      if duration == None:
        duration = int(el.text)
      else:
        #found duration tag twice
        print "Duration tag found twice for note..."
    elif el.tag == 'chord':
      isChord = True
    elif el.tag == 'tie':
      tieType = el.attrib['type']
    elif el.tag == 'pitch':
      for pitchel in el:
        if pitchel.tag == 'step':
          if step == None:
            step = pitchel.text
          else:
            #found step tag twice
            print "step tag found twice for note..."
        if pitchel.tag == 'octave':
          if octave == None:
            octave = int(pitchel.text)
          else:
            #found octave tag twice
            print "octave tag found twice for note..."
        if pitchel.tag == 'alter':
          if alter == None:
            alter = int(pitchel.text)
          else:
            #found alter tag twice
            print "alter tag found twice for note..."
  if isRest:
    #if it's a rest, then return None
    return None
  else:
    if duration == None:
      #this can happen for grace notes so actually just return none
      return None
    elif step == None:
      print "Note with no step found"
    elif octave == None:
      print "Note with no octave found"
    if alter == None:
      alter = 0
    midiPitch = xmlPitchToMidiPitch(step, octave, alter)
    return (midiPitch, duration, isChord, tieType)


def iterateThroughMusic(e, handleNote, resolution = 1):
  for part in e:
    if part.tag == 'part':
      partName = part.attrib['id']
      #keep track of the current time
      timePos = 0
      measureNum = 0
      lastNoteTimePos = 0
      for measure in part:
        if measure.tag == 'measure':
          #remember measure start time
          #measureStartTime = timePos
          #record latest time
          latestTime = timePos
          for note in measure:
            if note.tag == 'note':
              res = getRestLength(note)
              if res == None:
                #it's a note
                res = getNoteInfo(note, measureNum)
                if res == None:
                  #this can happen for grace notes, for example,
                  #just ignore
                  continue
                midiPitch, duration, isChord, tieType = res
                #allNotes[timePos, (midiPitch, duration)]
                #print "Found note, pitch: {0}, duration: {1}".format(midiPitch, duration)
                if timePos % resolution == 0:
                  if isChord:
                    #print "isChord, lastTime: {0}, currTime: {1}".format(lastNoteTimePos, timePos)
                    timePosForNote = lastNoteTimePos
                  else:
                    timePosForNote = timePos
                  if tieType != 'stop':
                    handleNote(timePosForNote / resolution, midiPitch, (duration - 1) / resolution + 1, partName)
                if not isChord:
                  lastNoteTimePos = timePos
                  timePos += duration
              else:
                #it's a rest
                duration = res
                timePos += duration
            elif note.tag == 'backup':
              duration = getBackupLength(note)
              timePos -= duration
            if timePos > latestTime:
              latestTime = timePos
          timePos = latestTime

#parse XML to find the tempo.  Note that for some songs,
#no tempo will exists, in which case return None.  Also,
#for some songs, there will be multiple tempos, in which
#case probably just return the first one found.
def getTempoForSong(tree):
  for el in tree:
    if el.tag == 'sound':
      if 'tempo' in el.attrib.keys():
        return int(round(float(el.attrib['tempo'])))
    else:
      res = getTempoForSong(el)
      if res != None:
        return res
  return None


def stateMatrixForSong(tree, startTime, speed = None, slow = None, transpositions = {}):

  secondsPerSlice = 0.125
  beatsPerMinute = 120

  #basically we would like to know divisions per slice...

  #e = xml.etree.ElementTree.parse(xmlfile).getroot()
  e = tree

  divisions = getDivisions(e)
  #print divisions
  tripleMeter = False
  for k in divisions.keys():
    if divisions[k] % 3 == 0:
      #Turn this off
      #print "Triple meter detected"
      tripleMeter = True

  divisionsMax = None
  for k in divisions.keys():
    if divisionsMax == None:
      divisionsMax = divisions[k]
    elif divisionsMax < divisions[k]:
      divisionsMax = divisions[k]

  #check that the min divisions value divides every
  #key in the map
  for k in divisions.keys():
    if divisionsMax % divisions[k] != 0:
      print "min division ({1}) not divisible by division found ({0})!".format(divisions[k], divisionsMax)


  class handleNote_interval_visitor:

    def __init__(self):
      self.minTimeInterval = None

    def __call__(self, time, pitch, duration, part):
      if time != 0:
        if self.minTimeInterval == None:
          self.minTimeInterval = time
        else:
          self.minTimeInterval = fractions.gcd(self.minTimeInterval, time)
      if duration != 0:
        if self.minTimeInterval == None:
          self.minTimeInterval = duration
        else:
          self.minTimeInterval = fractions.gcd(self.minTimeInterval, duration)

  visitor = handleNote_interval_visitor()
  iterateThroughMusic(e, visitor)
  minTimeInterval = visitor.minTimeInterval

  stateMatrix = []

  def handleNote_createStateMatrix(time, pitch, duration, part):
    #if part == 'P2':
      #print "Got note, pitch: {0}, duration: {1}, time: {2}".format(pitch, duration, time)
    pitch -= lowerBound
    if part in transpositions.keys():
      pitch += transpositions[part]

    #Sometimes different parts have different
    #numbers of divisions, so we have to scale
    #appropriately
    if divisions[part] != divisionsMax:
      slowFactor = (divisionsMax / divisions[part])
      time *= slowFactor
      duration *= slowFactor

    if slow != None:
      time *= slow
      duration *= slow
    if speed != None:
      #skip a note if its granularity
      #is too fine
      if time % speed != 0:
        return
      time /= speed
      duration /= speed
      if duration == 0:
        duration = 1

    #if necessary, extend state matrix so
    #that the desired times exists
    #last time needed is time + duration - 1,
    #len <= last time needed, so...
    #print "Note at time {0}, pitch: {1}".format(time, pitch)
    while len(stateMatrix) < time + duration:
      row = numPitches * [[0, 0]]
      stateMatrix.append(row)
    stateMatrix[time][pitch] = [1, 1]
    for i in range(time + 1, time + duration):
      if stateMatrix[i][pitch] == [0, 0]:
        stateMatrix[i][pitch] = [1, 0]

    #ad hoc--if divisions are divisible by 3, then assume
    #that the division is at the lowest level for the piece,
    #we set the granularity to ignore this subdivision level

  minTimeInterval = 1
  for k in divisions.keys():
    if divisions[k] % 3 == 0:
      minTimeInterval = 3

  iterateThroughMusic(e, handleNote_createStateMatrix, minTimeInterval)

  if slow == None:
    slow = 1
  if speed == None:
    speed = 1
  return (int(round(startTime*divisionsMax*slow/speed)), stateMatrix)


def createStateMatrices():

  f = open('catalog.txt', "r")
  lines = f.readlines()
  f.close()

  stateMatrices = {}

  #function that returns the default
  #value of a state matrix
  def defaultValFactory():
    return [0, 0]

  inBlockComment = False
  while lines:
    line = lines[0]
    del lines[0]
    if len(line) > 0 and line[0] == '#':
      continue
    toks = line.split()

    if len(toks) == 0:
      continue

    if inBlockComment:
      if toks[0] == 'endcomment':
        inBlockComment = False
      continue

    if toks[0] == 'begincomment':
      inBlockComment = True
      continue

    if len(toks) == 2 and toks[0] == 'file':
      pass
    else:
      continue
    mxlfile = toks[1]
    print mxlfile

    transpositions = {}
    slow = None
    speed = None
    startTime = 0
    while lines and len(lines[0].split()) != 0 and lines[0].split()[0] != 'file':
      line = lines[0]
      del lines[0]
      toks = line.split()
      if toks[0] == 'transpose':
        if not len(toks) == 3:
          continue
        transpositions[toks[1]] = int(toks[2])
      elif toks[0] == 'slow':
        if not len(toks) == 2:
          continue
        slow = int(toks[1])
      elif toks[0] == 'speed':
        if not len(toks) == 2:
          continue
        speed = int(toks[1])
      elif toks[0] == 'start-time':
        if not len(toks) == 2:
          continue
        startTime = float(toks[1])

    #parse xml file into document tree
    tree = xml.etree.ElementTree.parse(mxlfile).getroot()
    tempo = getTempoForSong(tree)
    if tempo == None:
      print "No tempo found"
    else:
      print "Tempo of {0} found".format(tempo)
    stateMatrices[mxlfile] = stateMatrixForSong(tree, startTime, speed, slow, transpositions)

  return stateMatrices

def midiForXML(xmlFile, midiDestFile):
  #parse xml file into document tree
  tree = xml.etree.ElementTree.parse(mxlfile).getroot()
  tempo = getTempoForSong(tree)
  if tempo == None:
    tempo = 120
  stateMatrix = stateMatrixForSong(tree, 0)[1]
  midi_to_statematrix.noteStateMatrixToMidi(stateMatrix, name=midiDestFile)

if __name__ == "__main__":
  stateMatrices = createStateMatrices()
  print "{0} songs total.".format(len(stateMatrices))
  for k in stateMatrices.keys():
    midi_to_statematrix.noteStateMatrixToMidi(stateMatrices[k][1], name=("./midi/" + k))





