'''Trains a simple binarize CNN on the MNIST dataset.
Modified from keras' examples/mnist_mlp.py
Gets to 98.98% test accuracy after 20 epochs using tensorflow backend
'''

from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

import keras.backend as K
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, BatchNormalization, MaxPooling2D
from keras.layers import Flatten
from tensorflow.keras.optimizers import SGD, Adam, RMSprop
from keras.callbacks import LearningRateScheduler
from keras.utils import np_utils

from binary_ops import binary_tanh as binary_tanh_op
from binary_layers import BinaryDense, BinaryConv2D
from binary_ops import binarize



def binary_tanh(x):
    return binary_tanh_op(x)


H = 1.
kernel_lr_multiplier = 'Glorot'

# nn
batch_size = 50
epochs = 20 
channels = 1
img_rows = 28 
img_cols = 28 
filters = 32 
kernel_size = (3, 3)
pool_size = (2, 2)
hidden_units = 128
classes = 10
use_bias = False

# learning rate schedule
lr_start = 1e-3
lr_end = 1e-4
lr_decay = (lr_end / lr_start)**(1. / epochs)

# BN
epsilon = 1e-6
momentum = 0.9

# dropout
p1 = 0.25
p2 = 0.5

# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = mnist.load_data()

# X_train = X_train.reshape(60000, 1, 28, 28)
# X_test = X_test.reshape(10000, 1, 28, 28)
X_train = X_train.reshape(60000, 1, 28, 28)
X_test = X_test.reshape(10000, 1, 28, 28)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, classes) * 2 - 1 # -1 or 1 for hinge loss
Y_test = np_utils.to_categorical(y_test, classes) * 2 - 1


model = Sequential()
# conv1
model.add(BinaryConv2D(128, kernel_size=kernel_size, input_shape=(channels, img_rows, img_cols),
                       data_format='channels_first',
                       H=H, kernel_lr_multiplier=kernel_lr_multiplier, 
                       padding='same', use_bias=use_bias, name='conv1'))
model.add(BatchNormalization(epsilon=epsilon, momentum=momentum, axis=1, name='bn1'))
model.add(Activation(binary_tanh, name='act1'))

# # conv2
# model.add(BinaryConv2D(128, kernel_size=kernel_size, H=H, kernel_lr_multiplier=kernel_lr_multiplier, 
#                        data_format='channels_first',
#                        padding='same', use_bias=use_bias, name='conv2'))
# model.add(MaxPooling2D(pool_size=pool_size, name='pool2', data_format='channels_last'))
# model.add(BatchNormalization(epsilon=epsilon, momentum=momentum, axis=1, name='bn2'))
# model.add(Activation(binary_tanh, name='act2'))

# # conv3
# model.add(BinaryConv2D(256, kernel_size=kernel_size, H=H, kernel_lr_multiplier=kernel_lr_multiplier,
#                        data_format='channels_first',
#                        padding='same', use_bias=use_bias, name='conv3'))
# model.add(BatchNormalization(epsilon=epsilon, momentum=momentum, axis=1, name='bn3'))
# model.add(Activation(binary_tanh, name='act3'))

# # conv4
# model.add(BinaryConv2D(256, kernel_size=kernel_size, H=H, kernel_lr_multiplier=kernel_lr_multiplier,
#                        data_format='channels_first',
#                        padding='same', use_bias=use_bias, name='conv4'))
# model.add(MaxPooling2D(pool_size=pool_size, name='pool4', data_format='channels_last'))
# model.add(BatchNormalization(epsilon=epsilon, momentum=momentum, axis=1, name='bn4'))
# model.add(Activation(binary_tanh, name='act4'))

model.add(Flatten())

# dense1
model.add(Dense(128, activation='relu'))
# model.add(BinaryDense(128, H=H, kernel_lr_multiplier=kernel_lr_multiplier, use_bias=use_bias, name='dense5'))
model.add(BatchNormalization(epsilon=epsilon, momentum=momentum, name='bn5'))
# model.add(Activation(binary_tanh, name='act5'))

# dense2
model.add(Dense(10, activation='softmax'))
# model.add(BinaryDense(classes, H=H, kernel_lr_multiplier=kernel_lr_multiplier, use_bias=use_bias, name='dense6'))
# model.add(BatchNormalization(epsilon=epsilon, momentum=momentum, name='bn6'))

# opt = Adam(learning_rate=lr_start) 
opt = Adam() 
model.compile(loss='squared_hinge', optimizer=opt, metrics=['acc'])
model.summary()

# 把weight轉出來
# 轉成num.py

from keras import callbacks
lr_scheduler = LearningRateScheduler(lambda e: lr_start * lr_decay ** e)
history = model.fit(X_train, Y_train,
                    batch_size=50, epochs=1,
                    verbose=1, validation_data=(X_test, Y_test))
score = model.evaluate(X_test, Y_test, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])


# 把 non_binarize weight 與 binarize weight 分別印出
print('=====================================NON_BINARIZE=======================================')
print(model.layers[0].get_weights())
binary_kernel = binarize(model.layers[0].kernel, H=model.layers[0].H) 
print('=======================================BINARIZE=========================================')
print('BINARIZE')
print(binary_kernel)

# 輸出成.txt檔
array = binary_kernel.numpy()
dk1_f = open('dk1.txt', 'a')
for i in range(len(binary_kernel)):
  dk1_f.write(str(array[i]) + '\n')
dk1_f.close()