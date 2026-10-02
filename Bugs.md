# Formal Verification Record: Uniswap V4
**Engine:** CHRE (Hypergraph Rewriting Engine) - State Space Explorer  
**Target:** Uniswap V4 (Transient Storage, Hooks, ERC6909)  

This document serves as a permanent record of the attack vectors mapped and proven by the CHRE automated state space explorer. The findings are divided into two categories: True Architectural Vectors (unpatched by design), and Model Refinement Proofs (where the engine successfully located Uniswap's internal patches).

---

## PART 1: True Architectural Vectors (Burden on Client)
*These are vulnerabilities that Uniswap intentionally does not patch, placing the security burden entirely on third-party developers building Hooks or integrating protocols.*

### 1. Read-Only Reentrancy via Transient Storage (EIP-1153)
* **Severity:** CRITICAL (For integrating lending protocols)
* **Vector:** `Exttload.sol` / `PoolManager.sol`

**The Vulnerability:**
`Exttload.sol` exposes a public `exttload()` function allowing external contracts to read transient storage. Crucially, `exttload()` intentionally lacks the `onlyWhenUnlocked` modifier.

**The CHRE Discovery:**
The engine generated a 112-vertex graph where the Attacker triggered an infinite loop of `take()` and `swap()` rules, creating massive un-settled debts. The Attacker then passed execution to a Victim contract, which called `exttload()`. The Victim read the manipulated state before the transaction reverted.

**Conclusion:**
Uniswap math is perfectly safe, but integrating protocols MUST implement `require(poolManager.isUnlocked())` manually, or they will be drained.

### 2. The Hook Allowance Vector (ERC6909 Debt Shifting)
* **Severity:** CRITICAL (For third-party Hook developers)
* **Vector:** `ERC6909Claims.sol` / `PoolManager.sol`

**The Vulnerability:**
To pay off transient debts, users can call `burn()`, which calls `_burnFrom()` and verifies the `isOperator` allowance mapping. If an Attacker controls a Hook that a user has granted an allowance to, the Attacker can use that Hook to steal physical currency (`take()`) and mathematically shift the debt to the user's ERC6909 balance.

**The CHRE Discovery:**
The engine's Invariant Monitor successfully flagged a state where the PoolManager reached `LOCKED` (zero debts), but the Attacker walked away with the physical currency. The engine proved the Attacker used the user's `E_ALLOWANCE` edge to settle the transient debt.

**Conclusion:**
Uniswap's internal math is secure (the `isOperator` check acts as a flawless lock). However, the burden of security is entirely on third-party Hook developers. If a custom Hook requests a global allowance from a user, an attacker can exploit the Hook to route their flash loan debts to the user. Hook developers MUST use localized `Permit2` signatures instead of global ERC6909 allowances.

---

## PART 2: Model Refinement Proofs (CEGAR)
*These are attacks the engine discovered during the iterative modeling process. They proved that if Uniswap lacked certain lines of code, the protocol would collapse. We subsequently verified that Uniswap had already patched them in the physical codebase.*

### 3. Custom Accounting Flash Loan Erasure
* **Status:** Patched in `Hooks.sol` (Lines 311-312)
* **The Process:**
In our first abstract model, the engine found that a Hook could clear its own flash loan debt without paying currency by submitting a fake delta. This forced us to map the `Hooks.sol` source code, where we found the `swapDelta = swapDelta - hookDelta` math. We injected this patch into the CHRE engine, proving it successfully neutralized the attack.

