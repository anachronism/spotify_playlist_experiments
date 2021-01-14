# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 20:58:20 2021

@author: Max
"""
from  sklearn.manifold import TSNE, Isomap
from sklearn.preprocessing import StandardScaler

def dimReduce(df_in):
    scaler = StandardScaler()
    np_clust_pool = scaler.fit_transform(df_in)
    ## Dimensionality reduction.
    dimRedModel = TSNE()
   # dimRedModel = Isomap(n_components=2,n_jobs =-1)
    return dimRedModel.fit_transform(np_clust_pool)