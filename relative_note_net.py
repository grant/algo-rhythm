import neural_net
import midi

class RelativeNote:
    """
    A RelativeNote stores a note's pitch and start time relative to the previous
    note (or relative to zero for an itial note), along with a duration.
    """
    def __init__(self, pitch, time, duration):
        self.pitch = pitch
        self.time = time
        self.duration = duration

    def get_absolute(self, pitch, time):
        """
        Return the absolute pitch, time, and duration in a tuple given the
        previous note.
        """
        return (self.pitch + pitch, self.time + time, self.duration)

def midi_to_note_list(track):
    """
    Reads a midi track into a list of RelativeNotes
    """
    tick = 0
    notes = []
    started_notes = {}
    for event in track:
        tick += event.tick
        if isinstance(event, midi.NoteOnEvent):
            if event.pitch in started_notes:
                index, time = started_notes[event.pitch]
                notes[index] = (event.pitch, time, tick - time)
            started_notes[event.pitch] = (len(notes), tick)
            notes.append(None)
        if isinstance(event, midi.NoteOffEvent):
            index, time = started_notes[event.pitch]
            notes[index] = (event.pitch, time, tick - time)
    for pitch in started_notes.keys():
        index, time = started_notes[pitch]
        notes[index] = (pitch, time, tick - time)
    prev_pitch = 0
    prev_time = 0
    note_list = []
    for pitch, time, duration in notes:
        relative = RelativeNote(pitch - prev_pitch, time - prev_time, duration)
        note_list.append(relative)
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
        track.append(midi.NoteOnEvent(tick=time, pitch=pitch))
        track.append(midi.NoteOffEvent(tick=time+duration, pitch=pitch))
    track.sort(key=lambda x: x.tick)
    track.append(midi.EndOfTrackEvent(tick=track[-1].tick + 1))
    track.make_ticks_rel()
    return track
    
            
