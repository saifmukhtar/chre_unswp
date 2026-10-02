from chre_api import Rule
from models.schema import NodeType, StateToken

def get_erc6909_rules():
    rules = []

    mint_claim = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", "State_DeltasNonZero"],
            ["Ledger", "T_DELTA_CREDIT", "Caller"],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED,
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Caller", "T_ERC6909_CLAIM"], ["Ledger", StateToken.DELTAS_ZERO]
        ]
    )
    rules.append(mint_claim)

    burn_own_claim = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC], ["Caller", "T_ERC6909_CLAIM"],       
            ["Ledger", NodeType.LEDGER], ["Ledger", "State_DeltasNonZero"],
            ["Ledger", "T_DELTA_DEBT", "Caller"],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED,
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[["Ledger", StateToken.DELTAS_ZERO]]
    )
    # -------------------------------------------------------------------------
    # transfer() / transferFrom()
    # -------------------------------------------------------------------------
    # Allows peer-to-peer transferring of claims. 
    # In CHRE, to transfer ownership, we must represent the Claim as a distinct node 
    # so we can delete its OWNS edge to the Sender and create an OWNS edge to the Receiver.
    transfer_claim = Rule(
        lhs=[
            ["ClaimNode", "T_ERC6909_CLAIM"],
            ["Sender", NodeType.USER], ["Sender", "OWNS", "ClaimNode"],
            ["Receiver", NodeType.USER],
            ["Sender", "LIVES_IN", "Singleton"], ["Receiver", "LIVES_IN", "Singleton"], ["ClaimNode", "LIVES_IN", "Singleton"]
        ],
        kept=["ClaimNode", "Receiver", "T_ERC6909_CLAIM", NodeType.USER, "LIVES_IN", "Singleton"],
        rhs=[
            ["Receiver", "OWNS", "ClaimNode"]
        ]
    )
    # Note: "Sender" and "OWNS" are NOT in kept, so the ownership edge is mathematically severed!
    rules.append(transfer_claim)

    # -------------------------------------------------------------------------
    # approve() / setOperator()
    # -------------------------------------------------------------------------
    # Allows a User to grant an external contract control over their claims.
    approve_operator = Rule(
        lhs=[
            ["Sender", NodeType.USER],
            ["Operator", "T_ExternalContract"],
            ["Sender", "LIVES_IN", "Singleton"], ["Operator", "LIVES_IN", "Singleton"]
        ],
        kept=["Sender", "Operator", NodeType.USER, "T_ExternalContract", "LIVES_IN", "Singleton"],
        rhs=[
            ["Operator", "IS_APPROVED_BY", "Sender"]
        ]
    )
    rules.append(approve_operator)

    return rules
