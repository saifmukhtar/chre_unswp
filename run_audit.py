import sys
import os

sys.path.insert(0, "/home/saif/chre")
sys.path.insert(0, "/home/saif/chre_unswp")

from chre_api import GraphUniverse, EngineConfig, Rule
from models.schema import NodeType, StateToken
from models.src.PoolManager import get_pool_manager_rules
from models.src.libraries.Hooks import get_hooks_library_rules
from models.src.ERC6909Claims import get_erc6909_rules
from models.exploits import get_exploits

def run_audit():
    print("==========================================================")
    print(" CEGAR LOOP 4: MODULAR SOURCE-MAPPED AUDIT")
    print("==========================================================")
    
    u = GraphUniverse(EngineConfig(semantics="DPO", verbose=False))

    u.add_rule(Rule(
        lhs=[], kept=[],
        rhs=[
            ["Singleton", NodeType.SINGLETON], ["Singleton", StateToken.LOCKED],
            ["Singleton", NodeType.CURRENCY],
            ["Ledger", NodeType.LEDGER], ["Ledger", StateToken.DELTAS_ZERO],
            ["Attacker", NodeType.USER], ["Attacker", StateToken.CF_IDLE],
            ["Victim", "T_Victim"]
        ]
    ))
    u.step()

    print("[+] Loading src/PoolManager.sol Rules...")
    for r in get_pool_manager_rules(): u.add_rule(r)
        
    print("[+] Loading src/ERC6909Claims.sol Rules...")
    for r in get_erc6909_rules(): u.add_rule(r)

    print("[+] Loading src/libraries/Hooks.sol Rules...")
    for r in get_hooks_library_rules(): u.add_rule(r)

    print("[+] Injecting Zero-Day Sandbox Exploits...")
    for r in get_exploits(): u.add_rule(r)

    print("[+] Exploring State Space...")
    u.evolve(15)

    os.makedirs("traces", exist_ok=True)
    u.save_graphml("traces/audit_result.graphml")
    
    with open("traces/audit_result.graphml", "r") as f:
        graphml_content = f.read()
        
    if "State_HACKED" in graphml_content:
        print("\n[!!!] CRITICAL ZERO-DAY CONFIRMED [!!!]")
    else:
        print("\n[+] Protocol is Secure. Attack vectors mitigated.")

if __name__ == "__main__":
    run_audit()
