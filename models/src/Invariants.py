import sys
sys.path.insert(0, "/home/saif/chre")
sys.path.insert(0, "/home/saif/chre_unswp")
from chre_api import Rule
from models.schema import NodeType, StateToken

def get_invariant_detectors():
    """
    Returns a list of 'Detector Rules'. 
    If any of these rules can successfully apply to the graph at the end of a transaction,
    it means a mathematically impossible state was reached (a True Zero-Day).
    """
    detectors = []

    # =========================================================================
    # INVARIANT 1: Solvency (No Unbacked Theft)
    # =========================================================================
    # A transaction is strictly secure if the PoolManager successfully returns 
    # to the LOCKED state, the transient ledger is DELTAS_ZERO, and the Attacker 
    # does NOT possess the physical CURRENCY (they must return it to settle).
    # If this rule matches, the Attacker successfully stole the money and walked away.
    
    detect_solvency_theft = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["Singleton", StateToken.LOCKED],       # The transaction finished successfully
            ["Ledger", NodeType.LEDGER],
            ["Ledger", StateToken.DELTAS_ZERO],     # The math claims everything is paid
            ["Attacker", NodeType.USER],
            ["Attacker", NodeType.CURRENCY]         # BUT the Attacker holds the physical currency!
        ],
        kept=[
            "Singleton", "Ledger", "Attacker", 
            NodeType.SINGLETON, StateToken.LOCKED, 
            NodeType.LEDGER, StateToken.DELTAS_ZERO, 
            NodeType.USER, NodeType.CURRENCY
        ],
        rhs=[
            ["Attacker", "State_CRITICAL_THEFT"]    # Flags the graph
        ]
    )
    detectors.append(detect_solvency_theft)

    return detectors
