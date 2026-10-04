"""Vaultbreak custom Slither detector: ETH-sending call followed by a storage write.

Shape (Fei Rari / Compound-fork class): a public/external function sends ETH
or makes a value-carrying low-level call, and *afterwards on the same control-flow
path* writes contract storage (directly or through an internal call). That is the
check -> interaction -> effect ordering that leaves a reentrancy window.

Heuristics, stated honestly:
  * Functions with a modifier whose name contains "nonreentrant" / "lock" / "mutex"
    are skipped (we do not prove the modifier works).
  * Only value-carrying calls are considered (call{value}, send, transfer).
    ERC-777/ERC-721 callback hooks and read-only reentrancy are out of scope.
  * Slither already ships `reentrancy-eth`; this plugin exists to keep a small,
    self-contained, readable detector tied to one Vaultbreak class and to its
    fixtures. It is not claimed to be more precise than the built-in.
Own code (MIT). Not derived from Slither's built-in detector source.
"""
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification

GUARD_HINTS = ("nonreentrant", "lock", "mutex")


def _guarded(function) -> bool:
    return any(any(h in m.name.lower() for h in GUARD_HINTS) for m in function.modifiers)


def _writes(node):
    written = list(node.state_variables_written)
    for call in node.internal_calls:
        # Slither versions differ: entries are Function objects or call operations.
        f = getattr(call, "function", call)
        if hasattr(f, "all_state_variables_written"):
            written.extend(f.all_state_variables_written())
    return written


class VBEthSendBeforeWrite(AbstractDetector):
    ARGUMENT = "vb-eth-send-before-write"
    HELP = "ETH-sending call followed by a storage write on the same path"
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = "https://example.invalid/vaultbreak/vb-eth-send-before-write"  # placeholder, nothing published
    WIKI_TITLE = "ETH send before state update"
    WIKI_DESCRIPTION = "Value-carrying call precedes a storage write in the same function."
    WIKI_EXPLOIT_SCENARIO = "A callee reenters while accounting is stale."
    WIKI_RECOMMENDATION = "Update storage before the call (checks-effects-interactions) or use a verified mutex."

    def _scan(self, function):
        """Return [(send_node, write_node, [vars])] for each offending path."""
        out = []
        seen = set()
        stack = [(function.entry_point, None)]
        while stack:
            node, send = stack.pop()
            if node is None or (node.node_id, send.node_id if send else None) in seen:
                continue
            seen.add((node.node_id, send.node_id if send else None))
            if send is not None:
                w = _writes(node)
                if w:
                    out.append((send, node, sorted({v.name for v in w})))
            new_send = send
            if send is None and node.can_send_eth():
                new_send = node
            for son in node.sons:
                stack.append((son, new_send))
        return out

    def _detect(self):
        results = []
        for contract in self.compilation_unit.contracts_derived:
            for f in contract.functions_declared:
                if f.is_constructor or not f.is_implemented:
                    continue
                if f.visibility not in ("public", "external") or _guarded(f):
                    continue
                hits = self._scan(f)
                if not hits:
                    continue
                send, write, names = hits[0]
                info = [f, " sends ETH at ", send, " then writes storage (", ", ".join(names), ") at ", write, "\n"]
                results.append(self.generate_result(info))
        return results
