import cv2
import mediapipe as mp
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import math
from functools import reduce
from .sampling_video_save import *

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


def data_gen(folders, labels, max_sequence_length=10, batch_size = 1):
  '''
    max_sequence_length: the maximum length for each sequence generated
    sample: list of samples, each is list of frames, each frame of shape (height, width, 3)
    return 
      a generator, each time it yields a batch of samples
  '''
  num_batches = len(folders) // batch_size
  Xs = []
  label_lst = []
  for i in range(num_batches):
    try:
      X = np.zeros((batch_size, max_sequence_length, 126))
      # range of folders to take
      start_idx = i * batch_size
      end_idx = (i+1) * batch_size
      # extract (batch_size) numbers of samples (each sample contains list of frames)
      list_frames = [load_images_from_folder(folder) for folder in folders[start_idx:end_idx]]
    
      # extract landmark
      for j, frames in enumerate(list_frames):
        X[j] = extract_landmarks(frames, max_sequence_length)
      
    #   yield X
      if len(Xs) == 0:
        Xs = X
      else:
        Xs = np.vstack((Xs, X))
      label_lst += labels[start_idx:end_idx]
    except Exception as e:
      print(e)
  return Xs, label_lst

def preprocess(folders, max_sequence_length=10, batch_size = 1):
  '''
    max_sequence_length: the maximum length for each sequence generated
    sample: list of samples, each is list of frames, each frame of shape (height, width, 3)
    return 
      a generator, each time it yields a batch of samples
  '''
  num_batches = len(folders) // batch_size
  Xs = []
  for i in range(num_batches):
    try:
      X = np.zeros((batch_size, max_sequence_length, 126))
      # range of folders to take
      start_idx = i * batch_size
      end_idx = (i+1) * batch_size
      # extract (batch_size) numbers of samples (each sample contains list of frames)
      list_frames = [load_images_from_folder(folder) for folder in folders[start_idx:end_idx]]
    
      # extract landmark
      for j, frames in enumerate(list_frames):
        X[j] = extract_landmarks(frames, max_sequence_length)
      
    #   yield X
      if len(Xs) == 0:
        Xs = X
      else:
        Xs = np.vstack((Xs, X))
    except Exception as e:
      print(e)
  return Xs
  

def extract_landmarks(frames, sequence_length):
  '''
    frames: list of frames in one sample: (height, width)
    sequence_length: the fixed size sequence length, zeros pad if a sequence is shorter
		return:
			array of shape (sequence_length, 126)
  '''
  n = len(frames)
  X = np.zeros((n,126))

  with mp_hands.Hands(
      model_complexity=1,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5, max_num_hands=1) as hands:
    i = 0
    for frame in frames:
      height, width, _ = frame.shape
      # key_points = []
      left_hand = [0] * 63
      right_hand = [0] * 63
      frame.flags.writeable = False
      handednesses = []
      results = hands.process(frame)
      frame.flags.writeable = True
      image = cv2.cvtColor(cv2.flip(frame,1), cv2.COLOR_RGB2BGR)
      
      if results.multi_handedness:
        for handedness in results.multi_handedness:
          if handedness.classification[0].score >= 0.5:
              handednesses.append(handedness.classification[0].label)
      # print(handednesses)
      if results.multi_hand_landmarks:    
        for idx,hand_landmarks in enumerate(results.multi_hand_landmarks):
          if idx < len(handednesses):
            if handednesses[idx] == 'Left':
              left_hand = reduce(lambda x, lm: x + [lm.x * width, lm.y * height, lm.z], hand_landmarks.landmark, [])
            elif handednesses[idx] == 'Right':
              right_hand = reduce(lambda x, lm: x + [lm.x * width, lm.y * height, lm.z], hand_landmarks.landmark, [])

        X[i] = np.array(left_hand + right_hand)
        i += 1

        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.imwrite('image.png',image)

  # feature normalization
  for j in range(X.shape[1]):
    if X[:,j].std() != 0:
      X[:,j] = (X[:,j] - X[:,j].mean()) / X[:,j].std()

  # zero padding if the sequence received is shorter
  if X.shape[0] < sequence_length:
    X = np.concatenate( (np.zeros((sequence_length - X.shape[0], 126)), X), axis=0)
  return X



#Driver code
# folders = read_video(10,'vid30s.mp4', 10)
# folders = ['vid30s_sample_0', 'vid_30s_sample_1']

# preprocessing for each sample videos
# train_ds = data_gen(folders, batch_size=2)
# print(next(train_ds).shape)
# print(next(train_ds).shape)
# print(next(train_ds).shape)
# print(next(train_ds).shape)
# print(next(train_ds).shape)
# print(next(train_ds).shape)
# for i in range(10):
#   print(X_train[0][i])
# print(X_train.shape)
