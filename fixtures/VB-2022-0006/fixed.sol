// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Same pool, effects before interactions, plus one guarded function.
pragma solidity ^0.8.20;

contract SaferPool {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;
    mapping(address => bool) public inMarket;
    uint256 private _lock = 1;

    modifier nonReentrant() {
        require(_lock == 1, "reentrant");
        _lock = 2;
        _;
        _lock = 1;
    }

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

    // Checks -> effects -> interaction.
    function withdraw(uint256 amount) external {
        require(collateral[msg.sender] >= amount, "insufficient");
        require(collateral[msg.sender] - amount >= debt[msg.sender] * 2, "would be undercollateralised");
        collateral[msg.sender] -= amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
    }

    function exitMarket() external {
        require(debt[msg.sender] == 0, "has debt");
        uint256 amount = collateral[msg.sender];
        _leave(msg.sender);
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
    }

    // Order is the bad one, but the function is mutex-guarded.
    function withdrawGuarded(uint256 amount) external nonReentrant {
        require(collateral[msg.sender] >= amount, "insufficient");
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
        collateral[msg.sender] -= amount;
    }

    function _leave(address who) internal {
        collateral[who] = 0;
        inMarket[who] = false;
    }
}
