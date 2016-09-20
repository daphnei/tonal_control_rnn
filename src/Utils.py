from argparse import ArgumentParser

class ArgParser(ArgumentParser):
    def __init__(self):
        ArgumentParser.__init__(self)

        self.add_argument('--midi_dir', type=str, default='data',
                            help='data directory containing input harmony midi files')
        self.add_argument('--melody_index', type=int, default='data',
                            help='The track index we will base music generation off of.')
        self.add_argument('--harmony_index', type=int, default='data',
                            help='The index for the supporting track that will be used to bias generation.')
        self.add_argument('--save_dir', type=str, default='save',
                            help='directory to store checkpointed models')
        self.add_argument('--rnn_size', type=int, default=128,
                            help='size of RNN hidden state')
        self.add_argument('--num_layers', type=int, default=2,
                            help='number of layers in the RNN')
        self.add_argument('--batch_size', type=int, default=50,
                            help='minibatch size')
        self.add_argument('--seq_length', type=int, default=50,
                            help='RNN sequence length')
        self.add_argument('--num_epochs', type=int, default=50,
                            help='number of epochs')
        self.add_argument('--save_every', type=int, default=1000,
                            help='save frequency')
        self.add_argument('--grad_clip', type=float, default=5.,
                            help='clip gradients at this value')
        self.add_argument('--learning_rate', type=float, default=0.002,
                            help='learning rate')
        self.add_argument('--decay_rate', type=float, default=0.97,
                            help='decay rate for rmsprop')
        self.add_argument('--init_from', type=str, default=None,
                            help="""continue training from saved model at this path. Path must contain files saved by previous training process:
                                    'config.pkl'        : configuration;
                                    'chars_vocab.pkl'   : vocabulary definitions;
                                    'checkpoint'        : paths to model file(s) (created by tf).
                                                          Note: this file contains absolute paths, be careful when moving files around;
                                    'model.ckpt-*'      : file(s) with model definition (created by tf)
                                """)