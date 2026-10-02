from chre_api import Rule
from models.schema import NodeType, StateToken

def get_pool_manager_rules():
    rules = []

    unlock_call = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.LOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_IDLE],
            ["Caller", "LIVES_IN", "Singleton"]
        ],
        kept=["Singleton", "Caller", NodeType.SINGLETON, NodeType.USER, "LIVES_IN"],
        rhs=[["Singleton", StateToken.UNLOCKED], ["Caller", StateToken.CF_HOOK_EXEC]]
    )
    rules.append(unlock_call)

    take_flash_loan = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED], ["Singleton", NodeType.CURRENCY],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Caller", NodeType.CURRENCY], ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"]
        ]
    )
    rules.append(take_flash_loan)

    settle_debt = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC], ["Caller", NodeType.CURRENCY],
            ["Ledger", NodeType.LEDGER], ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
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
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=["Singleton", "Caller", "Ledger", NodeType.SINGLETON, NodeType.USER, NodeType.LEDGER, StateToken.DELTAS_ZERO, "LIVES_IN"],
        rhs=[["Singleton", StateToken.LOCKED], ["Caller", StateToken.CF_IDLE]]
    )
    rules.append(unlock_return)

    execute_swap = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"]
        ]
    )
    # -------------------------------------------------------------------------
    # donate()
    # -------------------------------------------------------------------------
    # Allows anyone to donate tokens to the in-range LPs. 
    # Generates a Debt for the Caller, which they must settle before unlock.
    donate_liquidity = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"]
        ]
    )
    rules.append(donate_liquidity)

    # -------------------------------------------------------------------------
    # sync() / clear()
    # -------------------------------------------------------------------------
    # sync() allows a user to send ERC20s directly to the pool, turning physical
    # tokens into a mathematical Credit. clear() allows the pool to confiscate
    # dust/unclaimed credits. We model both as ledger state transitions.
    sync_and_clear = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.UNLOCKED],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_HOOK_EXEC], ["Caller", NodeType.CURRENCY],
            ["Ledger", NodeType.LEDGER], ["Ledger", "T_DELTA_DEBT", "Caller"], ["Ledger", "State_DeltasNonZero"],
            ["Caller", "LIVES_IN", "Singleton"], ["Ledger", "LIVES_IN", "Singleton"]
        ],
        kept=[
            "Singleton", "Caller", "Ledger", NodeType.SINGLETON, StateToken.UNLOCKED, 
            NodeType.USER, StateToken.CF_HOOK_EXEC, NodeType.LEDGER, "LIVES_IN"
        ],
        rhs=[
            ["Ledger", StateToken.DELTAS_ZERO]
        ]
    )
    # -------------------------------------------------------------------------
    # initialize()
    # -------------------------------------------------------------------------
    # Initializes a new pool. Crucially, this does NOT require the onlyWhenUnlocked
    # modifier. It triggers beforeInitialize and afterInitialize hooks, handing
    # execution control to an external contract.
    initialize_pool = Rule(
        lhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", "Uninitialized"],
            ["Caller", NodeType.USER], ["Caller", StateToken.CF_IDLE],
            ["Caller", "LIVES_IN", "Singleton"]
        ],
        kept=["Singleton", "Caller", NodeType.SINGLETON, NodeType.USER, "LIVES_IN"],
        rhs=[
            ["Singleton", "Initialized"],
            ["Caller", StateToken.CF_HOOK_EXEC]  # The Hook hijacking vector
        ]
    )
    rules.append(initialize_pool)

    return rules
