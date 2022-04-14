import matplotlib.pyplot as plt
import numpy as np
import csv


def readCSV():
    csvArray=[]
    with open('./results/results.csv', newline='') as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
        lineCount=0
        for row in csvReader:
            if lineCount==0:
                print(f'row names are {", ".join(row)}')
                lineCount+=1
            elif len(row)!=0:
                csvArray.append({'nodeCount':row[0],'simCount':row[1],'compileTime':row[2],
                'keyGenerationTime':row[3],'encryptionTime':row[4],'executionTime':row[5],'decryptionTime':row[6],'referenceExecutionTime':row[7],'MSE':row[8]})
                lineCount+=1
            else:
                lineCount+=1
    return csvArray
def getAverageStatsPerNodeCount(array):
    countDict=getNodeCounts(array)
    statDict={}
    for value in array:
        nodeCount=float(value['nodeCount'])
        compileTime=float(value['compileTime'])
        keyGenerationTime=float(value['keyGenerationTime'])
        encryptionTime=float(value['encryptionTime'])
        executionTime=float(value['executionTime'])
        decryptionTime=float(value['decryptionTime'])
        referenceExecutionTime=float(value['referenceExecutionTime'])
        mse=float(value['MSE'])
        if nodeCount not in statDict:
            statDict[nodeCount]={'avgCompileTime':compileTime,'avgKeyGenerationTime':keyGenerationTime,'avgEncryptionTime':encryptionTime,'avgExecutionTime':executionTime,'avgdecryptionTime':decryptionTime,'avgReferenceExecutionTime':referenceExecutionTime,'avgMSE':mse}
        else:
            statDict[nodeCount]['avgCompileTime']+=compileTime
            statDict[nodeCount]['avgKeyGenerationTime']+=keyGenerationTime
            statDict[nodeCount]['avgEncryptionTime']+=encryptionTime
            statDict[nodeCount]['avgExecutionTime']+=executionTime
            statDict[nodeCount]['avgdecryptionTime']+=decryptionTime
            statDict[nodeCount]['avgReferenceExecutionTime']+=referenceExecutionTime
            statDict[nodeCount]['avgMSE']+=mse
    for key,value in statDict.items():
        value['avgCompileTime']=value['avgCompileTime']/int(countDict[str(int(key))])
        value['avgKeyGenerationTime']=value['avgKeyGenerationTime']/int(countDict[str(int(key))])
        value['avgEncryptionTime']=value['avgEncryptionTime']/int(countDict[str(int(key))])
        value['avgExecutionTime']=value['avgExecutionTime']/int(countDict[str(int(key))])
        value['avgdecryptionTime']=value['avgdecryptionTime']/int(countDict[str(int(key))])
        value['avgReferenceExecutionTime']=value['avgReferenceExecutionTime']/int(countDict[str(int(key))])
        value['avgMSE']=value['avgMSE']/int(countDict[str(int(key))])
    return statDict

def getNodeCounts(array):
    countDict={}
    for index,value in enumerate(array):
        if value['nodeCount'] in countDict:
            countDict[value['nodeCount']]+=1
        else:
            countDict[value['nodeCount']]=1
    return countDict
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha = 'center')

if __name__ == "__main__":
    result=readCSV()
    statDict=getAverageStatsPerNodeCount(result)
    nodeCounts=getNodeCounts(result)

    avgCompileTime = []
    avgKeyGenerationTime = []
    avgEncryptionTime = []
    avgExecutionTime = []
    avgdecryptionTime = []
    avgReferenceExecutionTime = []
    avgMSE = []
    for key,value in statDict.items():
        avgCompileTime.append(value['avgCompileTime']) 
        avgKeyGenerationTime.append(value['avgKeyGenerationTime'])   
        avgEncryptionTime.append(value['avgEncryptionTime'])    
        avgExecutionTime.append(value['avgExecutionTime'])     
        avgdecryptionTime.append(value['avgdecryptionTime'])     
        avgReferenceExecutionTime.append(value['avgReferenceExecutionTime'])     
        avgMSE.append(value['avgMSE'])     

    x = np.arange(len(nodeCounts))  # the label locations
    plt.ylabel('Average Compile Time')
    plt.xlabel('Node Count')
    plt.title('Average compile Time Per Node Count')
    plt.xticks(x,nodeCounts)
    plt.bar(nodeCounts.keys(), avgCompileTime)
    addlabels(nodeCounts.keys(), avgCompileTime)
    plt.tight_layout()
    plt.show()
        
    
    