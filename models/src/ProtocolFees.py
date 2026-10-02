from chre_api import Rule
from models.schema import NodeType, StateToken

def get_protocol_fee_rules():
    rules = []

    # -------------------------------------------------------------------------
    # setProtocolFeeController & setProtocolFee
    # -------------------------------------------------------------------------
    # The Owner can designate a Protocol Controller. The Controller can then 
    # configure the fee rate for a specific pool.
    set_protocol_controller = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["Owner", NodeType.USER], ["Owner", "IS_OWNER", "Singleton"],
            ["NewController", NodeType.USER]
        ],
        kept=["Singleton", "Owner", "NewController", NodeType.SINGLETON, NodeType.USER, "IS_OWNER"],
        rhs=[
            ["NewController", "T_ProtocolController"],
            ["NewController", "LIVES_IN", "Singleton"]
        ]
    )
    rules.append(set_protocol_controller)

    set_protocol_fee = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["ProtocolController", "T_ProtocolController"],
            ["ProtocolController", "LIVES_IN", "Singleton"]
        ],
        kept=["Singleton", "ProtocolController", NodeType.SINGLETON, "T_ProtocolController", "LIVES_IN"],
        rhs=[
            ["Singleton", "ProtocolFee_Enabled"]
        ]
    )
    rules.append(set_protocol_fee)

    # -------------------------------------------------------------------------
    # accrue_protocol_fee
    # -------------------------------------------------------------------------
    # During a swap or LP modification, the pool mathematically sets aside a 
    # portion of the fee for the Uniswap Protocol itself. 
    accrue_protocol_fee = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", "ProtocolFee_Enabled"],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Caller", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", NodeType.SINGLETON, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, "LIVES_IN"
        ],
        rhs=[
            ["ProtocolController", "T_ProtocolController"],
            ["ProtocolController", "LIVES_IN", "Singleton"],
            ["Singleton", "OWES_PROTOCOL_FEE", "ProtocolController"]
        ]
    )
    rules.append(accrue_protocol_fee)

    # -------------------------------------------------------------------------
    # collectProtocolFees
    # -------------------------------------------------------------------------
    # The Protocol Controller extracts physical currency directly from the pool.
    # CRITICAL: This explicitly BYPASSES the Transient Ledger (no T_DELTA_DEBT).
    collect_protocol_fees = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["Singleton", NodeType.CURRENCY],
            ["ProtocolController", "T_ProtocolController"],
            ["Singleton", "OWES_PROTOCOL_FEE", "ProtocolController"],
            ["ProtocolController", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "ProtocolController", NodeType.SINGLETON,
            "T_ProtocolController", "LIVES_IN"
        ],
        rhs=[
            ["ProtocolController", NodeType.CURRENCY]
        ]
    )
    rules.append(collect_protocol_fees)

    # -------------------------------------------------------------------------
    # malicious_sync_protocol_fee_theft
    # -------------------------------------------------------------------------
    # Because collectProtocolFees physically transfers tokens without using 
    # the transient ledger, an attacker can theoretically trigger a sync() 
    # reentrancy, forcing the pool to count the protocol's physical tokens 
    # as the attacker's own deposit!
    # (Note: Uniswap V4 added a custom revert 'ProtocolFeeCurrencySynced' to stop this).
    sync_fee_theft = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON],
            ["Singleton", NodeType.CURRENCY],
            ["Attacker", NodeType.USER], ["Attacker", StateToken.CF_HOOK_EXEC],
            ["ProtocolController", "T_ProtocolController"],
            ["Singleton", "OWES_PROTOCOL_FEE", "ProtocolController"],
            ["Attacker", "LIVES_IN", "Singleton"], ["ProtocolController", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Attacker", "ProtocolController", NodeType.SINGLETON,
            NodeType.USER, StateToken.CF_HOOK_EXEC, "T_ProtocolController", "LIVES_IN"
        ],
        rhs=[
            # Attacker intercepts the physical currency by triggering a sync() collision
            ["Attacker", NodeType.CURRENCY]
        ]
    )
    rules.append(sync_fee_theft)

    return rules
