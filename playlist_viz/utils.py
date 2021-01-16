import numpy as np
from scipy.spatial.distance import cdist

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
				if not (int(indAdd) in indDraw):
					indDraw.append(indAdd)
					clustersOut[ind,:] = npIn[indAdd,:]
					valChosen = True

			#print(indDraw)			

	return indDraw,clustersOut

