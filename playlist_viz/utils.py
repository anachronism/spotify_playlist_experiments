import numpy as np
from scipy.spatial.distance import cdist
import pandas as pd
import unicodedata
import re

#
def getExtrema(dfIn,categories,rangePrint):
    df_min = pd.DataFrame()
    df_max = pd.DataFrame()

    dfDownsel = dfIn.groupby(['Cluster']).mean()
    for cat in categories:
        df_sort = dfDownsel.sort_values(by=[cat],ascending = True)
        idxMin = df_sort.index[0]
        idxMax = df_sort.index[-1]
        df_min_tmp = dfIn[dfIn["Cluster"] == idxMin]
        df_min_tmp = df_min_tmp.assign(Category= [cat] * len(df_min_tmp.index))
        df_min_tmp = df_min_tmp.assign(Extrema= ["Min"] * len(df_min_tmp.index))
        df_max_tmp = dfIn[dfIn["Cluster"] == idxMax]
        df_max_tmp = df_max_tmp.assign(Category= [cat] * len(df_max_tmp.index))
        df_max_tmp = df_max_tmp.assign(Extrema= ["Max"] * len(df_max_tmp.index))


        df_min = df_min.append(df_min_tmp)
        df_max = df_max.append(df_max_tmp)

        #print(df_sort.index)
        minVals = df_sort.index[0:rangePrint].values
        maxVals = np.flip(df_sort.index[-rangePrint:].values)
        minStr = str(minVals)
        maxStr = str(maxVals)
        print("Min "+ cat + ": "+ minStr)
        #print(df_sort[cat].iloc[idxValsMin].values)
        print("Max "+ cat + ": "+ maxStr)
    return df_min,df_max
##### Parsing things
#return list of int values
def parseNodeInputStr(strIn, nClusters):
    inVals = strIn.split(',')

    # Have to decide how I want to handle error cases
    xInt = [int(x) for x in inVals]
    #	idx = np.where(xInt >= nClusters)
    print("NC:" + str(nClusters))
    print(xInt)
    xOut = [(nClusters-1) if (idx >= nClusters) else idx for idx in xInt]
    return xOut

# Cluster selection
def drawClusters(dfIn, nClustersOut = 6,distance = 'l2',centersAvoid = []):
    thresh = 20 # 20 for kmeans/tvne combo
    dfRange = dfIn[["x","y","z"]]
    npIn = np.array(dfRange)
    nClustersIn = npIn.shape[0]


    indDraw = [np.random.choice(range(nClustersIn))]

    clustersOut = np.zeros((nClustersOut,npIn.shape[1]))
    clustersOut[0,:] = npIn[indDraw[0],:]

    for ind in range(1,nClustersOut):
            npUse = np.tile(clustersOut[ind-1,:],(nClustersIn,1))#np.transpose([clustersOut[ind-1,:]] * nClustersIn)
            offsetPoints = (npUse - npIn)
            pointDist = np.apply_along_axis(np.linalg.norm,1,offsetPoints)
            indSelect = np.where(pointDist > thresh)
            indSelect = indSelect[0]
            #print(indSelect)
            valChosen = False
            while not valChosen:
                indAdd = np.random.choice(indSelect)
                if not (int(indAdd) in indDraw) and not(int(indAdd) in centersAvoid):
                    indDraw.append(indAdd)
                    clustersOut[ind,:] = npIn[indAdd,:]
                    valChosen = True

    return indDraw

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
