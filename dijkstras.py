# Adjacency matrix based implementation of Dijkstra's algorithm
import math

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

    for node in range(verts):
        print ("Vertex Distance from Source")
        print (node, "\t", dist[node])

    return

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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test
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