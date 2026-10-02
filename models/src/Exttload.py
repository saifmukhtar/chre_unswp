from chre_api import Rule
from models.schema import NodeType, StateToken

def get_exttload_rules():
    rules = []
    
    external_transient_read = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["Caller", NodeType.USER],
            ["Caller", "CF_EXTERNAL_EXEC"],
            ["Ledger", NodeType.LEDGER],
            ["Ledger", "State_DeltasNonZero"],
            ["Caller", "LIVES_IN", "Singleton"],
            ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger",
            NodeType.SINGLETON, NodeType.USER, NodeType.LEDGER,
            "State_DeltasNonZero", "LIVES_IN"
        ],
        rhs=[
            ["Caller", "CF_EXTERNAL_RETURN"],
            ["Caller", "State_HACKED"]
        ]
    )
    rules.append(external_transient_read)
    
    return rules
