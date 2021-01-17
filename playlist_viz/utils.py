import numpy as np
from scipy.spatial.distance import cdist

##### Parsing things
#return list of int values
def parseNodeInputStr(strIn, nClusters):
	inVals = strIn.split(',')	

	# Have to decide how I want to handle error cases
	xInt = [int(x) for x in inVals]
#	idx = np.where(xInt >= nClusters)
	xOut = [(nClusters-1) if (idx >= nClusters) else idx for idx in xInt]
	return xOut

# Cluster selection
def drawClusters(npIn, nClustersOut = 6,distance = 'l2'):
	thresh = 20
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

			valChosen = False
			while not valChosen:
				indAdd = np.random.choice(indSelect)
				#print(indAdd)
				if not (int(indAdd) in indDraw):
					indDraw.append(indAdd)
					clustersOut[ind,:] = npIn[indAdd,:]
					valChosen = True

			#print(indDraw)			

	return indDraw,clustersOut

