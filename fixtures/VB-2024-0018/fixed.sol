// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Near miss: idleBalance() still calls balanceOf(address(this)), but that value
// is not the share price. A rule that flags every balanceOf(address(this)) is too wide.
pragma solidity ^0.8.20;

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

contract SaferIndex {
    IERC20 public underlying;
    uint256 public totalShares;
    uint256 public trackedCash;

    function exchangeRate() public view returns (uint256) {
        if (totalShares == 0) return 1e18;
        return trackedCash * 1e18 / totalShares;
    }

    function idleBalance() public view returns (uint256) {
        return underlying.balanceOf(address(this));
    }
}
