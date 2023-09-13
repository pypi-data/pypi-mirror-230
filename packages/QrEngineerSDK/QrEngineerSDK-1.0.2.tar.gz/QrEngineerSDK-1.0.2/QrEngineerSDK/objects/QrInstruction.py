class QrInstruction:
    
    """
    Class representing a gate of a circuit.    
    
    Parameters
    ----------
    gate : str
        Literal tha represents the gate type.
    params: int[]
        Array with the gate parameters

    qubits: int[]
        Array with the indices of the qubits affected by the gate

    Attributes
    ----------
    gate : str
        Literal tha represents the gate type.
    params: int[]
        Array with the gate parameters
    qubits: int[]
        Array with the indices of the qubits affected by the gate
    """

    def __init__(self, gate, params, qubits):  
        self.gate = gate
        self.params = params
        self.qubits = qubits        
        