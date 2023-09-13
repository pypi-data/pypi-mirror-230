from ..objects.QrInstruction import QrInstruction
from ..objects.QrGates import *

# Qiskit Library
from qiskit import QuantumCircuit, Aer, transpile, assemble

class QrQiskitManager:
    
    """
    Class that allows to transpile gates circuits developed with the Amazon Braket SDK.
    """

    def getCircuitInstructions(self,circuit):
        """
        Decompose a Qiskit gates circuit and returns the list of gates, its parameters and qubits affected.

        Prerequisites
        ----------
        None.

        Parameters
        ----------
        circuit : qiskit.QuantumCircuit
            Circuit object created with the Qiskit SDK

        Output
        ----------
        Array of QrInstruction objects. 
        Each QrInstruction object contains a gate with its parameters and qubits to which it applies.
        """        
        instructions = []
        qasm_sim = Aer.get_backend('qasm_simulator')        
        circuit = circuit.decompose()    #ESTE MÉTODO DESHACE LOS ORÁCULOS 
        circuit = transpile(circuit, basis_gates = ['id', 'x','y','z','h','s','t','swap','measure','cx','ccx','rx','ry','rz'])                    
        circuit = assemble(circuit, qasm_sim).to_dict()               
        for instr in circuit["experiments"][0]["instructions"]: 
            gateVar = self.__getGateOperation(instr['name'])            
            paramVar = 0
            if 'params' in instr:
                paramVar = instr['params'][0]
            qbitVar = instr['qubits']
            instructions.append(QrInstruction(gateVar, paramVar, qbitVar))   
                              
        return instructions
    
    # We get the gate of the operation
    def __getGateOperation(self,gateName):        
        if (gateName=="x"):
            return GATE_X
        elif (gateName=="y"):
            return GATE_Y
        elif (gateName=="z"):
            return GATE_Z
        elif (gateName=="h"):
            return GATE_H
        elif (gateName=="s"):
            return GATE_S
        elif (gateName=="t"):
            return GATE_T
        elif (gateName=="swap"):
            return GATE_Swap
        elif (gateName=="rx"):
            return GATE_Rx
        elif (gateName=="ry"):
            return GATE_Ry
        elif (gateName=="rz"):
            return GATE_Rz
        elif (gateName=="cx"):
            return GATE_Cx
        elif (gateName=="ccx"):
            return GATE_Ccx
        elif (gateName=="measure"):
            return GATE_Measure
        else:
            return gateName
        
    
