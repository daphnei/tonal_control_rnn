import midi
import numpy as np
import glob
from tqdm import tqdm
class MusicLoader(object):
    def __init__(self, midi_dir, batch_size, seq_length):
        self.midi_dir = midi_dir
        self.batch_size = batch_size
        self.seq_length = seq_length

        self.MIN_MIDI_NOTE = 1
        self.MAX_MIDI_NOTE = 127

        files = glob.glob('{}/*.mid*'.format(self.midi_dir))
        self.songs = []
        for f in tqdm(files):
            try:
                song = self.get_song(f)

                # Don't use any songs that are shorter than the sequence length.
                if np.array(song).shape[0] > self.seq_length:
                    self.songs.append(song)
            except Exception as e:
                print f, e


        def preprocess(self, input_file, vocab_file, tensor_file):
            with codecs.open(input_file, "r", encoding=self.encoding) as f:
                data = f.read()

        def load_preprocessed(self, vocab_file, tensor_file):
            with open(vocab_file, 'rb') as f:
                self.chars = cPickle.load(f)

        def create_batches(self):


        def next_batch(self):


        def reset_batch_pointer(self):
            self.pointer = 0

        def get_song(self, path):
            # Load the song and reshape it to place multiple timesteps next to each other
            song = np.array(self.midiToNoteStateMatrix(path))
            song = song[:np.floor(song.shape[0] / num_timesteps) * num_timesteps]
            song = np.reshape(song, [song.shape[0] / num_timesteps, song.shape[1] * num_timesteps])
            return song

        def midiToNoteStateMatrix(self, midifile, squash=True, span=span):
            pattern = midi.read_midifile(midifile)

            timeleft = [track[0].tick for track in pattern]

            posns = [0 for track in pattern]

            statematrix = []
            time = 0

            state = [[0, 0] for x in range(span)]
            statematrix.append(state)
            condition = True
            while condition:
                if time % (pattern.resolution / 4) == (pattern.resolution / 8):
                    # Crossed a note boundary. Create a new state, defaulting to holding notes
                    oldstate = state
                    state = [[oldstate[x][0], 0] for x in range(span)]
                    statematrix.append(state)
                for i in range(len(timeleft)):  # For each track
                    if not condition:
                        break
                    while timeleft[i] == 0:
                        track = pattern[i]
                        pos = posns[i]

                        evt = track[pos]
                        if isinstance(evt, midi.NoteEvent):
                            if (evt.pitch < self.MIN_MIDI_NOTE) or (evt.pitch > self.MAX_MIDI_NOTE):
                                pass
                                # print "Note {} at time {} out of bounds (ignoring)".format(evt.pitch, time)
                            else:
                                if isinstance(evt, midi.NoteOffEvent) or evt.velocity == 0:
                                    state[evt.pitch - lowerBound] = [0, 0]
                                else:
                                    state[evt.pitch - lowerBound] = [1, 1]
                        elif isinstance(evt, midi.TimeSignatureEvent):
                            if evt.numerator not in (2, 4):
                                # We don't want to worry about non-4 time signatures. Bail early!
                                # print "Found time signature event {}. Bailing!".format(evt)
                                out = statematrix
                                condition = False
                                break
                        try:
                            timeleft[i] = track[pos + 1].tick
                            posns[i] += 1
                        except IndexError:
                            timeleft[i] = None

                    if timeleft[i] is not None:
                        timeleft[i] -= 1

                if all(t is None for t in timeleft):
                    break

                time += 1

            S = np.array(statematrix)
            statematrix = np.hstack((S[:, :, 0], S[:, :, 1]))
            statematrix = np.asarray(statematrix).tolist()
            return statematrix
