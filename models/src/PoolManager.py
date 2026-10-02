import sys
sys.path.insert(0, "/home/saif/chre")
sys.path.insert(0, "/home/saif/chre_unswp")
from chre_api import Rule
from models.schema import NodeType, StateToken

def get_pool_manager_rules():
    rules = []

    unlock_call = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.LOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_IDLE]
        ],
        kept=["Singleton", "Caller", NodeType.SINGLETON, NodeType.USER],
        rhs=[["Singleton", StateToken.UNLOCKED], ["Caller", StateToken.CF_HOOK_EXEC]]
    )
    rules.append(unlock_call)

    # take() generates a DEBT (-)
    take_flash_loan = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED], ["Singleton", NodeType.CURRENCY],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER
        ],
        rhs=[
            ["Caller", NodeType.CURRENCY], ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"]
        ]
    )
    rules.append(take_flash_loan)

    # settle() pays off a DEBT (-)
    settle_debt = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC], ["Caller", NodeType.CURRENCY],
            ["Ledger", NodeType.LEDGER], ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER
        ],
        rhs=[
            ["Singleton", NodeType.CURRENCY], ["Ledger", StateToken.DELTAS_ZERO]
        ]
    )
    rules.append(settle_debt)

    unlock_return = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", "CF_RETURN"],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO]
        ],
        kept=["Singleton", "Caller", "Ledger", NodeType.SINGLETON, NodeType.USER, NodeType.LEDGER, StateToken.DELTAS_ZERO],
        rhs=[["Singleton", StateToken.LOCKED], ["Caller", StateToken.CF_IDLE]]
    )
    rules.append(unlock_return)

    # FIXED: execute_swap no longer prints free CREDIT. 
    # To manipulate the pool price, the attacker must generate a DEBT that they have to pay back.
    execute_swap = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER
        ],
        rhs=[
            ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"]
        ]
    )
    rules.append(execute_swap)

    return rules
