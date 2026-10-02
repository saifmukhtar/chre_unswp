import sys
sys.path.insert(0, "/home/saif/chre")
sys.path.insert(0, "/home/saif/chre_unswp")
from chre_api import Rule
from models.schema import NodeType, StateToken

def get_exttload_rules():
    """
    Returns the strict mathematical rules for Exttload.sol
    This models EIP-1153 Transient Storage reads by external contracts.
    """
    rules = []

    # =========================================================================
    # FUNCTION: exttload (Lines 10-15)
    # =========================================================================
    # The External Contract executes a read. 
    # To prevent EVM infinite loops, this action CONSUMES the Execution token
    # and transitions the contract to a RETURN state, mirroring a single Solidity line of code.
    
    external_transient_read = Rule(
        lhs=[
            ["ExternalContract", "T_ExternalContract"],
            ["ExternalContract", "CF_EXTERNAL_EXEC"],   # Contract holds the EVM Call Stack
            ["Ledger", NodeType.LEDGER],
            ["Ledger", "State_DeltasNonZero"]           # Pool is unbalanced
        ],
        kept=[
            "ExternalContract", "Ledger", 
            "T_ExternalContract", NodeType.LEDGER, "State_DeltasNonZero"
        ],
        rhs=[
            # The execution advances to the return phase
            ["ExternalContract", "CF_EXTERNAL_RETURN"],
            # The contract successfully acquires the transient data
            ["ExternalContract", "State_ReadTransientData"]
        ]
    )
    rules.append(external_transient_read)

    return rules
