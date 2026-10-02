import sys
import os
sys.path.insert(0, "/home/saif/chre")
sys.path.insert(0, "/home/saif/chre_unswp")
from chre_api import Rule
from models.schema import NodeType, StateToken

def get_hooks_library_rules():
    """
    Returns the strict mathematical rules translated directly 
    from Uniswap V4's Hooks.sol library.
    """
    rules = []

    # =========================================================================
    # FUNCTION: afterSwap (Lines 311-312)
    # "swapDelta = swapDelta - hookDelta;"
    # =========================================================================
    # This rule is the fundamental physics patch that prevents Hooks from 
    # printing free money. If a Hook returns a custom delta to clear its debt,
    # that exact debt is subtracted from the Swapper. 
    # Because our Attacker is acting as both the Hook and the Swapper, 
    # the Debt Edge (DELTA) is kept securely attached to them.
    
    enforce_zero_sum_delta = Rule(
        lhs=[
            ["Attacker", NodeType.USER],
            ["Attacker", StateToken.CF_HOOK_EXEC],  # Hook has execution control
            ["Ledger", NodeType.LEDGER],
            ["Ledger", "State_DeltasNonZero"],      # Ledger has an active debt
            ["Ledger", NodeType.DELTA, "Attacker"]  # Attacker owes the debt
        ],
        kept=[
            "Attacker", "Ledger", 
            NodeType.USER, NodeType.LEDGER, 
            "State_DeltasNonZero", NodeType.DELTA   # THE PATCH: The debt edge cannot be deleted!
        ],
        rhs=[
            # The Hook finishes its custom accounting and returns control to the PoolManager
            ["Attacker", "CF_RETURN"]
        ]
    )
    rules.append(enforce_zero_sum_delta)

    return rules
