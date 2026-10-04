// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Safe shapes: fixed/immutable target, or an explicit allowlist check.
pragma solidity ^0.8.20;

contract SaferWallet {
    address public immutable LIBRARY;
    address public owner;
    mapping(address => bool) public approvedModule;

    constructor(address lib) {
        LIBRARY = lib;
        owner = msg.sender;
    }

    // delegatecall target is fixed at deployment, not caller-controlled.
    function callLibrary(bytes calldata data) external returns (bytes memory) {
        require(msg.sender == owner, "not owner");
        (bool ok, bytes memory ret) = LIBRARY.delegatecall(data);
        require(ok, "library call failed");
        return ret;
    }

    // Parameterised target, but only allowlisted modules are accepted.
    function execModule(address module, bytes calldata data) external {
        require(msg.sender == owner, "not owner");
        require(approvedModule[module], "module not approved");
        (bool ok, ) = module.delegatecall(data);
        require(ok, "module call failed");
    }

    function call(address to, uint256 value, bytes calldata data) external {
        require(msg.sender == owner, "not owner");
        (bool ok, ) = to.call{value: value}(data);
        require(ok, "call failed");
    }
}
