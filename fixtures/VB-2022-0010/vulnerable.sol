// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Shape: caller-controlled token / source / spender reaching transferFrom or approve.
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

contract VulnerableRouter {
    // Anyone who has approved this router can have their tokens moved to `to`,
    // because `token` and `from` come straight from the caller.
    function claimTokens(address token, address from, address to, uint256 amount) external {
        IERC20(token).transferFrom(from, to, amount);
    }

    // The contract approves a spender chosen by the caller.
    function createCampaign(address token, address spender, uint256 amount) external {
        IERC20(token).approve(spender, amount);
    }
}
