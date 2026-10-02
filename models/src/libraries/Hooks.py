from chre_api import Rule
from models.schema import NodeType, StateToken

def get_hooks_library_rules():
    rules = []

    enforce_zero_sum_delta = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["Attacker", NodeType.USER],
            ["Attacker", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER],
            ["Ledger", "State_DeltasNonZero"],
            ["Ledger", "T_DELTA_DEBT", "Attacker"],
            ["Attacker", "LIVES_IN", "Singleton"],
            ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Attacker", "Ledger", 
            NodeType.SINGLETON, NodeType.USER, NodeType.LEDGER, 
            "State_DeltasNonZero", "T_DELTA_DEBT", "LIVES_IN"
        ],
        rhs=[
            ["Attacker", "CF_RETURN"]
        ]
    )
    rules.append(enforce_zero_sum_delta)

    return rules
