from ..objects.QrInstruction import QrInstruction
from ..objects.QrGates import *
# Cirq Google Library
import cirq
import json

class QrCirqManager:

    """
    Class that allows to transpile gates circuits developed with the Cirq SDK.
    """
        
    def getCircuitInstructions(self,circuit):   
        """
        Decompose a Cirq gates circuit and returns the list of gates, its parameters and qubits affected.

        Prerequisites
        ----------
        None.

        Parameters
        ----------
        circuit : cirq.Circuit
            Circuit object created with the Cirq SDK

        Output
        ----------
        Array of QrInstruction objects. 
        Each Qrinstruction objetc contains a gate with its parameters and qubits where applied.
        """
        circuitJson = cirq.to_json(circuit) 
        circuitDict = json.loads(circuitJson)
        instructions = []
        for moments in circuitDict["moments"]:
            for operations in moments["operations"]:
                gateVar = self.__getGateOperation(list(operations.values())[1])
                paramVar = self.__getParamOperation(list(operations.values())[1])
                qbitVar = self.__getNQubitsOperation(list(operations.values())[2])
                if((gateVar is not None) and (paramVar is not None) and (qbitVar is not None)):
                    instructions.append(QrInstruction(gateVar, paramVar, qbitVar))  
        return instructions
    
    # We get the gate of the operation
    def __getGateOperation(self,operation):
        gateTmp = list(operation.values())[0]
        if (gateTmp=="_PauliX"):
            return GATE_X
        elif (gateTmp=="_PauliY"):
            return GATE_Y
        elif (gateTmp=="_PauliZ"):
            return GATE_Z
        elif (gateTmp=="HPowGate"):
            return GATE_H
        elif (gateTmp=="ZPowGate"):
            return GATE_Zpower
        elif (gateTmp=="SwapPowGate"):
            return GATE_Swap
        elif (gateTmp=="Rx"):
            return GATE_Rx
        elif (gateTmp=="Ry"):
            return GATE_Ry
        elif (gateTmp=="Rz"):
            return GATE_Rz
        elif (gateTmp=="CXPowGate"):
            return GATE_Cx
        elif (gateTmp=="CCXPowGate"):
            return GATE_Ccx
        elif (gateTmp=="MeasurementGate"):
            return GATE_Measure
        else:
            return gateTmp

    # We get the params of the operation
    def __getParamOperation(self,operation):
        return list(operation.values())[1]

    # We obtain the qubit/s of the operation
    def __getNQubitsOperation(self,operation):
        if isinstance(operation, dict):
            return list(operation.values())[1]
        else:
            return [x.get('x') for x in operation]