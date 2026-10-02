from enum import Enum

class NodeType(str, Enum):
    """
    Defines the strict structural types for the vertices in the CHRE graph.
    Inheriting from str allows these to be passed directly into CHRE rules.
    """
    # System Architecture
    SINGLETON = "T_Singleton"
    LEDGER = "T_Ledger"        # The EIP-1153 Transient Storage
    
    # Actors
    ATTACKER = "T_Attacker"
    HOOK = "T_Hook"
    USER = "T_User"
    
    # Tokens & Value
    CURRENCY = "T_Currency"    # Represents ETH or ERC20
    DELTA = "T_Delta"          # A debt/credit record on the ledger

class StateToken(str, Enum):
    """
    Defines the Control Flow and State markers. 
    In structural graph rewriting, these act as the "Program Counter" 
    or the current lock state of a contract.
    """
    # Singleton Lock States
    UNLOCKED = "State_Unlocked"
    LOCKED = "State_Locked"
    
    # Control Flow (Who has execution rights?)
    CF_IDLE = "CF_Idle"
    CF_SWAP_ACTIVE = "CF_SwapActive"
    CF_HOOK_EXEC = "CF_HookExec"
    CF_TAKE_EXEC = "CF_TakeExec"

    # Accounting States
    DELTAS_ZERO = "State_DeltasZero" # Represents NonzeroDeltaCount == 0
