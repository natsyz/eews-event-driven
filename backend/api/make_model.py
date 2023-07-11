from keras.models import *
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, Input
from keras.layers import Activation, Dropout, Flatten, Dense, BatchNormalization
from keras.optimizers import Adam
import cv2
import matplotlib.pyplot as plt
from keras.utils import load_img, img_to_array

# IMAGES PATH
dataset_path = 'plot-waveform/crop_ENZ/'

def preparation():
    # GET IMAGE SIZE FROM DATASET
    img = load_img(dataset_path+'20090118_064750crop/'+'000000_20090118_064750_crop.png')
    x = img_to_array(img)
    x = cv2.resize(x, (192, 256))
    return x

PA_start = 5
PA_end = 6

NonPA_times = 20
NonPA_start = -200
NonPA_end = 100

NonPA_times_close = 4
NonPA_start_close = -17 
NonPA_end_close = -1

NonPA_times_close2 = 40
NonPA_start_close2 = 100
NonPA_end_close2 = 200

# DEFINE CUSTOM NAME (name is given manually after the model name and PA position)
custom_name = "ENZ_final_all_ep50_batch4_1"

# ADDITIONAL METRIC FUNCTIONS
from keras import backend as K

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

# MODEL BUILD FUNCTION
def make_model(base="", custom_name=custom_name):
    x = preparation()
    m_ = None
    model_name = base.upper() + "_parival_"  
    model_name = model_name + "_".join([str(PA_start),str(PA_end)])

    if base.lower()=="cnn":
        ### FOR CNN MODELS ###

        base_model = Sequential()
        base_model.add(Conv2D(32, (3, 3), input_shape=(x.shape[0], x.shape[1], 3)))
        base_model.add(BatchNormalization())
        base_model.add(Activation('relu'))
        base_model.add(MaxPooling2D(pool_size=(2, 2)))

        base_model.add(Conv2D(64, (3, 3)))
        base_model.add(BatchNormalization())
        base_model.add(Activation('relu'))
        base_model.add(MaxPooling2D(pool_size=(2, 2)))

        base_model.add(Conv2D(128, (3, 3)))
        base_model.add(BatchNormalization())
        base_model.add(Activation('relu'))
        base_model.add(MaxPooling2D(pool_size=(2, 2)))

        base_model.add(Conv2D(256, (3, 3)))
        base_model.add(BatchNormalization())
        base_model.add(Activation('relu'))
        base_model.add(MaxPooling2D(pool_size=(2, 2)))

        base_model.add(Flatten()) 
        base_model.add(Dense(1024))
        base_model.add(Activation('relu'))
        base_model.add(Dense(512))
        base_model.add(Activation('relu'))
        base_model.add(Dense(128))
        base_model.add(Activation('relu'))
        m_ = base_model.output

        ### --------------- ###

    elif base.lower()=="mobilenetv3":
        ### FOR MOBILENETV3 ###

        import keras
        from keras.applications import keras_applications
        from keras_applications.mobilenet_v3 import MobileNetV3Large, MobileNetV3Small

        base_model = MobileNetV3Large(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet', backend=keras.backend, layers=keras.layers, models=keras.models, utils=keras.utils) #RGB 3, grayscale 1

        # RENAME LAYER TO SOLVE THE PROBLEM WHEN SAVING THE MODEL
        for i, layer in enumerate(base_model.layers[1:]):
            layer.name = 'layer_' + str(i) + '_' + layer.name

        m_ = base_model.output

        m_ = GlobalAveragePooling2D()(m_)
        m_ = Dense(1024,activation='relu')(m_) #we add dense layers so that the model can learn more complex functions and classify for better results.
        m_ = Dense(512,activation='relu')(m_) #dense layer 2
        m_ = Dense(256,activation='relu')(m_) #dense layer 3
        
        ### --------------- ###
    elif base.lower()[:-1]=="efficientnetb":
        ### FOR EFFICIENTNET ###
        import keras
        from efficientnet.keras import EfficientNetB0,EfficientNetB1
        from efficientnet.keras import EfficientNetB2,EfficientNetB3
        from efficientnet.keras import EfficientNetB4,EfficientNetB5

        EFMODEL = {}
        EFMODEL['efficientnetb0'] = EfficientNetB0(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet') #RGB 3, grayscale 1
        EFMODEL['efficientnetb1'] = EfficientNetB1(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet') #RGB 3, grayscale 1
        EFMODEL['efficientnetb2'] = EfficientNetB2(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet') #RGB 3, grayscale 1
        EFMODEL['efficientnetb3'] = EfficientNetB3(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet') #RGB 3, grayscale 1
        EFMODEL['efficientnetb4'] = EfficientNetB4(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet') #RGB 3, grayscale 1
        EFMODEL['efficientnetb5'] = EfficientNetB5(input_shape=(x.shape[0], x.shape[1], 3), include_top=False, weights='imagenet') #RGB 3, grayscale 1

        base_model = EFMODEL[base.lower()]
        # RENAME LAYER TO SOLVE THE PROBLEM WHEN SAVING THE MODEL
        for i, layer in enumerate(base_model.layers[1:]):
            layer.name = 'layer_' + str(i) + '_' + layer.name

        m_ = base_model.output

        m_ = GlobalAveragePooling2D()(m_)
        m_ = Dense(1024,activation='relu')(m_) #we add dense layers so that the model can learn more complex functions and classify for better results.
        m_ = Dense(512,activation='relu')(m_) #dense layer 2
        m_ = Dense(256,activation='relu')(m_) #dense layer 3
        
        ### --------------- ###
    else:
        print("Model Definition Error")
    
    outputs = Dense(1, activation = 'sigmoid')(m_) #final layer with sigmoid activation
        
    model = Model(inputs=base_model.input, outputs=outputs) 
    
    model.compile(optimizer=Adam(1e-4),
                  loss="binary_crossentropy",   
                  metrics=["accuracy",f1_m,precision_m, recall_m])
    
    model._name = model_name if custom_name is "" else model_name + "_" + custom_name
    
    return model