# -*- coding: utf-8 -*-
"""
Created on Tue May 30 15:45:54 2023

@author: bzapardiel
"""

#QReengineerSDK: Imports
from QrEngineerSDK import QProviderFactory

def getTestCirqCircuit():
    import cirq
    circuitCirq = cirq.Circuit()
    qubits = cirq.LineQubit.range(4)
    circuitCirq.append(cirq.H(q) for q in cirq.LineQubit.range(4))
    circuitCirq.append(cirq.CCNOT(qubits[0],qubits[1],qubits[3]))
    circuitCirq.append(cirq.CNOT(qubits[0],qubits[1]))
    circuitCirq.append(cirq.CCNOT(qubits[1],qubits[2],qubits[3]))
    circuitCirq.append(cirq.CNOT(qubits[1],qubits[2]))
    circuitCirq.append(cirq.CNOT(qubits[0],qubits[1]))
    circuitCirq.append(cirq.measure(qubits[2],qubits[3]))
    return circuitCirq

def getTestQiskitCircuit():    
    from qiskit import QuantumCircuit
    circuitQiskit = QuantumCircuit(4, 2)
    circuitQiskit.h(0)
    circuitQiskit.h(1)
    circuitQiskit.h(2)
    circuitQiskit.h(3)
    circuitQiskit.ccx(0, 1, 3)
    circuitQiskit.cx(0, 1)
    circuitQiskit.ccx(1, 2, 3)
    circuitQiskit.cx(1, 2)
    circuitQiskit.cx(0, 1)
    circuitQiskit.measure(2, 0)
    circuitQiskit.measure(3, 0)
    return circuitQiskit

def getTestAmazonCircuit():
    from braket.circuits import Circuit
    circuitAmazon = Circuit()
    circuitAmazon.h([0,1,2,3])
    circuitAmazon.ccnot(0,1,3)
    circuitAmazon.cnot(0,1)
    circuitAmazon.ccnot(1,2,3)
    circuitAmazon.cnot(1,2)
    circuitAmazon.cnot(0,1)
    return circuitAmazon

# Define the mandatory parameters needed by the SDK

#QrEngineerSDK: QSOA Auth
qProvider = QProviderFactory(user = 'amartinez.aquantum.pro', password64='QXNkZjE5ODE=') #User enters his password encoded in Base64
#qProvider = QProviderFactory(user = 'bgarcia.AQLAB', passwordSHA256='') #User enters his password encoded in SHA256

qpathSolutionID = 10622 #TESTING_GATES
qpathDeviceID =  2 #QISKIT Local Simulator
qpathCircuitName = 'TestQiskit'
qpathNamespace = 'TEST'
qpathNumRepeats = 100

technologyToTest = 'Qiskit' #Cirq | Qiskit | Amazon | Dwave

sourceCircuit = ""
qpathCircuit = ""
if technologyToTest == 'Cirq':
    sourceCircuit = getTestCirqCircuit()
    qpathCircuit = qProvider.transpileCirqCircuit(sourceCircuit)

if technologyToTest == 'Qiskit':
    sourceCircuit = getTestQiskitCircuit()
    qpathCircuit = qProvider.transpileQiskitCircuit(sourceCircuit)

if technologyToTest == 'Amazon':
    sourceCircuit = getTestAmazonCircuit()
    qpathCircuit = qProvider.transpileAmazonCircuit(sourceCircuit)

result = qProvider.executeQPathCircuit(qpathSolutionID,qpathDeviceID,qpathCircuitName,qpathNamespace,qpathNumRepeats,qpathCircuit)
if result.success:
    print(result.histogram)    
else:
    print("Error executing the circuit" + result.error)


