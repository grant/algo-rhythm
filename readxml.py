import xml.etree.ElementTree
import fractions
import os
import collections
from collections import defaultdict
import fractions

import midi_to_statematrix
import math

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


def iterateThroughMusic(e, handleNote, handleMeasure = None, handleRest = None, handlePart = None):
  #for legacy reasons
  resolution = 1
  for part in e:
    if part.tag == 'part':
      partName = part.attrib['id']
      if handlePart != None:
        handlePart(partName)
      #keep track of the current time
      timePos = 0
      measureNum = 0
      lastNoteTimePos = 0
      for measure in part:
        if handleMeasure != None:
          handleMeasure()
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
                if handleRest != None:
                  handleRest(timePos, duration)
                timePos += duration
            elif note.tag == 'backup':
              duration = getBackupLength(note)
              timePos -= duration
            if timePos > latestTime:
              latestTime = timePos
          timePos = latestTime

#look under the current node and return
#the first node with the given name, if
#it exists
def getNodesUnderNodeWithName(node, name):
  retlist = []
  for el in node:
    if el.tag == name:
      retlist.append(el)
    retlist = retlist + getNodesUnderNodeWithName(el, name)
  return retlist

#look under the current node and return
#the first node with the given name, if
#it exists
def getNodeUnderNodeWithName(node, name):
  thelist = getNodesUnderNodeWithName(node, name)
  if thelist:
    return thelist[0]
  else:
    return None

#  for el in node:
#    if el.tag == name:
#      return el
#    else:
#      res = getNodeUnderNodeWithName(el, name)
#      if res != None:
#        return res
#  return None


#parse XML to find the tempo.  Note that for some songs,
#no tempo will exists, in which case return None.  Also,
#for some songs, there will be multiple tempos, in which
#case probably just return the first one found.
def getTempoForSong(tree):
  soundNodes = getNodesUnderNodeWithName(tree, 'sound')
  for soundNode in soundNodes:
    if 'tempo' in soundNode.attrib.keys():
      return int(round(float(soundNode.attrib['tempo'])))
  return None

#return hashmap of part to int, where the int
#is the amount to transpose each part in half steps.
#if there is no transposition for a given part, it
#can be omitted from the hash map
def getTranspositions(tree):
  ret = {}
  parts = getNodesUnderNodeWithName(tree, 'part')
  for part in parts:
    if 'id' in part.attrib.keys():
      partId = part.attrib['id']
      transposeNode = getNodeUnderNodeWithName(part, 'transpose')
      if transposeNode != None:
        for chromatic in transposeNode:
          if chromatic.tag == 'chromatic':
            ret[partId] = int(chromatic.text)
            break
  return ret

#we'll put this in its own routine, basically, the problem is,
#suppose a beat can be divided into div1 divisions and div2
#divisions. Suppose num specifies a point in time in divisions
#along the first scale.  Can it be translated to a point in
#time in units of the second scale?  If so, what is the number
#of units (everything must be an integer)
#In our code, this will be used to translate notes from "divs"
#(time unit of XML file) to "slices" (time unit of statematrix)
#If the note can't be translated then it is lost
def translateToDifferentDivScale(num, divs1, divs2):
  theGcd = fractions.gcd(divs1, divs2)
  if num % (divs2/theGcd) != 0:
    #we can't translate it
    return None
  else:
    return num * divs2 / divs1

#parses XML, delivering events to the callback
#that indicate note locations/durations in
#slices.  This can be used as a basis for parsing
#XML into various specific data structures
#also, this function returns a number indicating
#the number of slices that are actually a pickup
def parseXMLToSomething(xmltree, noteCreationCallback):

  #examine tree for any transpositions
  transpositions = getTranspositions(xmltree)

  #examine tree for tempo
  tempo = getTempoForSong(xmltree)
  if tempo == None:
    raise ValueError("can't produce state matrix for this XML, as there is no tempo")

  #also, check music to see if there's a pickup.
  #To do this, we look at the first two measures,
  #if the lengths are different (as can be determined
  #by looking at the notes and rests) then we have a
  #nonzero pickup, which is the length of the first measure
  class PickupLengthHandler:

    def __init__(self):
      self.measureNum = 0
      self.latestTimeSeen = 0
      self.measureLengths = [0, 0]

    def __handleSomething(self, time, duration):
      if self.measureNum == 1 or self.measureNum == 2:
        index = self.measureNum - 1
        if time + duration > self.measureLengths[index]:
          self.measureLengths[index] = time + duration

    def __call__(self, time, pitch, duration, part):
      self.__handleSomething(time, duration)

    def handleMeasure(self):
      self.measureNum += 1

    def handleRest(self, timePos, duration):
      self.__handleSomething(timePos, duration)

    def handlePart(self, partName):
      self.partName = partName

    def getPickupDivisions(self):
      if self.measureLengths[0] == self.measureLengths[1]:
        return 0
      else:
        return self.measureLengths[0]

  plm = PickupLengthHandler()
  iterateThroughMusic(xmltree, plm, plm.handleMeasure, plm.handleRest, plm.handlePart)

  pickupDivisions = plm.getPickupDivisions()
  pickupDivisionsPart = plm.partName

  #This is a constant, but actually it should be an input parameter.  Anyways,
  #given the tempo, the secondsPerSlice, and the divisions per beat, we should
  #be able to figure out how divisions in the input correspond to slices in the
  #output
  secondsPerSlice = 0.125

  beatsPerMinute = float(tempo)
  beatsPerSecond = beatsPerMinute / 60
  
  #e = xml.etree.ElementTree.parse(xmlfile).getroot()
  e = xmltree

  #returns hashmap, part to divisions number
  divisions = getDivisions(e)

  #compute lcm of divisions over various parts, this
  #will be the divisions we use
  divisionsLCM = None
  for k in divisions.keys():
    thisDiv = divisions[k]
    if divisionsLCM == None:
      divisionsLCM = thisDiv
    else:
      divisionsLCM = (thisDiv * divisionsLCM)/fractions.gcd(thisDiv, divisionsLCM)

  #use divisions now to translate the pickup divisions for the given part, not all
  #parts use the same division scale, so use the LCM scale
  pickupDivisions *= (divisionsLCM/divisions[pickupDivisionsPart])


  divisionsPerBeat = divisionsLCM

  #this will be an exact floating point number
  #print "secondsPerSlice: {}".format(secondsPerSlice)
  #print "beatsPerSecond: {}".format(beatsPerSecond)
  slicesPerBeat = 1 / (beatsPerSecond * secondsPerSlice)

  #we require that the number of slices for a beat be an integer which
  #is a power of two.  To do this, we'll take the log base 2, round
  #to the nearest int, then compute inverse log
  #print "SlicesPerBeat (real): {}".format(slicesPerBeat)
  slicesPerBeat = int(2**(int(round(math.log(slicesPerBeat, 2)))))

  #print "SlicesPerBeat: {}".format(slicesPerBeat)
  #print "divisionsPerBeat: {}".format(divisionsPerBeat)

  #compute gcd of slices per beat and divisions per beat
  slicesDivisionsGcd = fractions.gcd(slicesPerBeat, divisionsPerBeat)

  #we require that for a note to be resolved to slices, it's time in
  #divisions must be divisible by this number
  divisionsDivisor = divisionsPerBeat / slicesDivisionsGcd

  #compute the size of the pickup in slices, this is information
  #that will be needed for neural net training
  pickupSlices = pickupDivisions * slicesPerBeat / divisionsPerBeat

  #print "Pickup Divs: {}".format(pickupDivisions)
  #print "Pickup Slices: {}".format(pickupSlices)

  def handleNote_createStateMatrix(time, pitch, duration, part):
    #if part == 'P2':
    #print "Got note, pitch: {0}, duration: {1}, time: {2}".format(pitch, duration, time)
    pitch
    if part in transpositions.keys():
      pitch += transpositions[part]

    #Sometimes different parts have different
    #numbers of divisions, scale so that the time/
    #duration is in terms of the LCM divisions
    if divisions[part] != divisionsLCM:
      #print "LCM scaling happening"
      scalingFactor = (divisionsLCM / divisions[part])
      time *= scalingFactor
      duration *= scalingFactor

    #time and duration are in divisions, we need them in slices
    if time % divisionsDivisor != 0:
      #this note doesn't fall on a slice boundary so we just skip it
      return
    else:
      time = time * slicesPerBeat / divisionsPerBeat
      #print "duration before: {}".format(duration)
      duration = duration * slicesPerBeat / divisionsPerBeat
      #print "duration after: {}".format(duration)
      if duration == 0:
        duration = 1

    noteCreationCallback(time, pitch, duration)


    #ad hoc--if divisions are divisible by 3, then assume
    #that the division is at the lowest level for the piece,
    #we set the granularity to ignore this subdivision level

  iterateThroughMusic(e, handleNote_createStateMatrix)

  return pickupSlices

#wrapper that takes filename instead of tree
def parseXMLFileToSomething(xmlFile, noteCreationCallback):
  tree = xml.etree.ElementTree.parse(xmlFile).getroot()
  return parseXMLToSomething(tree, noteCreationCallback)

def stateMatrixForSong(tree):

  stateMatrix = []

  def handleNoteCreation(time, pitch, duration):
    #for state matrices, we shift pitch down
    #by lower bound constant
    pitch -= lowerBound

    #if necessary, extend state matrix so
    #that the desired times exists
    #last time needed is time + duration - 1,
    #len <= last time needed, so...
    #print "Note at time {0}, pitch: {1}".format(time, pitch)
    while len(stateMatrix) < time + duration:
      row = numPitches * [[0, 0]]
      stateMatrix.append(row)
    #print "time: {}".format(time)
    #print "size: {}".format(len(stateMatrix))
    stateMatrix[time][pitch] = [1, 1]
    for i in range(time + 1, time + duration):
      if stateMatrix[i][pitch] == [0, 0]:
        stateMatrix[i][pitch] = [1, 0]

  pickupSlices = parseXMLToSomething(tree, handleNoteCreation)

  return (pickupSlices, stateMatrix)


def createStateMatrices(basedir = 'musicxml', minslices = 0):

  stateMatrices = {}

  for theFile in os.listdir(os.getcwd() + '/' + basedir):
    if not theFile.split('.')[-1] == 'xml':
      continue
        #parse xml file into document tree
    print basedir + '/' + theFile
    tree = xml.etree.ElementTree.parse(basedir + '/' + theFile).getroot()
    if getTempoForSong(tree) == None:
      print "File {} has no tempo!!!".format(theFile)
    else:
      sm = stateMatrixForSong(tree)
      songMatrix = sm[1]
      if len(songMatrix) < minslices:
        print "File {} omitted, it is too short.".format(theFile)
      else:
        stateMatrices[theFile] = sm

  return stateMatrices




#NOTE: INTERFACE CHANGED--now returns 0 on success,
#1 on failure, reason for failure is that there is
#actually no tempo information in the xml file, so
#we don't know how to convert to midi
def midiForXML(xmlFile, midiDestFile):
  #parse xml file into document tree
  tree = xml.etree.ElementTree.parse(xmlFile).getroot()
  tempo = getTempoForSong(tree)
  #We're no longer using a default tempo, this was never
  #really a good idea, since actually the various tempos
  #can differ by an order of magnitued, instead, we return
  #a code to indicate success or failure.
  #if tempo == None:
  #  tempo = 120
  if tempo == None:
    return 1
  else:
    stateMatrix = stateMatrixForSong(tree, 0)[1]
    midi_to_statematrix.noteStateMatrixToMidi(stateMatrix, name=midiDestFile)
    return 0    

if __name__ == "__main__":
  stateMatrices = createStateMatrices()
  print "{0} songs total.".format(len(stateMatrices))
  #print "Pwd: " + os.getcwd()
  for k in stateMatrices.keys():
    midi_to_statematrix.noteStateMatrixToMidi(stateMatrices[k][1], name='./midi_output_test/{}'.format(k))
    


#NO LONGER USED!!!!
def createStateMatrices_old():
  basedir = "musicxml/"

  f = open(basedir + 'catalog.txt', "r")
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
    origFilename = toks[1]
    mxlfile = basedir + origFilename
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
    if getTempoForSong(tree) == None:
      print "File {} has no tempo!!!".format(mxlfile)
    else:
      stateMatrices[origFilename] = stateMatrixForSong(tree)

  return stateMatrices


