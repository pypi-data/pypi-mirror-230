import json
import hashlib

from QuantumPathQSOAPySDK import QSOAPlatform
from .objects import QrCircuitExecutionResult, QrInstruction
from .objects.QrGates import *


class QProviderFactory:     

    """
    QrEngineerSDK main class that provides access to transpilation and circuit execution functionality.
    """

    # CONSTRUCTOR
    def __init__(self, user: str = None, password64: str = None, passwordSHA256: str = None):
        """        
        Prerequisites
        ----------
        - User created in Quantum Path.
        
        Parameters
        ----------
        user : str
            Quantum Path user name.

        password64 : str
            Base64 encoding of the user's password.

        passwordSHA256 : str
            SHA256 encoding of the user's password. 
        """       
        qsoa = QSOAPlatform()

        if user:
            self.user = user
        if password64:
            self.password64 = password64
            qsoa.authenticate(self.user, self.password64)
        elif passwordSHA256:
            self.passwordSHA256 = passwordSHA256
            qsoa.authenticateEx(self.user, self.passwordSHA256)

        if qsoa.echostatus():
            self.qsoa = qsoa
        else:
            raise Exception('User not authenticated')


    # PUBLIC METHODS
    def transpileCirqCircuit(self, sourceCircuit):     
        """
        Transpile a Cirq circuit to a QPath gates circuit.

        Prerequisites
        ----------
        - User already authenticated

        Parameters
        ----------
        sourceCircuit : cirq.Circuit
            Circuit object created with the Cirq SDK

        Output
        ----------
        QuantumPathQSOAPySDK.circuit.gates.CircuitGates object
        """
        from .providers.QrCirqManager import QrCirqManager
        print("Transpiling Cirq circuit to Quantum Path especification...")
        objQrCirqManager = QrCirqManager()
        circuitInstructions = objQrCirqManager.getCircuitInstructions(sourceCircuit)
        qpathCircuit = self.__getQPathCircuitGates(circuitInstructions)
        print("Circuit transpiled")
        return qpathCircuit

    def transpileQiskitCircuit(self, sourceCircuit):  
        """
        Transpile a Qiskit circuit to a QPath gates circuit.

        Prerequisites
        ----------
        - User already authenticated

        Parameters
        ----------
        sourceCircuit : qiskit.QuantumCircuit
            Circuit object created with the Qiskit SDK

        Output
        ----------
        QuantumPathQSOAPySDK.circuit.gates.CircuitGates object
        """
        from .providers.QrQiskitManager import QrQiskitManager   
        print("Transpiling Qiskit circuit to QPath especification...")
        objQrQiskitManager = QrQiskitManager()
        circuitInstructions = objQrQiskitManager.getCircuitInstructions(sourceCircuit)
        qpathCircuit = self.__getQPathCircuitGates(circuitInstructions)
        print("Circuit transpiled")
        return qpathCircuit
    
    def transpileAmazonCircuit(self, sourceCircuit):
        """
        Transpile an Amazon Braket circuit to a QPath gates circuit.

        Prerequisites
        ----------
        - User already authenticated

        Parameters
        ----------
        sourceCircuit : braket.circuits.Circuit
            Circuit object created with the Amazon Braket SDK

        Output
        ----------
        QuantumPathQSOAPySDK.circuit.gates.CircuitGates object
        """
        from .providers.QrAmazonBraketManager import QrAmazonBraketManager
        print("Transpiling Amazon circuit to QPath especification...")
        objQrAmazonBraketManager = QrAmazonBraketManager()
        circuitInstructions =  objQrAmazonBraketManager.getCircuitInstructions(sourceCircuit)
        qpathCircuit = self.__getQPathCircuitGates(circuitInstructions)
        # Amazon doesn't allow you to measure a specific qubit. When we finish building the circuit, we make a measurement of all the qubits. 
        qpathCircuit.measure()
        print("Circuit transpiled")
        return qpathCircuit

    def transpileDwaveBQM(self, sourceBQM):
        """
        Transpile a Dwave Binary Quadratic Model to a QPath annealing circuit.

        Prerequisites
        ----------
        - User already authenticated

        Parameters
        ----------
        sourceBQM : dimod.BinaryQuadraticModel
            BinaryQuadraticModel object created with the Dwave Ocean SDK

        Output
        ----------
        QuantumPathQSOAPySDK.circuit.annealing.CircuitAnnealing object
        """ 
        from .providers.QrDwaveManager import QrDwaveManager
        print("Transpiling Dwave annealing circuit to QPath especification...")
        objDewaveManager = QrDwaveManager()
        qpathCircuit = objDewaveManager.generateQPathCircuitFromBQM(sourceBQM)
        print("Circuit transpiled")
        return qpathCircuit           
    
    def transpileDwaveQubo(self, qubo, offset=0):
        """
        Transpile a Quadratic unconstrained binary optimization problem to a QPath annealing circuit.

        Prerequisites
        ----------
        - User already authenticated

        Parameters
        ----------
        Q : dict(float)
            Dictionary with the coefficients of the QUBO problem

        offset : Constant term of the QUBO problem 
        
        Output
        ----------
        QuantumPathQSOAPySDK.circuit.annealing.CircuitAnnealing object
        """ 
        from .providers.QrDwaveManager import QrDwaveManager
        print("Transpiling Dwave annealing circuit to QPath especification...")
        objDewaveManager = QrDwaveManager()
        qpathCircuit = objDewaveManager.generateQPathCircuitFromBQM(qubo, offset)
        print("Circuit transpiled")
        return qpathCircuit     

    def transpileDwaveIsing(self, h, J, offset=0):
        """
        Transpile the Ising model of a optimization problem to a QPath annealing circuit.

        Prerequisites
        ----------
        - User already authenticated

        Parameters
        ----------
        h : Union[Mapping, Sequence]
            Linear biases of the Ising problem.

        J : Union[Mapping, Sequence]
            Quadratic biases of the Ising problem

        offset : Constant term of the QUBO problem 
        
        Output
        ----------
        QuantumPathQSOAPySDK.circuit.annealing.CircuitAnnealing object
        """ 
        from .providers.QrDwaveManager import QrDwaveManager
        print("Transpiling Dwave annealing circuit to QPath especification...")
        objDewaveManager = QrDwaveManager()
        qpathCircuit = objDewaveManager.generateQPathCircuitFromIsing(h, J, offset)
        print("Circuit transpiled")
        return qpathCircuit 

    def executeQPathCircuit(self, solutionId, deviceId, circuitName, circuitNamespace, numRepeats, circuit):     

        """
        Run a QPath gates/annealing circuit on a quantum device via Quantum Path.

        Prerequisites
        ----------
        - User already authenticated
        - Existing QPath solution.

        Parameters
        ----------
        solutionId : int
            QPath Solution ID to create the circuit and the flow needed to the execution.

        deviceId : int
            Specific Device ID to run the circuit.    

        circuitName : str
            Circuit name.    

        circuitNamespace : str
            Circuit namespace. 

        numRepeats : int
            Number of repetitions of each circuit, for sampling. 

        circuit : CircuitAnnealing | CircuitGates
            CircuitAnnealing or CircuitGates to be executed. 

        Output
        ----------
        QuantumPathQSOAPySDK.circuit.annealing.CircuitAnnealing object
        """ 

        print("Executing circuit through QuantumPath...")        
        objResult = QrCircuitExecutionResult() 
        
        # Create Circuit in QPath
        circuitManagementResult = self.__createCircuitInQuantumPath(solutionId, circuitName, circuitNamespace, circuit)            
        
        if (circuitManagementResult.getExitCode()=="KO"):
            objResult.success = False
            objResult.error = circuitManagementResult.getExitMessage()                
        else:                            
            objResult.circuitId = circuitManagementResult.getIdAsset()
            # Create Flow in QPath
            flowManagementResult = self.__createFlowInQuantumPath(solutionId, circuitName, circuitNamespace, numRepeats)
            
            if (flowManagementResult.getExitCode()=="KO"):
                objResult.success = False
                objResult.error = flowManagementResult.getExitMessage()                    
            else:
                print("     Executing QPath flow...")
                
                # Running Circuit in QPath
                flowId = flowManagementResult.getIdAsset()
                exe_application = self.qsoa.runQuantumApplicationSync('TASK_EXECUTION_' + circuitName, solutionId, flowId, deviceId)
                exe_response = self.qsoa.getQuantumExecutionResponse(exe_application.getExecutionToken(), solutionId, flowId)
                
                if (exe_response.getExitCode() == "ERR"):
                    objResult.success = False
                    objResult.error = exe_response.getExitMessage()
                    print("Execution finished with error")              
                else:
                    objResult.success = True
                    objResult.flowId = flowId
                    objResult.histogram = exe_response.getHistogram() 
                    print("Execution finished")

        return objResult    

    # PRIVATE METHODS
    def __getQPathCircuitGates(self, circuitInstructions):                
        qpathCircuit = self.qsoa.CircuitGates()        
        for i in circuitInstructions:            
            if(i.gate== GATE_X): 
                qpathCircuit.x(i.qubits)
            elif(i.gate== GATE_Y): 
                qpathCircuit.y(i.qubits)
            elif(i.gate== GATE_Z): 
                qpathCircuit.z(i.qubits)
            elif(i.gate== GATE_H):
                qpathCircuit.h(i.qubits)
            elif(i.gate== GATE_Zpower): 
                if(i.params==0.5):
                    qpathCircuit.s(i.qubits)
                elif(i.params==0.25):
                    qpathCircuit.t(i.qubits)
            elif(i.gate==GATE_S):
                qpathCircuit.s(i.qubits)
            elif(i.gate==GATE_T):
                qpathCircuit.t(i.qubits)
            elif(i.gate==GATE_SwapPow or i.gate==GATE_Swap): 
                qpathCircuit.swap(i.qubits[0],i.qubits[1])
            elif(i.gate==GATE_Cx): 
                qpathCircuit.cx(i.qubits[0],i.qubits[1])
            elif(i.gate==GATE_Ccx): 
                qpathCircuit.ccx(i.qubits[0],i.qubits[1],i.qubits[2])
            elif(i.gate==GATE_CXPow): 
                qpathCircuit.cx(i.qubits[0],i.qubits[1])
            elif(i.gate==GATE_CCXPow): 
                qpathCircuit.ccx(i.qubits[0],i.qubits[1],i.qubits[2])
            elif(i.gate==GATE_Rx): 
                qpathCircuit.rx(i.qubits,str(i.params))
            elif(i.gate==GATE_Ry): 
                qpathCircuit.ry(i.qubits,str(i.params))
            elif(i.gate==GATE_Rz): 
                qpathCircuit.rz(i.qubits,str(i.params))
            elif(i.gate==GATE_Measure):
                listPosMeasure = []
                if (isinstance(i.qubits, int)):
                    listPosMeasure.append(i.qubits)
                else:
                    for j in i.qubits:
                        listPosMeasure.append(j)
                qpathCircuit.measure(listPosMeasure)
            else:
                print("WARNING: Gate not supported in QuantumPath: " + i.gate)       
                  
        return qpathCircuit
        
        
    def __createCircuitInQuantumPath(self, solutionId, circuitName, circuitNamespace, circuit):
        assetDescription = 'Circuit generated from QAPPS QrEngineer'
        assetBody = circuit
        assetType = ''
        assetLevel = ''

        if (circuit.__class__.__name__ == 'CircuitGates'):
            assetType = 'GATES' 
            assetLevel = 'VL'  
        else:
            assetType = 'ANNEAL' 
            assetLevel = 'IL'
        
        # Check if the circuit exists
        listAssets = self.qsoa.getAssetCatalog(solutionId, 'CIRCUIT', assetLevel)
        # There is already a circuit with that name: Update, else Create
        if(len(([x for x in listAssets if x.getName() == circuitName]))>0):
            print("     Updating QPath circuit...")
            asset = [x for x in listAssets if x.getName() == circuitName][0]
            circuitManagementResult = self.qsoa.updateAssetSync(asset, circuitName, circuitNamespace, assetDescription, assetBody, assetType, assetLevel)
            return circuitManagementResult
        else:
            print("     Creating QPath circuit...")
            circuitManagementResult = self.qsoa.createAssetSync(solutionId, circuitName, circuitNamespace, assetDescription, assetBody, assetType, assetLevel)
            return circuitManagementResult
        
    
    def __createFlowInQuantumPath(self, solutionId, circuitName, circuitNamespace, numRepeats):
        # Defining flow
        flow = self.qsoa.CircuitFlow()
        startNode = flow.startNode()
        initNode = flow.initNode(0)
        nameCircuitNode = circuitNamespace + '.' + circuitName
        circuit = flow.circuitNode(nameCircuitNode)
        repeatNode = flow.repeatNode(numRepeats)
        endNode = flow.endNode()
        flow.linkNodes(startNode, initNode)
        flow.linkNodes(initNode, circuit)
        flow.linkNodes(circuit, repeatNode)
        flow.linkNodes(repeatNode, endNode)
                
        # Creating flow
        flowName = circuitName + '_QR_FLOW'
        flowDescription = "Flow generated from QApps QrEngineer"

        assetPublication = True
        assetBody = flow
        assetLevel = 'VL'
        assetType = 'FLOW'
        listFlows = self.qsoa.getQuantumFlows(solutionId)

        # There is already a flow with that name of circuit: Update, else Create
        if(len(([x for x in listFlows if x.getName() == flowName]))>0):
            print("     Updating QPath flow...")
            idUpdatedFlow = [x for x in listFlows if x.getName() == flowName][0].getId()
            asset = self.qsoa.getAsset(idUpdatedFlow, 'FLOW', assetLevel)
            flowManagementResult = self.qsoa.updateAssetSync(asset, flowName, circuitNamespace, flowDescription, assetBody, assetType, assetLevel)
            return flowManagementResult
        else:
            print("     Creating QPath flow...")
            flowManagementResult = self.qsoa.createAssetFlowSync(solutionId, flowName,circuitNamespace, flowDescription, assetBody, assetLevel, assetPublication)
            return flowManagementResult

    
    
