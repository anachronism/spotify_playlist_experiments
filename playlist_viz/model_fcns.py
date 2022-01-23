# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 20:58:20 2021

@author: Max
"""

'''
SCore metric possiblities
silhouette
    Bounded between -1 and 1
clalinski_harabasz
    Quick
davies_bouldin_score
    Quick but limited to L2
'''

from sklearn.preprocessing import StandardScaler
from  sklearn.manifold import TSNE, Isomap
from sklearn.cluster import SpectralClustering,OPTICS,AgglomerativeClustering,MiniBatchKMeans
from sklearn.metrics import silhouette_score,davies_bouldin_score # calinski_harabasz_score,

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def dimReduce(df_in,n_components):
    scaler = StandardScaler()
    np_clust_pool = scaler.fit_transform(df_in)
    ## Dimensionality reduction.
    dimRedModel = TSNE(n_components = n_components,init='pca',n_jobs=-1)
 #   dimRedModel = Isomap(n_components=n_components,n_jobs =-1)
    return dimRedModel.fit_transform(np_clust_pool)


def dimReduce_test(df_in,n_components):
    import keras
    from keras import layers,regularizers
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from keras.callbacks import TensorBoard

    scaler = StandardScaler()
    np_clust_pool = scaler.fit_transform(df_in)
    ## Dimensionality reduction.

    #define layers
    encoding_dim = n_components
    inSize = df_in.shape[1]
    input_vec = keras.Input(shape=(inSize,))
    encoded = layers.Dense(encoding_dim,activation='relu')(input_vec) # ,activity_regularizer = regularizers.l1(10e-5)
    encoded_input = keras.Input(shape=(encoding_dim,))
    decoded = layers.Dense(inSize,activation='sigmoid')(encoded)
    #define models.
    autoencoder = keras.Model(input_vec,decoded)
    encoder = keras.Model(input_vec,encoded)
    decoder_layer = autoencoder.layers[-1]
    decoder=keras.Model(encoded_input, decoder_layer(encoded_input))
    autoencoder.compile(optimizer='adam',loss='binary_crossentropy') ###NOTE: reinvestigate loss function.
    x_train,x_test = train_test_split(np_clust_pool)
    # tensorboard --logdir=/tmp/autoencoder
    autoencoder.fit(x_train,x_train,
                    epochs=50,batch_size=128,shuffle=True,
                    validation_data=(x_test,x_test),
                    callbacks=[TensorBoard(log_dir="/tmp/autoencoder")])
    embedded_pool = encoder.predict(np_clust_pool)
    print(embedded_pool)

    return embedded_pool
# Check learning_rate,


def runClustering(dfIn,maxNumClusters = 1000,findClusterCount = True,showPlot = True):
    # Takes a dataframe in, must have columns x, y, and z.

    dimsAccess = ["x","y","z"]
    npIn = dfIn[dimsAccess]

    if isinstance(maxNumClusters,list):
        rangeSearch = range(maxNumClusters[0],maxNumClusters[1])
        silScore = np.ones((maxNumClusters[1]-maxNumClusters[0],)) * 2
    else:
        rangeSearch = range(1,maxNumClusters)
        silScore = np.ones((maxNumClusters-1,)) * 500

    #silScore = np.zeros((10,))
    #sc = OPTICS(min_samples=100,n_jobs=-1)

    splitVals = []
    if findClusterCount:
        idxSave = 0
        for ind in rangeSearch:
            sc = MiniBatchKMeans(n_clusters = ind+1)
            splitVals.append(sc.fit_predict(npIn))
            silScore[idxSave] = davies_bouldin_score(npIn,splitVals[idxSave])
            # silScore[ind-1] = silhouette_score(npIn,splitVals[ind-1])
            print("Cluster count "+ str(ind+1) + ": " + str(silScore[idxSave]))
            idxSave = idxSave + 1
        idxUse = np.argmin(silScore)
        valsUse = splitVals[idxUse]
        idxUse = rangeSearch[idxUse]
        if showPlot:
            sns.lineplot(data=silScore)
            plt.show()
    else:
        idxUse = maxNumClusters
        sc = MiniBatchKMeans(n_clusters = idxUse)
        valsUse = sc.fit_predict(npIn)


    dfOut = dfIn
    dfOut["Cluster"] = valsUse

    return dfOut, idxUse
