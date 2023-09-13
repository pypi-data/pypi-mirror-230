import sys
import os
import ntpath
import pathlib
from dimod import utilities
from itertools import chain

class QrDwaveManager:

    """
    Class that allows to transpile the Binary Quadratic Model of an optimization problem, generated with the Dwave Ocean SDK.
    """
    
    def generateQPathCircuitFromBQM(self, bqm):        
        quboMatrix = [[0 for i in range(bqm.num_variables)] for j in range(bqm.num_variables)] 

        for i in range(bqm.num_variables):
            for j in range (i, bqm.num_variables):
                index_i = bqm.variables[i]
                index_j = bqm.variables[j]
                if i==j:
                    quboMatrix[i][j] = bqm.linear[index_i]
                else:
                    if (index_j, index_i) in bqm.quadratic:                        
                        quboMatrix[i][j] = bqm.quadratic[(index_j, index_i)]   
        
        circuitIL = "PARAM(NVars|@NVars@);PARAM(Offset|@Offset@);AUXDATA(C|\"@C@\");CLASS(ClassX|NVars|\"\");VARIABLE(X|{ClassX}|\"\");RULE(Rule1|\"\"|\"1\"|	{ SUMMATORY(from 1 to NVars iterate i| { SUMMATORY(from i+1 to NVars iterate j|	{ QUADRATIC(X[i]|X[j]|\"C[i,j]\")	})}),SUMMATORY(from 1 to NVars iterate i|{ LINEAR(X[i]| \"C[i,i]\")}),OFFSET(\"Offset\")});"        
        circuitIL = circuitIL.replace("@NVars@",str(bqm.num_variables))
        circuitIL = circuitIL.replace("@Offset@",str(bqm.offset))
        circuitIL = circuitIL.replace("@C@",str(quboMatrix))        
        return circuitIL    

    def generateQPathCircuitFromQubo(self, qubo, offset=0):  
        bqm = BinaryQuadraticModel.from_qubo(Q=qubo, offset=offset)
        return self.generateQPathCircuitFromBQM(bqm)

    def generateQPathCircuitFromIsing(self, h, J, offset=0):  
        bqm = BinaryQuadraticModel.from_ising(h=h, J=J, offset=offset)
        return self.generateQPathCircuitFromBQM(bqm) 
    
            
    