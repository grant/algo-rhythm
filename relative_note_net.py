from neural_net import *
import midi, os, sys, time


class RelativeNote:
    """
    A RelativeNote stores a note's pitch and start time relative to the previous
    note (or relative to zero for an itial note), along with a duration.
    """
    def __init__(self, binary=None, pitch=0, time=0, duration=0):
        if binary != None:
            binary = map(str, binary)
            self.pitch = int(''.join(binary[:8]), 2)
            if binary[0] == 1:
                self.pitch -= (1 << 8) 
            self.time = int(''.join(binary[8:32]), 2)
            self.duration = int(''.join(binary[32:56]), 2)
        else:
            self.pitch = pitch
            self.time = time
            self.duration = duration

    def get_absolute(self, pitch, time):
        """
        Return the absolute pitch, time, and duration in a tuple given the
        previous note.
        """
        return (self.pitch + pitch, self.time + time, self.duration)

    def get_binary(self):
        pitch = format(self.pitch if self.pitch >= 0
                       else (1 << 8) + self.pitch, '08b')
        time = format(self.time, '024b')
        duration = format(self.duration, '024b')
        return map(int, pitch + time + duration)[:56]

class AbsoluteNote(RelativeNote):
    """
    Like a RelativeNote, but with pitches stored absolutely rather than
    relatively. Time is still relative.
    """
    def get_absolute(self, pitch=0, time):
        return (self.pitch, self.time + time, self.duration)

def midi_to_note_list(track, absolute=False):
    """
    Reads a midi track into a list of RelativeNotes
    """
    tick = 0
    notes = []
    started_notes = {}
    for event in track:
        tick += event.tick
        if isinstance(event, midi.NoteOffEvent) or isinstance(
            event, midi.NoteOnEvent) and event.velocity == 0:
            index, time = started_notes[event.pitch]
            notes[index] = (event.pitch, time, tick - time)
        elif isinstance(event, midi.NoteOnEvent):
            if event.pitch in started_notes:
                index, time = started_notes[event.pitch]
                notes[index] = (event.pitch, time, tick - time)
            started_notes[event.pitch] = (len(notes), tick)
            notes.append(None)
    for pitch in started_notes.keys():
        index, time = started_notes[pitch]
        notes[index] = (pitch, time, tick - time)
    prev_pitch = 0
    prev_time = 0
    note_list = []
    for pitch, time, duration in notes:
        note = None
        if absolute:
            note = AbsoluteNote(None, pitch, time = prev_time, duration)
        else:
            note = RelativeNote(None, pitch - prev_pitch,
                                time - prev_time, duration)
        note_list.append(note)
        prev_time = time
        prev_pitch = pitch
    return note_list

def note_list_to_midi(notes):
    """
    Converts a list of RelativeNotes to a MIDI track
    """
    track = midi.Track(tick_relative=False)
    pitch = 0
    time = 0
    for note in notes:
        pitch, time, duration = note.get_absolute(pitch, time)
        if pitch > 0 and pitch < 128:
            track.append(midi.NoteOnEvent(tick=time, pitch=pitch,
                                          velocity=60))
            track.append(midi.NoteOffEvent(tick=time+duration, pitch=pitch))
    track.sort(key=lambda x: x.tick)
    track.append(midi.EndOfTrackEvent(tick=track[-1].tick + 1
                                      if len(track) else 0))
    track.make_ticks_rel()
    return track

def get_note_lists(path):
    """
    Extract RelativeNote lists from all midi files in a folder.
    """
    lists = []
    for f in os.listdir(path):
        if f.endswith('.mid'):
            pattern = midi.read_midifile(path + f)
            for track in pattern:
                l = midi_to_note_list(track)
                if len(l):
                    lists.append(l)
    return lists

def train_note_list_net(net, lists, dropout=.5, output_rate=100,
                        output_length=64, total_epochs=5000, absolute=False,
                        path = 'net_output/note_list/'):
    """
    Trains a neural network, taking time notes from relative note lists
    as input.
    """
    batches = []
    for l in lists:
        binaries = [[map(float, n.get_binary())] for n in l]
        batches.append(zip(binaries[:-1], binaries[1:]))

    if not os.path.exists(path):
            os.makedirs(path)

    print('\nTraining network:')
    for i in xrange(0, total_epochs, output_rate):
        note_list_net_generate(net, output_length, path + '{0}.mid'.format(i),
                               absolute = absolute)
        print('\tfile example{0}.mid created'.format(i))
        net.save(path + 'weights{0}'.format(i))
        print('\tweights saved in weights{0}'.format(i))
        
        for j in xrange(output_rate):
            print "\t\t{}: {}".format(time.strftime("%c"), i + j)
            sys.stdout.flush()

            for batch in batches:
                net.reset()
                net.train(batch, 1, .075, dropout, .5)

def note_list_net_generate(net, length, path, start_note=60, absolute = False):
    """
    Generate a snippet of music with custom length using a note_list net.
    The net must be seeded with an initial note (which will not be played),
    the default for which is middle C.
    """
    net.reset()
    last = [RelativeNote(pitch=start_note).get_binary()]
    notes = []
    for i in xrange(length):
        note = net.run(last)
        if absolute:
            notes.append(AbsoluteNote(map(lambda x: int(round(x)), note[0])))
        else:
            notes.append(RelativeNote(map(lambda x: int(round(x)), note[0])))
        last = note
    midi.write_midifile(path, midi.Pattern([note_list_to_midi(notes)]))

if __name__ == '__main__':
    net = MLP(56, 56, [256, 256], True)
    lists = get_note_lists('midisamples_raw/')
    train_note_list_net(net, lists)
            
