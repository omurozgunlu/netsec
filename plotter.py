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
        print(lineCount)
    return csvArray
if __name__ == "__main__":
    result=readCSV()
    