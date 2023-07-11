import time
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Activation, Dropout, Flatten, Dense, BatchNormalization
# from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model
from keras.utils import load_img, img_to_array
from sklearn.metrics import accuracy_score
import tensorflow as tf
import numpy as np
import pandas as pd
import os
import time
from keras_applications.mobilenet_v3 import MobileNetV3
from .make_model import *

x = preparation()
ncheck = 5
def getime(func):
    def func_wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print("function {} completed in - {} seconds".format(
            func.__name__,
            time.time()-start_time))
    return func_wrapper

## TESTING FUNCTION
def prediction_final(ncheck, folder, model):
    pred_images_start = [] 
    pred_images_end = [] 

    ncheck = ncheck

    directory = dataset_path+folder+'/'
    predicted_label = []
    # print(_im,'Predicting',folder,'with',len([img for img in os.listdir(directory) if len(img)>2]),'images', end=' ')
    flag = np.zeros([ncheck])
    i = 0
    nothing = True
    for filename in [img for img in os.listdir(directory) if len(img)>2]:
        if filename.endswith(".jpg") or filename.endswith(".png"):
            start_time = time.time()
            img = load_img(directory+filename, target_size=(x.shape[0], x.shape[1]))
            img = img_to_array(img)
            img = np.expand_dims(img, axis=0)/255

            images = np.vstack([img])
            classes = model.predict(images)
            predicted_label.append(classes[0][0])

            if int(filename[:6])%1000==0:
                print('.', end=' ')

            if float(classes[0][0]) > 0.5: 
                flag[i] = 1
                i += 1
                if sum(flag) == ncheck:
                    print('')
                    pred_images_start.append(int(str(filename)[:6])-(ncheck-1))
                    pred_images_end.append(int(str(filename)[:6]))
                    print('-->',int(str(filename)[:6])-(ncheck-1),'({})'.format(filename[:-4]))                             
                    nothing = False
                    print()
                    break
            else:
                flag = np.zeros([ncheck])
                i = 0
    if nothing:
        pred_images_start.append(np.nan)
        pred_images_end.append(np.nan)  
                            
    return pred_images_start,pred_images_end

# test_df = pd.read_csv('storage/data/data_test_val_final2.csv')
# test_df = test_df[test_df.foldername.isin(df.foldername.values)]

# list_folder_for_validation = [__ for __ in test_df.foldername.values]
# list_folder_for_test = list_folder_for_validation
    
### LOAD IMAGE AND LABEL DATA
# def load_data(path,folder,shuffle=False):
#     train_data = np.zeros([len(images_data),x.shape[0],x.shape[1],3]) 
#     y = np.zeros([len(images_data),1])
    
#     img_ids = np.arange(len(images_data))

#     if shuffle:
#         np.random.shuffle(img_ids)

#     for i in img_ids:
#         image_path = source_path + images_data[i][0] + '/' + images_data[i][1] 
#         image = cv2.imread(image_path, 1) 
#         b,g,r = cv2.split(image) 
#         image = cv2.merge([r,g,b]) 
#         image = cv2.resize(image, (x.shape[1], x.shape[0]))
#         image = image/255.0 
        
#         train_data[i,:,:,:] = image
#         y[i,:] = images_data[i][2]

#     return train_data,y.astype(int),img_ids

@getime
def predict(folder):
    folders = folder + 'crop'
    lst = [].append(folders)
    # X_test,y_test,img_test_ids = load_data(dataset_path, lst)
    
    model_save_path = 'storage/hasil_predict/'
    
    model = make_model(base="cnn")
    output_names = ["loss","accuracy","f1_m","precision_m", "recall_m"]
    model.load_weights("storage/model/CNN_parival_5_6_ENZ_final_all_ep50_batch4_1_best.h5")
    
    for check in range(1,ncheck+1):
        ### Predict
        # print('###',check,'###')
        pred_images_start,pred_images_end = prediction_final(check,folders,model) # Fungsi Prediction Final
                
        ### Save CSV 
        df_save = pd.DataFrame()
        df_save['filename'] = folder
        df_save['flag_start'] = pred_images_start
        df_save['flag_end'] = pred_images_end
        # df_save['second_start'] = df_save.apply(lambda x: round((x['flag_start']-(int(df[df.filename==x['filename']].PA_start_real.values)+(PA_start*20)))*0.05,2),axis=1)
        # df_save['second_end'] = df_save.apply(lambda x: round((x['flag_end']-(int(df[df.filename==x['filename']].PA_start_real.values)+(PA_start*20)))*0.05,2),axis=1)
        df_save.to_csv(model_save_path+'/Hasil_test_PA_{}_{}_Check{}_best.csv'.format(PA_start,PA_end,check),index=False)
