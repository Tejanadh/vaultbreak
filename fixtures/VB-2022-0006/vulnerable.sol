// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Shape: a lending-style pool that sends ETH to the caller before it finishes
// updating its own accounting (check -> interaction -> effect).
pragma solidity ^0.8.20;

contract VulnerablePool {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;
    mapping(address => bool) public inMarket;

    function deposit() external payable {
        collateral[msg.sender] += msg.value;
        inMarket[msg.sender] = true;
    }

    function borrow(uint256 amount) external {
        require(collateral[msg.sender] >= (debt[msg.sender] + amount) * 2, "undercollateralised");
        debt[msg.sender] += amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
    }

    // Reentrancy window: ETH leaves before collateral is reduced, so a callback
    // can borrow against collateral that is already on its way out.
    function withdraw(uint256 amount) external {
        require(collateral[msg.sender] >= amount, "insufficient");
        require(collateral[msg.sender] - amount >= debt[msg.sender] * 2, "would be undercollateralised");
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
        collateral[msg.sender] -= amount;
    }

    // Same hazard, state change hidden behind an internal call.
    function exitMarket() external {
        require(debt[msg.sender] == 0, "has debt");
        uint256 amount = collateral[msg.sender];
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
        _leave(msg.sender);
    }

    function _leave(address who) internal {
        collateral[who] = 0;
        inMarket[who] = false;
    }
}
