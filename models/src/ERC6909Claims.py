import sys
sys.path.insert(0, "/home/saif/chre")
sys.path.insert(0, "/home/saif/chre_unswp")
from chre_api import Rule
from models.schema import NodeType, StateToken

def get_erc6909_rules():
    rules = []

    # mint() strictly requires a CREDIT (+)
    mint_claim = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", "State_DeltasNonZero"],
            ["Ledger", "T_DELTA_CREDIT", "Caller"] 
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED,
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER
        ],
        rhs=[
            ["Caller", "T_ERC6909_CLAIM"], ["Ledger", StateToken.DELTAS_ZERO]
        ]
    )
    rules.append(mint_claim)

    # burn() strictly requires a DEBT (-)
    burn_own_claim = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC], ["Caller", "T_ERC6909_CLAIM"],       
            ["Ledger", NodeType.LEDGER], ["Ledger", "State_DeltasNonZero"],
            ["Ledger", "T_DELTA_DEBT", "Caller"] 
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED,
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER
        ],
        rhs=[["Ledger", StateToken.DELTAS_ZERO]]
    )
    rules.append(burn_own_claim)

    return rules
