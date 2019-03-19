# Adjacency matrix based implementation of Dijkstra's algorithm
import math
import numpy as np

# takes the adj matrix of the network and source node as arguments
# returns
def dijkstras(mat, src):
    # number of vertices in the graph
    verts = len(mat)
    print (verts)

    # init distances to max int other than the source
    dist = [math.inf] * verts
    dist[src] = 0
    sptSet = [False] * verts
    
    # init parent array to store shortest path tree
    parent = [-1] * verts

    for cout in range(verts):

        # pick min distance vert from those not processed
        # u is always equal to src in first iteration
        u = minDistance(dist, sptSet, verts)

        # put min distance vert in the shortest path tree
        sptSet[u] = True

        # update dist value of the neighbors of the picked vert
        # if the current distance is greater than new distance and
        # the vertex in not in the shortest path tree
        for v in range(verts):
            if mat[u][v] > 0 and sptSet[v] == False and dist[v] > dist[u] + mat[u][v]:
                dist[v] = dist[u] + mat[u][v]
                parent[v] = u

    printSolution(dist,parent)

    return(dist,parent)

# find the vert with minimum distance value, from the set of vertices
# not yet included in shortest path tree
def minDistance(dist, sptSet, verts):
    # init minimum distance for next node
    min = math.inf

    # Search not nearest vertex not in the
    # shortest path tree
    for v in range(verts):
        if dist[v] < min and sptSet[v] == False:
            min = dist[v]
            min_index = v

    return min_index

# Function to print shortest path from source to j using parent array 
def printPath( parent, j):        
	#Base Case : If j is source 
	if parent[j] == -1 :  
		print(j)
		return
	printPath(parent , parent[j]) 
	print(j)

# A function to print the constructed distance array 
def printSolution(dist, parent): 
    src = 0
    print("Vertex \t\tDistance from Source\tPath") 
    for i in range(1, len(dist)): 
        print("\n%d --> %d \t\t%d \t\t\t\t\t" % (src, i, dist[i])), 
        printPath(parent,i) 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test

#connec = np.loadtxt("config_file.txt", dtype='i', delimiter=',')
#print(connec)
#print("Network Configuration")

#connec = [[0, 4, 0, 0, 0, 0, 0, 8, 0],
#           [4, 0, 8, 0, 0, 0, 0, 11, 0],
#           [0, 8, 0, 7, 0, 4, 0, 0, 2],
#           [0, 0, 7, 0, 9, 14, 0, 0, 0],
#           [0, 0, 0, 9, 0, 10, 0, 0, 0],
#           [0, 0, 4, 14, 10, 0, 2, 0, 0],
#           [0, 0, 0, 0, 0, 2, 0, 1, 6],
#           [8, 11, 0, 0, 0, 0, 1, 0, 7],
#           [0, 0, 2, 0, 0, 0, 6, 7, 0]
#          ];

#dijkstras(connec, 0)