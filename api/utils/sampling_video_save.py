# importing libraries
import cv2
import numpy as np
import math
import os
import shutil


def read_video(num_selected_frames, input_video = 0, sample = 1):
    """
    Input:
    num_selected_frames(int): number of frames selected from video
    input_video(mp4): input video
    sample(int): number of samples to generate from input_video
    
    Output:
    folder_names(array of string): list of folders containing images (1 sample = 1 folder)
    """
    cap = cv2.VideoCapture(input_video)   
  
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = num_selected_frames
    
    #length of gaps between frames
    z = math.floor(total_frames/(n-1))
    
    #baseline sequence 
    y = math.floor((total_frames - z*(n-1)) / 2)
    base_seq = range(y, y+(n-1)*z, z) # start = y, stop = y+(n-1)z, step = z
    result_arr = []
    
    folder_names = []
    for i in range(sample):
        sample_folder = str(os.path.splitext(os.path.basename(input_video))[0]) + '_sample_' + str(i)
        sample_folder = os.path.join('sample_folders', sample_folder)
        if os.path.exists(sample_folder):
            shutil.rmtree(sample_folder)
        os.makedirs(sample_folder)
        folder_names.append(sample_folder)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        random_seq = [np.random.randint(1, z) for j in range(n+1)] 
        result_seq = [sum(x) for x in zip(base_seq, random_seq)]
            
        for frame_pos in result_seq:        
            ret, frame = cap.read()
            if ret == True:
                cv2.imwrite(os.path.join(sample_folder,'frame_'+ str(frame_pos) +'.png'), frame)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)        
            else: 
                break
            
        print('Sequence', i, ' = ', result_seq)
        
    
    cap.release()   
    return folder_names


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(str(folder)):
        img = cv2.imread(os.path.join(str(folder),filename))
        if img is not None:
            img = cv2.cvtColor(cv2.flip(img,1), cv2.COLOR_BGR2RGB)
            images.append(img)
    return images

'''
#Driver code
#Create samples (1 sample  = 1 folder)
result = read_video(10,'vid30s.mp4', 2)

# WHEN GENERATING LARGE NUMBER OF SAMPLES, DO NOT LOAD EVERYTHING AT ONCE

#Loop through folder(sample) and load in
for i in range(len(result)):
    img_arr = load_images_from_folder(result[i])
    print(img_arr)
'''



