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

# Check learning_rate,  


def runClustering(dfIn,maxNumClusters = 1000,findClusterCount = True):
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
        sns.lineplot(data=silScore)
        plt.show()
    else:
        idxUse = maxNumClusters
        sc = MiniBatchKMeans(n_clusters = idxUse)
        valsUse = sc.fit_predict(npIn)


    dfOut = dfIn
    dfOut["Cluster"] = valsUse

    return dfOut, idxUse

