// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Shape: a wallet that lets the executor pick the delegatecall target.
pragma solidity ^0.8.20;

contract VulnerableWallet {
    address public implementation; // slot 0, shared with whatever the target writes
    address public owner;

    constructor(address impl) {
        implementation = impl;
        owner = msg.sender;
    }

    // Caller-chosen `to` + `operation == 1` means arbitrary code runs in this
    // contract's storage context.
    function execute(address to, uint256 value, bytes calldata data, uint8 operation) external {
        require(msg.sender == owner, "not owner");
        if (operation == 1) {
            (bool ok, ) = to.delegatecall(data);
            require(ok, "delegatecall failed");
        } else {
            (bool ok, ) = to.call{value: value}(data);
            require(ok, "call failed");
        }
    }

    // Same hazard, different spelling: `target` is a parameter.
    function forward(address target, bytes memory data) external returns (bytes memory) {
        (bool ok, bytes memory ret) = target.delegatecall(data);
        require(ok, "forward failed");
        return ret;
    }
}
