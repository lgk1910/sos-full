from keras.layers import Lambda
from keras import backend as K
import pandas as pd
import tensorflow as tf
from tensorflow.keras.utils import plot_model
import numpy as np
import cv2
import numpy as np
import uuid
import os
from functools import reduce
import glob
from tqdm import tqdm
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from utils.preprocess import data_gen, preprocess
from utils.sampling_video_save import *

NUM_SELECTED_FRAMES = 30
NUM_SAMPLE = 1

class SOSign:
    def __init__(self, model_path='models/sign2text.h5', tokenizer_path='tokenizers/tokenizer.pickle'):
        self.model = tf.keras.models.load_model(model_path)
        with open(tokenizer_path, 'rb') as f:
            self.tokenizer = pickle.load(f)

        self.REVERSE_WORD_INDEX = {}
        for key in self.tokenizer.word_index:
            self.REVERSE_WORD_INDEX[self.tokenizer.word_index[key]] = key
        self.num_token = len(self.tokenizer.word_index)

    def reformat_input(self, files):
        labels = []
        samples = []
        for i, file_ in tqdm(enumerate(files)):
            print(i, file_)
            try:
                if i == 0:
                    tmp = read_video(NUM_SELECTED_FRAMES, file_, NUM_SAMPLE)
                    samples = tmp
                else:
                    tmp = read_video(NUM_SELECTED_FRAMES, file_, NUM_SAMPLE)
                    samples = np.concatenate([samples, tmp])
            except:
                pass

        if len(samples) == 0:
            return None

        input_data = preprocess(samples, max_sequence_length=NUM_SELECTED_FRAMES)
        return input_data

    def infer(self, files):
        out_status = 0
        try:
            # Preprocessing data
            encoder_input = self.reformat_input(files)
            decoder_input = np.array([np.identity(self.num_token)[[1]] for seq in range(encoder_input.shape[0])])

            # Inference
            output = self.model.predict([encoder_input, decoder_input])
            predicted_seqs = []
            for out in output:
                predicted_seq = 'sos'
                for tok in out:
                    predicted_tok = self.REVERSE_WORD_INDEX[np.argmax(tok)]
                    predicted_seq += ' ' + predicted_tok
                    if predicted_tok == 'eos':
                        predicted_seqs.append(predicted_seq)
                        break

            if len(predicted_seqs) == 0:
                out_status = 1

            return predicted_seqs, out_status
        except:
            return [], 1
