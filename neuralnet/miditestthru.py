import sys
import relative_note_net
import midi



if __name__ == '__main__':
  if len(sys.argv) != 3:
    print 'Requires midi files as args, src then dest'
    exit(1)

  filename = sys.argv[1]
  outfile = sys.argv[2]

  notelist = relative_note_net.get_notelist_for_xml(filename)
  tracklist = []
#  for notelist in notelists:
#    tracklist.append(relative_note_net.note_list_to_midi(notelist))
  #55 ticks per slice
  tracklist.append(relative_note_net.note_list_to_midi_XML(notelist))

  midi.write_midifile(outfile, midi.Pattern(tracklist))

