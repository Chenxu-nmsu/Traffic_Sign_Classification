# -*- coding: utf-8 -*-
"""Traffic_Sign_Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Gped5FMZlq9_xBKfou3tdyBoKJVkQ86d
"""

# from google.colab import drive
# drive.mount('/content/gdrive')

# import tensorflow as tf
# tf.test.gpu_device_name()

# import os
# os.chdir('../content/gdrive/My Drive/Colab Notebooks/traffic-signs-data/')
# print(os.getcwd())

"""# STEP 1: IMPORT LIBRARIES AND LOAD DATASET"""

# import libraries 
import warnings
warnings.filterwarnings("ignore")
import pickle
import seaborn as sns
import pandas as pd # Import Pandas for data manipulation using dataframes
import numpy as np # Import Numpy for data statistical analysis 
import matplotlib.pyplot as plt # Import matplotlib for data visualisation
import random
from time import process_time
import argparse

# add arguments
parser = argparse.ArgumentParser()

# parameters 
parser.add_argument('--image', help='color or grey', type=str)

args = parser.parse_args()
args = vars(parser.parse_args())

# The pickle module implements binary protocols for serializing and de-serializing a Python object structure.
with open("train.p", mode='rb') as training_data:
    train = pickle.load(training_data)
with open("valid.p", mode='rb') as validation_data:
    valid = pickle.load(validation_data)
with open("test.p", mode='rb') as testing_data:
    test = pickle.load(testing_data)

# original dataset
X_train, y_train = train['features'], train['labels']
X_validation, y_validation = valid['features'], valid['labels']
X_test, y_test = test['features'], test['labels']
X_test_color = X_test

# Check data shape
print(X_train.shape)
print(y_train.shape)
print(X_validation.shape)
print(y_validation.shape)
print(X_test.shape)
print(y_test.shape)



"""# STEP 2: CHECK DATASET (LABEL DISTRIBUTION)"""

unique,count = np.unique(y_train,return_counts=True)
data_count = dict(zip(unique,count))
fig, ax = plt.subplots(figsize=(4,3))
plt.bar(data_count.keys(), data_count.values(), color='g')
ax.set_title('Statistics of train labels')
plt.savefig('Statistics of train labels.pdf', dpi=600)

unique,count = np.unique(y_test,return_counts=True)
data_count = dict(zip(unique,count))
fig, ax = plt.subplots(figsize=(4,3))
plt.bar(data_count.keys(), data_count.values(), color='g')
ax.set_title('Statistics of test labels')
plt.savefig('Statistics of test labels.pdf', dpi=600)

unique,count = np.unique(y_validation,return_counts=True)
data_count = dict(zip(unique,count))
fig, ax = plt.subplots(figsize=(4,3))
plt.bar(data_count.keys(), data_count.values(), color='g')
ax.set_title('Statistics of validation labels')
plt.savefig('Statistics of validation labels.pdf', dpi=600)

"""# STEP 3: IMAGE VISUALIZATIONS"""

import matplotlib.pyplot as plt
import numpy as np
fig, axs = plt.subplots(4, 4, sharex=True, sharey=True)
fig.set_size_inches(10, 10, forward=True)
fig.tight_layout(pad=1.0)

for i in range(4):
    for j in range(4):
        axs[i, j].imshow(X_train[100*i + 100*j])
        axs[i, j].set_title('Label: {}'.format(y_train[100*i + 100*j]))
plt.show()

"""# STEP 4: DATA PREPROCESSING"""
## Shuffle the dataset 
from sklearn.utils import shuffle
import tensorflow as tf
tf.random.set_seed(1)
X_train, y_train = shuffle(X_train, y_train)

if args['image'] == 'color':
    ## normalization
    X_train_norm = (X_train - 128)/128 
    X_test_norm = (X_test - 128)/128
    X_validation_norm = (X_validation - 128)/128

    X_train = X_train_norm
    X_test = X_test_norm
    X_validation = X_validation_norm

else:
    ## transfer to gray images
    X_train_gray = np.sum(X_train/3, axis=3, keepdims=True)
    X_test_gray  = np.sum(X_test/3, axis=3, keepdims=True)
    X_validation_gray  = np.sum(X_validation/3, axis=3, keepdims=True)

    ## normalization
    X_train_gray_norm = (X_train_gray - 128)/128 
    X_test_gray_norm = (X_test_gray - 128)/128
    X_validation_gray_norm = (X_validation_gray - 128)/128

    X_train = X_train_gray_norm
    X_test = X_test_gray_norm
    X_validation = X_validation_gray_norm

    # show color and grey images
    i = 620
    fig, ax = plt.subplots(1,2,figsize=(3,3))
    ax[1].imshow(X_train_gray[i].squeeze(), cmap='gray')
    ax[1].set_title('X_train_gray')
    ax[0].imshow(X_train[i].squeeze())
    ax[0].set_title('X_train')
    fig.tight_layout()
    fig.savefig('image_show_styles.pdf', dpi=600)
    plt.show()

"""# STEP 5: MODEL IMPLEMENTATION

The model consists of the following layers:

STEP 1: THE FIRST CONVOLUTIONAL LAYER #1
Input = 32x32x1
Output = 28x28x6
Output = (Input-filter+1)/Stride* => (32-5+1)/1=28
Used a 5x5 Filter with input depth of 3 and output depth of 6
Apply a RELU Activation function to the output
pooling for input, Input = 28x28x6 and Output = 14x14x6

STEP 2: THE SECOND CONVOLUTIONAL LAYER #2
Input = 14x14x6
Output = 10x10x16
Layer 2: Convolutional layer with Output = 10x10x16
Output = (Input-filter+1)/strides => 10 = 14-5+1/1
Apply a RELU Activation function to the output
Pooling with Input = 10x10x16 and Output = 5x5x16

STEP 3: FLATTENING THE NETWORK
Flatten the network with Input = 5x5x16 and Output = 400

STEP 4: FULLY CONNECTED LAYER
Layer 3: Fully Connected layer with Input = 400 and Output = 120
Apply a RELU Activation function to the output

STEP 5: DROPOUT LAYER

STEP 6: ANOTHER FULLY CONNECTED LAYER
Layer 4: Fully Connected Layer with Input = 120 and Output = 84
Apply a RELU Activation function to the output

STEP 7: FULLY CONNECTED LAYER
Layer 5: Fully Connected layer with Input = 84 and Output = 43
"""

# Import train_test_split from scikit library
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, Dense, Flatten, Dropout
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split

if args['image'] == 'color':
    input_shape = (32,32,3)
else:
    input_shape = (32,32,1)

# CREATE THE CNN
cnn_model = Sequential()

cnn_model.add(Conv2D(filters=6, kernel_size=(5, 5), activation='relu', input_shape=input_shape))
cnn_model.add(AveragePooling2D())

cnn_model.add(Conv2D(filters=16, kernel_size=(5, 5), activation='relu'))
cnn_model.add(AveragePooling2D())

cnn_model.add(Flatten())

cnn_model.add(Dense(units=120, activation='relu'))

# add dropout to prevent overfitting
cnn_model.add(Dropout(rate=0.5))

cnn_model.add(Dense(units=84, activation='relu'))

cnn_model.add(Dense(units=43, activation = 'softmax'))

# COMPILE THE MODEL
cnn_model.compile(loss ='sparse_categorical_crossentropy', optimizer=Adam(lr=0.001),metrics =['accuracy'])
print(cnn_model.summary())

# record initial time
start = process_time()

# MODEL TRAINING
history = cnn_model.fit(X_train,
                        y_train,
                        batch_size=500,
                        nb_epoch=50,
                        verbose=1,
                        validation_data = (X_validation,y_validation))

# calculate the time elapse
elapse = process_time() - start

print('Running time: {0:.5f} s'.format(elapse))

"""# STEP 6: MODEL EVALUATION"""

score = cnn_model.evaluate(X_test, y_test,verbose=0)
print('Test Accuracy : {:.4f}'.format(score[1]))

# PLOT ACCURACY CURVE
accuracy = history.history['accuracy']
val_accuracy = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(accuracy))
plt.figure(figsize=(4,3))
plt.plot(epochs, accuracy, 'b', ls = '--', label='Training Accuracy')
plt.plot(epochs, val_accuracy, 'b', label='Validation Accuracy')
plt.title('Training and Validation accuracy')
plt.legend()
plt.savefig('Training and validation accuracy.pdf', figsize=(3, 3), dpi=600)
plt.show()

# PLOT LOSS CURVE
plt.figure(figsize=(4,3))
plt.plot(epochs, loss, 'b', ls = '--', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend()
plt.savefig('Training and validation loss.pdf', figsize=(3, 3), dpi=600)
plt.show()

# Get the predictions for the test data
predicted_classes = cnn_model.predict_classes(X_test)
# Get the indices to be plotted
y_true = y_test

# SHOW SAMPLE PREDICTIONS
L = 3
W = 3
fig, axes = plt.subplots(L, W, figsize = (4,4))
axes = axes.ravel()

for i in np.arange(0, L * W):  
    axes[i].imshow(X_test_color[i])
    axes[i].set_title("Pred={}\n True={}".format(predicted_classes[i], y_true[i]))
    axes[i].axis('off')

plt.subplots_adjust(wspace=1)
plt.savefig('Predicted and true labels.pdf', figsize=(3, 3), dpi=600)