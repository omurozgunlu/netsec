from eva import EvaProgram, Input, Output, evaluate
from eva.ckks import CKKSCompiler
from eva.seal import generate_keys
from eva.metric import valuation_mse
import timeit
import networkx as nx
from random import random
def longestPaths(neighbors):
    longestPathsDict = {}
    for node in neighbors:
        longestPathsDict[node]=[]
        visited = [False for x in range(len(neighbors.keys()))]
        DFS(neighbors,node,visited,longestPathsDict)
    return longestPathsDict
        

def DFS(neighbors,src,visited,longestPathsDict):
    visited[src]= True
    for key in neighbors[src]:
        tempArray=[]
        if (not visited[key]):
            tempArray.append(neighbors[src][key])
            # tempArray.append(neighbors[src][key])
            innerDFS(neighbors,key,visited,tempArray)
            longestPathsDict[src].append(tempArray)
        print(tempArray)
            
def innerDFS(neighbors,src,visited,tempArray):
    visited[src]= True
    allVisited = True
    reset = False
    for key in neighbors[src]:
        if reset:
            del tempArray[-1]
        if (not visited[key]):
            tempArray.append(neighbors[src][key])
            # print(tempArray)
            allVisited = False
            reset = innerDFS(neighbors,key,visited,tempArray)           
    return allVisited

# Using networkx, generate a random graph
# You can change the way you generate the graph
def generateGraph(n, k, p):
    #ws = nx.cycle_graph(n)
    ws = nx.watts_strogatz_graph(n,k,p)
    return ws

# If there is an edge between two vertices its weight is 1 otherwise it is zero
# You can change the weight assignment as required
# Two dimensional adjacency matrix is represented as a vector
# Assume there are n vertices
# (i,j)th element of the adjacency matrix corresponds to (i*n + j)th element in the vector representations
def serializeGraphZeroOne(GG,vec_size):
    n = GG.size()
    graphdict = {}
    g = []
    for row in range(n):
        for column in range(n):
            if GG.has_edge(row, column): # I assumed the vertices are connected to themselves
                weight = 1
            else:
                weight = 0 
            g.append(weight)
            if weight>0:
                if row in graphdict:
                    graphdict[row][column] = weight  # EVA requires str:listoffloat
                else:
                    graphdict[row] = {}
                    graphdict[row][column] = weight 
    # EVA vector size has to be large, if the vector representation of the graph is smaller, fill the eva vector with zeros
    return g, graphdict

# To display the generated graph
def printGraph(graph,n):
    for row in range(n):
        for column in range(n):
            print("{:.5f}".format(graph[row*n+column]), end = '\t')
        print() 

# Eva requires special input, this function prepares the eva input
# Eva will then encrypt them
def prepareInput(n, m):
    input = {}
    GG = generateGraph(n,3,0.5)
    graph, graphdict = serializeGraphZeroOne(GG,m)
    paths = longestPaths(graphdict)
    # input['Graph'] = graph
    # return input
    return paths

# This is the dummy analytic service
# You will implement this service based on your selected algorithm
# you can other parameters using global variables !!! do not change the signature of this function 


def graphanalticprogram(graph,n):
    temp = graph
    for i in range(n-1):
        graph = graph<<1
        temp = graph + temp
    return temp
    
# Do not change this 
# the parameter n can be passed in the call from simulate function
class EvaProgramDriver(EvaProgram):
    def __init__(self, name, vec_size=4096, n=4):
        self.n = n
        super().__init__(name, vec_size)

    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

# Repeat the experiments and show averages with confidence intervals
# You can modify the input parameters
# n is the number of nodes in your graph
# If you require additional parameters, add them
def simulate(path,m,arrLength):
    #print("Will start simulation for ", n)
    config = {}
    config['warn_vec_size'] = 'false'
    config['lazy_relinearize'] = 'true'
    config['rescaler'] = 'always'
    config['balance_reductions'] = 'true'
    inputs = {}
    inputs['Graph']=path
    graphanaltic = EvaProgramDriver("graphanaltic", vec_size=m,n=arrLength)
    with graphanaltic:
        graph = Input('Graph')
        reval = graphanalticprogram(graph,arrLength)
        Output('ReturnedValue', reval)
    
    prog = graphanaltic
    prog.set_output_ranges(30)
    prog.set_input_scales(30)

    start = timeit.default_timer()
    compiler = CKKSCompiler(config=config)
    compiled_multfunc, params, signature = compiler.compile(prog)
    compiletime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    public_ctx, secret_ctx = generate_keys(params)
    keygenerationtime = (timeit.default_timer() - start) * 1000.0 #ms
    
    start = timeit.default_timer()
    encInputs = public_ctx.encrypt(inputs, signature)
    encryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    encOutputs = public_ctx.execute(compiled_multfunc, encInputs)
    executiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    outputs = secret_ctx.decrypt(encOutputs, signature)
    decryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    reference = evaluate(compiled_multfunc, inputs)
    referenceexecutiontime = (timeit.default_timer() - start) * 1000.0 #ms
    
    # Change this if you want to output something or comment out the two lines below
    # for key in outputs:
    #     print(key, float(outputs[key][0]), float(reference[key][0]))

    mse = valuation_mse(outputs, reference) # since CKKS does approximate computations, this is an important measure that depicts the amount of error

    return compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse, outputs

def fillWithZeros(arr,m):
    for i in range(m - len(arr)): 
        arr.append(0.0)

if __name__ == "__main__":
    simcnt = 1 #The number of simulation runs, set it to 3 during development otherwise you will wait for a long time
    # For benchmarking you must set it to a large number, e.g., 100
    #Note that file is opened in append mode, previous results will be kept in the file
    resultfile = open("results.csv", "a")  # Measurement results are collated in this file for you to plot later on
    resultfile.write("NodeCount,SimCnt,CompileTime,KeyGenerationTime,EncryptionTime,ExecutionTime,DecryptionTime,ReferenceExecutionTime,Mse\n")
    resultfile.close()
    
    print("Simulation campaing started:")
    for nc in range(36,64,4): # Node counts for experimenting various graph sizes
        n = nc
        resultfile = open("results.csv", "a")
        maxPathLength= 0
        maxLength=0
        for i in range(simcnt):
            #Call the simulator
            m = 4096*4
            paths = prepareInput(n, m)
            tempPaths= paths
            start = timeit.default_timer()
            for key in paths:
                for path in paths[key]:
                    arrLength = len(path)
                    fillWithZeros(path,m)
                    compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse,outputs = simulate(path,m,arrLength)
                    if (outputs['ReturnedValue'][0]>maxPathLength):
                        maxPathLength = outputs['ReturnedValue'][0]
            totalExecutionTime = (timeit.default_timer() - start) * 1000.0 #ms
            print(totalExecutionTime)
            for key in tempPaths:
                for arr in tempPaths[key]:
                    tempVal=0
                    for element in arr:
                        tempVal = tempVal + element
                    if tempVal > maxLength:
                        maxLength = tempVal
            mse = pow((maxPathLength - maxLength),2)
            print('node count ',nc)
            print(maxPathLength)
            print(maxLength)
            print(mse)
        resultfile.close()