from ..objects.QrInstruction import QrInstruction
from ..objects.QrGates import *
# AWS imports: Import Braket SDK modules
from braket.circuits import Circuit

class QrAmazonBraketManager:
    
    """
    Class that allows to transpile gates circuits developed with the Amazon Braket SDK.
    """
    
    def getCircuitInstructions(self, circuit):
        """
        Decompose a Amazon Braket gates circuit and returns the list of gates, its parameters and qubits affected.

        Prerequisites
        ----------
        None.

        Parameters
        ----------
        circuit : braket.circuits.Circuit
            Circuit object created with the Amazon Braket SDK

        Output
        ----------
        Array of QrInstruction objects. 
        Each Qrinstruction objetc contains a gate with its parameters and qubits where applied.
        """       
        instructions = []
        for instr in circuit.instructions:
            gateVar = self.__getGateOperation(instr.operator.name)            
            paramVar = self.__getParamOperation(instr.operator)            
            qbitsVar = self.__getNQubitsOperation(instr.target) 
            if((gateVar is not None) and (paramVar is not None) and (qbitsVar is not None)):
                instructions.append(QrInstruction(gateVar, paramVar, qbitsVar))

        return instructions
    
    # We get the gate of the operation
    def __getGateOperation(self,gateName):        
        if (gateName=="X"):
            return GATE_X
        elif (gateName=="Y"):
            return GATE_Y
        elif (gateName=="Z"):
            return GATE_Z
        elif (gateName=="H"):
            return GATE_H
        elif (gateName=="S"):
            return GATE_S
        elif (gateName=="T"):
            return GATE_T
        elif (gateName=="Swap"):
            return GATE_Swap
        elif (gateName=="Rx"):
            return GATE_Rx
        elif (gateName=="Ry"):
            return GATE_Ry
        elif (gateName=="Rz"):
            return GATE_Rz
        elif (gateName=="CCNot"):
            return GATE_Ccx
        elif (gateName=="CNot"):
            return GATE_Cx
        else:
            return gateName
                      
    def __getParamOperation(self,operator):
        listGatesWithParams = ['Rx','Ry','Rz']
        if operator.name in listGatesWithParams:
            return operator.angle
        else:
            return 0
    
    # We obtain the qubit/s of the operation        
    def __getNQubitsOperation(self,target):
        qubits = []
        for qbit in target:
            qubits.append(int(qbit))
        return qubits