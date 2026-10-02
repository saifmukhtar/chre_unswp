from chre_api import Rule
from models.schema import NodeType, StateToken

def get_position_rules():
    rules = []
    
    # -------------------------------------------------------------------------
    # modifyLiquidity (ADD)
    # -------------------------------------------------------------------------
    # When a user adds liquidity, the Pool Manager generates a Position node.
    # The math dictates that the user now OWES the pool Tokens A and B.
    # We model this by generating T_DELTA_DEBT on the Ledger.
    add_liquidity = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED,
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Position", "T_Position"],
            ["Position", "OWNED_BY", "Caller"],
            ["Position", "IN_POOL", "Singleton"],
            ["Ledger", "T_DELTA_DEBT", "Caller"],
            ["Ledger", "State_DeltasNonZero"]
        ]
    )
    rules.append(add_liquidity)

    # -------------------------------------------------------------------------
    # modifyLiquidity (REMOVE)
    # -------------------------------------------------------------------------
    # When a user removes liquidity, they burn their Position.
    # The math dictates that the Pool now OWES the user Tokens A and B (plus fees).
    # We model this by generating T_DELTA_CREDIT on the Ledger.
    remove_liquidity = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Position", "T_Position"], ["Position", "OWNED_BY", "Caller"], ["Position", "IN_POOL", "Singleton"],
            ["Ledger", NodeType.LEDGER],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED,
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Ledger", "T_DELTA_CREDIT", "Caller"],
            ["Ledger", "State_DeltasNonZero"]
        ]
    )
    # Note: We do NOT keep the Position node, simulating its mathematical destruction/withdrawal
    rules.append(remove_liquidity)

    # -------------------------------------------------------------------------
    # malicious_hook_liquidity_accounting
    # -------------------------------------------------------------------------
    # Just like swap(), the Hook can intercept afterModifyLiquidity and apply a 
    # hookDelta. A malicious hook can use this to take T_DELTA_CREDIT for itself
    # during an LP's transaction, effectively stealing the LP's fees.
    malicious_hook_liquidity = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["HookContract", "T_ExternalContract"],
            ["Ledger", NodeType.LEDGER],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"], ["HookContract", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", "HookContract",
            NodeType.SINGLETON, StateToken.UNLOCKED, NodeType.USER, StateToken.CF_HOOK_EXEC, 
            NodeType.LEDGER, "T_ExternalContract", "LIVES_IN"
        ],
        rhs=[
            ["Ledger", "T_DELTA_CREDIT", "HookContract"],
            ["Ledger", "State_DeltasNonZero"]
        ]
    )
    rules.append(malicious_hook_liquidity)

    return rules
