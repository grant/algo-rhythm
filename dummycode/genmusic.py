import sys, random, time, os
import midi
from time import sleep


if __name__ == '__main__':

  if len(sys.argv) != 4:
    print "Needs exactly three args, configfile, output file and number of seconds of music to make"
    exit(1)

  paramfile = sys.argv[1]
  if not os.path.isfile(paramfile):
    print "paramfile {} does not exist.".format(paramfile)
    exit(1)

  outfile = sys.argv[2]

  numseconds = int(sys.argv[3])

  print "{}: Loading model from file {}".format(time.strftime("%c"), paramfile)
  sys.stdout.flush()
  sleep(4)

  slices_to_generate = 8 * numseconds

  print "{}: Generating music to output/generated...".format(time.strftime("%c"))
  print "PERCENT: 20"
  sys.stdout.flush()
  sleep(1)
  print "Still generating music..."
  print "PERCENT: 40"
  sys.stdout.flush()
  sleep(1)
  print "Still generating music... (2)"
  print "PERCENT: 50"
  sys.stdout.flush()
  sleep(1)
  print "Still generating music... (3)"
  print "PERCENT: 60"
  sys.stdout.flush()
  sleep(1)
  print "Still generating music... (4)"
  print "PERCENT: 85"
  sys.stdout.flush()
  sleep(1)
  print "Done generating music, writing out..."
  print "PERCENT: 100"
  sys.stdout.flush()




  # Instantiate a MIDI Pattern (contains a list of tracks)
  pattern = midi.Pattern()
  # Instantiate a MIDI Track (contains a list of MIDI events)
  track = midi.Track()
  # Append the track to the pattern
  pattern.append(track)

  # Instantiate a MIDI note on event, append it to the track
  on = midi.NoteOnEvent(tick=0, velocity=50, pitch=midi.G_3)
  track.append(on)
  on = midi.NoteOnEvent(tick=0, velocity=50, pitch=midi.G_2)
  track.append(on)
  # Instantiate a MIDI note off event, append it to the track
  off = midi.NoteOffEvent(tick=100, pitch=midi.G_3)
  track.append(off)


  # Instantiate a MIDI note on event, append it to the track
  on = midi.NoteOnEvent(tick=0, velocity=50, pitch=midi.B_3)
  track.append(on)
  # Instantiate a MIDI note off event, append it to the track
  off = midi.NoteOffEvent(tick=100, pitch=midi.B_3)
  track.append(off)

  # Instantiate a MIDI note on event, append it to the track
  on = midi.NoteOnEvent(tick=0, velocity=50, pitch=midi.D_4)
  track.append(on)
  # Instantiate a MIDI note off event, append it to the track
  off = midi.NoteOffEvent(tick=100, pitch=midi.D_4)
  track.append(off)

  # Instantiate a MIDI note on event, append it to the track
  #on = midi.NoteOnEvent(tick=100, velocity=50, pitch=midi.G_3)
  #track.append(on)
  # Instantiate a MIDI note off event, append it to the track
  #off = midi.NoteOffEvent(tick=300, pitch=midi.G_2)
  #track.append(off)


  # Add the end of track event, append it to the track
  eot = midi.EndOfTrackEvent(tick=1)
  track.append(eot)
  # Print out the pattern
  #print pattern
  # Save the pattern to disk
  midi.write_midifile(outfile, pattern)




  print "Written out!!"
  sys.stdout.flush()

