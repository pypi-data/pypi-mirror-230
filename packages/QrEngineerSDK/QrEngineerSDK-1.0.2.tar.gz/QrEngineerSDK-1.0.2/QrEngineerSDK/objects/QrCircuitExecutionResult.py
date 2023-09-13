class QrCircuitExecutionResult:
    
    """
    Class that represents the result of the execution of a circuit in Quantum Path.

    Attributes
    ----------
    success : bool
        Represents whether the execution has completed successfully
    error: str
        Error Description            
    histogram: dict
        Dictionary with the result of the execution of the circuit
    circuitId: int
        ID of the circuit created in Quantum Path
    flowId: int
        ID of the flow created in Quantum Path
    """

    def __init__(self):
        self.success = True
        self.error = ''
        self.histogram = ''
        self.circuitId = -1
        self.flowId = -1        
        