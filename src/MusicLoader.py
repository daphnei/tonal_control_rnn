import midi
import numpy as np
import glob
import cPickle
import os
from Utils import ArgParser
import argparse
from tqdm import tqdm

class MusicLoader(object):
    ''' This class reads the MIDI files in the specified folder into a big numpy array. '''

    def __init__(self, args):
        self.midi_dir = args.midi_dir
        self.batch_size = args.batch_size
        self.seq_length = args.seq_length
        self.melody_track_num = args.melody_index
        self.harmony_track_num = args.harmony_index

        self.MIN_MIDI_NOTE = 24
        self.MAX_MIDI_NOTE = 102
        self.SAVE_FILE = 'midi_cache.pickle'

        # Which song training is currently retrieving samples from.
        self.song_index = 0
        #

        self.songs_melody = []
        self.songs_harmony = []
        if not self.check_for_cache():
            self.load_data()

    def load_data(self):
        files = glob.glob('{}/*.mid*'.format(self.midi_dir))
        for f in tqdm(files):
            try:
                melody, harmony = self.process_song(f)

                # Don't use any songs that are shorter than 1 sequence length long.
                if np.array(melody).shape[0] > self.seq_length:
                    self.songs_melody.append(melody)
                    self.songs_harmony.append(harmony)
            except Exception as e:
                print f, e

        with open(os.path.join(self.midi_dir, self.SAVE_FILE), "w") as file:
            cPickle.dump({'mel' : self.songs_melody, 'har' : self.songs_harmony}, file)

    def check_for_cache(self):
        cache_loc = os.path.join(self.midi_dir, self.SAVE_FILE)
        if os.path.isfile(cache_loc):
            with open(cache_loc, "r") as file:
                songs = cPickle.load(file)
                self.songs_melody = songs['mel']
                self.songs_harmony = songs['har']
                return True
        else:
            return False

    # def preprocess(self, input_file, vocab_file, tensor_file):
    #     with codecs.open(input_file, "r", encoding=self.encoding) as f:
    #         data = f.read()
    #
    # def load_preprocessed(self, vocab_file, tensor_file):
    #     with open(vocab_file, 'rb') as f:
    #         self.chars = cPickle.load(f)


    def next_batch(self):
        pass

    def reset_batch_pointer(self):
        self.pointer = 0

    def process_song(self, path):
        pattern = midi.read_midifile(path)

        # Load the song and reshape it to place multiple timesteps next to each other
        melody = np.array(self.midi_to_note_states(pattern, self.melody_track_num))
        harmony = np.array(self.midi_to_note_states(pattern, self.harmony_track_num))

        # Reshape each of the above to have length that is a multiple of the sequence length
        melody = self.reshape_to_seq_length(melody)
        harmony = self.reshape_to_seq_length(harmony)

        return melody, harmony

    def reshape_to_seq_length(self, song):
        song = song[:np.floor(song.shape[0] / self.seq_length) * self.seq_length]
        song = np.reshape(song, [song.shape[0] / self.seq_length, song.shape[1] * self.seq_length])

        return song

    def midi_to_note_states(self, pattern, track_index, squash=True):
        track = pattern[track_index]

        timeleft = track[0].tick

        statematrix = []
        time = 0

        span = self.MAX_MIDI_NOTE - self.MIN_MIDI_NOTE

        state = [[0, 0] for x in range(span)]

        statematrix.append(state)

        condition = True
        while condition:
            if time % (pattern.resolution / 4) == (pattern.resolution / 8):
                # Crossed a note boundary. Create a new state, defaulting to holding notes
                oldstate = state
                state = [[oldstate[x][0], 0] for x in range(span)]
                statematrix.append(state)

            if not condition:
                break
            pos = 0
            while timeleft == 0:
                evt = track[pos]
                if isinstance(evt, midi.NoteEvent):
                    if (evt.pitch < self.MIN_MIDI_NOTE) or (evt.pitch > self.MAX_MIDI_NOTE):
                        print "Note {} at time {} out of bounds (ignoring)".format(evt.pitch, time)
                        pass
                    else:
                        if isinstance(evt, midi.NoteOffEvent) or evt.velocity == 0:
                            state[evt.pitch - self.MIN_MIDI_NOTE] = [0, 0]
                        else:
                            state[evt.pitch - self.MIN_MIDI_NOTE] = [1, 1]
                elif isinstance(evt, midi.TimeSignatureEvent):
                    if evt.numerator not in (2, 4):
                        # We don't want to worry about non-4 time signatures. Bail early!
                        print "Found time signature event {} which is not currently supported!".format(evt)
                        out = statematrix
                        condition = False
                        break
                try:
                    pos += 1
                    timeleft = track[pos].tick
                except IndexError:
                    timeleft = None

            if timeleft is not None:
                timeleft -= 1

            if all(t is None for t in timeleft):
                break

            time += 1

        S = np.array(statematrix)
        statematrix = np.hstack((S[:, :, 0], S[:, :, 1]))
        statematrix = np.asarray(statematrix).tolist()
        return statematrix

    def write_song(self, path, song):
        #Reshape the song into a format that midi_manipulation can understand, and then write the song to disk
        song = np.reshape(song, (song.shape[0]*self.seq_length, 2*(self.MAX_MIDI_NOTE - self.MIN_MIDI_NOTE)))
        self.note_states_to_midi(song, path)

    def note_states_to_midi(self, statematrix, target_path):
        statematrix = np.array(statematrix)
        span = self.MAX_MIDI_NOTE - self.MIN_MIDI_NOTE
        if not len(statematrix.shape) == 3:
            statematrix = np.dstack((statematrix[:, :span], statematrix[:, span:]))
        statematrix = np.asarray(statematrix)
        pattern = midi.Pattern()
        track = midi.Track()
        pattern.append(track)

        tickscale = 55

        lastcmdtime = 0
        prevstate = [[0, 0] for x in range(span)]
        for time, state in enumerate(statematrix + [prevstate[:]]):
            offNotes = []
            onNotes = []
            for i in range(span):
                n = state[i]
                p = prevstate[i]
                if p[0] == 1:
                    if n[0] == 0:
                        offNotes.append(i)
                    elif n[1] == 1:
                        offNotes.append(i)
                        onNotes.append(i)
                elif n[0] == 1:
                    onNotes.append(i)
            for note in offNotes:
                track.append(midi.NoteOffEvent(tick=(time - lastcmdtime) * tickscale, pitch=note + lowerBound))
                lastcmdtime = time
            for note in onNotes:
                track.append(midi.NoteOnEvent(tick=(time - lastcmdtime) * tickscale, velocity=40, pitch=note + lowerBound))
                lastcmdtime = time

            prevstate = state

        eot = midi.EndOfTrackEvent(tick=1)
        track.append(eot)

        midi.write_midifile("{}.mid".format(target_path), pattern)

if __name__ == "__main__":
    parser = ArgParser()

    ml = MusicLoader(parser.parse_args())
    ml.write_song("test", ml.songs_melody[0])