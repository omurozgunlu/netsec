#depth first search
def DFS(graph, src, prev_len,
        max_len, visited):
     
    # Mark the src node visited
    visited[src] = 1
 
    curr_len = 0
 
    adjacent = None
 
    # Traverse all adjacent
    for i in range(len(graph[src])):
         
        # Adjacent element
        adjacent = graph[src][i]
 
        if (not visited[adjacent[0]]):
             
            curr_len = prev_len + adjacent[1]
 
            DFS(graph, adjacent[0], curr_len,
                            max_len, visited)
 
        if (max_len < curr_len):
            max_len = curr_len
 
        # make curr_len = 0 for next adjacent
        curr_len = 0
 
# returns longest path in graph
def longestPath(graph, n):
     
    max_len = -1
 
    for i in range(0, n):
         
        # initialize visited array with 0
        visited = [False] * (n)
 
        # Call DFS for src vertex i
        DFS(graph, i, 0, max_len, visited)
 
    return max_len
 