# Visualization improvements
## Plots to add 
* Min/max clusters for each type. Select type from drop down menu, or show all of them.
* Slider to determine size of cluster that we care about.
* Plot ephemera clusters.
* for active cluster, show the average of the spotify features for the cluster.
* Maybe hover mode stuff.
## Cluster size analysis
* Get closest cluster to currently active on second pane
* Pull largest clusters
* Group ephemera together, cluster that ephemera again.

## Better tool use
* Genre List/representation, able to select down clusters by genre.
* Search corpus if song is in there.
* Get number of songs liked on playlist, return for discover weeklies
    * Cull playlists with most liked at beginning, move up playlists with most liked at end (Maybe keep new likes list?). 
* List, sorted by various parameters, selectable.

## Plot efficiency
* Make each cluster a different trace so that it might be easier to update the figure.

# Algorithm improvements
* Look into autoencoders for embedding.
    * Pull in own playlists to look at how they look in the embedding.
* Split out the viz from the processing.
 