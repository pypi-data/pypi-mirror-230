# -*- coding: utf-8 -*-
"""
Created on Tue May 30 15:45:54 2023

@author: bzapardiel
"""

# Import our class from SDK
from QrEngineerSDK import QProviderFactory
from dwave.system import EmbeddingComposite, DWaveSampler
from dwave.system import LeapHybridSampler
from dimod.reference.samplers import ExactSolver
from dimod import BinaryQuadraticModel
from dwave.cloud import Client
from collections import defaultdict
from collections import namedtuple
import json
import numpy as np
from math import *

def customJsonDecoder(inputDict):
    newObj = namedtuple('AUXDATA', inputDict.keys())
    for key in inputDict:        
        setattr(newObj, key, np.array(inputDict[key]))    
    return newObj

def parseJSONAuxdata(inputJSON):
    return json.loads(inputJSON, object_hook=customJsonDecoder)

def SquareQUBO(VARIABLES, Q,offset):
    
    varmax=len(VARIABLES) #añadimos un nuevo termino a la matriz qubo con nuestro termino de offset. Trataremos el offset como una variable
    Q[(varmax,varmax)]=offset
    Q1=defaultdict(float) #Creamos nuestro diccionario de salida. 
    
    n2=len(VARIABLES)+1
    for i in range (n2): #Iteramos sobre los elementos de la qubo.
        for j in range(n2): 
            #Cuando i o j representan el término de offset, al no ser éste una variable, el valor de la multiplicación obtenido se añade a la verdadera variable que multiplica.
            if (i==varmax and j!=varmax):
                Q1[(j,j)]+=Q[(i,i)]*Q[(j,j)]
            if (j==varmax and i!=varmax):
                Q1[(i,i)]+=Q[(i,i)]*Q[(j,j)]
            if (i==varmax and j==varmax):
                Q1[(i,i)]+=Q[(i,i)]*Q[(j,j)]
            else:
                Q1[(i,j)]+=Q[(i,i)]*Q[(j,j)]
                    
    # Nos quedamos solo con los elementos de la diagonal superior. 
    for i in range(n2):
        for j in range(n2):
            if (i>j):
                Q1[(j,i)]+=Q1[(i,j)]
                Q1[(i,j)]=0
                
    #guardamos el termino de offset
    offset=Q1[(varmax,varmax)]
    
    #Eliminamos la ultima fila de la matriz Q, con el termino de offset 
    for i in range(n2):
        Q1.pop((varmax,i))
    for i in range(n2-1):
         Q1.pop((i,varmax))

    
    output=[Q1,offset]
    return output


def SumQUBO(VARIABLES, Q1, Q2):           
    n=len(VARIABLES)
    for i in range (n): 
        for j in range(n): 
            if i <= j:
                Q1[(i,j)]+=Q2[(i,j)]
            else:
                Q1[(j,i)]+=Q2[(i,j)]
                Q1[(i,j)]=0

                
def MultiplyQUBO(VARIABLES, Q,value):
    n=len(VARIABLES)
    for i in range (n): 
        for j in range(n): 
            Q[(i,j)]=Q[(i,j)]*value


def FormatResult(solution, variables):
            
    record = solution.record
    firstResult = solution.first
        
    fullsample = {}
    for index in range(len(firstResult.sample)):
        varName = variables[index][0] + "[" + ','.join(str(x) for x in variables[index][1:]) + "]"
        fullsample[varName] = str(firstResult.sample[index])

    s_solution = { "number_of_samples": str(len(record)), "number_of_variables": str(len(record[0][0])),"sample_energy": str(firstResult.energy),"sample_occurence": str(firstResult.num_occurrences),"fullsample": fullsample}

    return s_solution

def getDwaveBQM():
    
    from collections import defaultdict

    ###--INITIALIZATION--###
    offset = 0
    Q = defaultdict(float)

    ###--AUXDATA--###
    Prices = parseJSONAuxdata('[4,1,3]')
    Weights = parseJSONAuxdata('[1,2,3]')

    ###--VARIABLES--###
    VARIABLES = []
    for i0 in range(1, int(3 + 1)):
        VARIABLES.append(('Boxes', i0))

    VARIABLES = dict(zip(VARIABLES,[i for i in range(len(VARIABLES))])) 
    VARIABLES_INV = {v: k for k, v in VARIABLES.items()}

    ###--RULES--###

    ##Rule1: Maximize the package price
    Q_Rule1 = defaultdict(float)

    lambda_Rule1 = 1
    offset_Rule1 = 0

    for i in range(int(1), int(3+1)):
        var = VARIABLES[('Boxes', i)]
        coefficient = -Prices[i-1]
        Q_Rule1[(var, var)] += coefficient

    MultiplyQUBO(VARIABLES, Q_Rule1, lambda_Rule1)
    SumQUBO(VARIABLES, Q, Q_Rule1)
    offset += offset_Rule1 * lambda_Rule1

    ## END RULE ##

    ##Rule2: Total weight must be 6kg
    Q_Rule2 = defaultdict(float)

    lambda_Rule2 = 10
    offset_Rule2 = 0

    offset_1780558693 = 0
    Q_1780558693 = defaultdict(float)

    for i in range(int(1), int(3+1)):
        var = VARIABLES[('Boxes', i)]
        coefficient = Weights[i-1]
        Q_1780558693[(var, var)] += coefficient
    offset_1780558693 += -3

    resultSquareQUBO = SquareQUBO(VARIABLES, Q_1780558693, offset_1780558693)
    Q_1780558693 = resultSquareQUBO[0]
    offset_1780558693 = resultSquareQUBO[1]

    SumQUBO(VARIABLES, Q_Rule2, Q_1780558693)
    offset_Rule2 += offset_1780558693

    MultiplyQUBO(VARIABLES, Q_Rule2, lambda_Rule2)
    SumQUBO(VARIABLES, Q, Q_Rule2)
    offset += offset_Rule2 * lambda_Rule2

    ## END RULE ##

    ###--DWAVE MANAGED EXECUTION--###    
    bqm = BinaryQuadraticModel.from_qubo(Q, offset)
    
    return bqm
    
#QrEngineerSDK: QSOA Auth
qProvider = QProviderFactory(user = 'bgarcia.AQLAB', password64='') #User enters his password encoded in Base64
qProvider = QProviderFactory(user = 'bgarcia.AQLAB', passwordSHA256='') #User enters his password encoded in SHA256

idSolution = 10617
idDevice = 18
nameCircuit = 'TestDwave'
nameSpace = 'TEST'
numRepeats = 100

bqm = getDwaveBQM()
qpathCircuit = qProvider.transpileDwaveBQM(bqm)

result = qProvider.executeQPathCircuit(idSolution,idDevice,nameCircuit,nameSpace,numRepeats,qpathCircuit)

if result.success:
    print(result.histogram)    
else:
    print("Error executing the circuit" + result.error)


