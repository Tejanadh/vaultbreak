// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Shape: share price reads the raw token balance, so a donation moves the rate.
pragma solidity ^0.8.20;

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

contract VulnerableIndex {
    IERC20 public underlying;
    uint256 public totalShares;

    function exchangeRate() public view returns (uint256) {
        if (totalShares == 0) return 1e18;
        return underlying.balanceOf(address(this)) * 1e18 / totalShares;
    }

    function priceOfShare() public view returns (uint256) {
        return underlying.balanceOf(address(this)) * 1e18 / totalShares;
    }
}
