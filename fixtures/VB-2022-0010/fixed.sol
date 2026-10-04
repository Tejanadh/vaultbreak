// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

contract SaferRouter {
    address public immutable LOCKER;
    mapping(address => bool) public allowedToken;

    constructor(address locker) {
        LOCKER = locker;
    }

    // Tokens are only ever pulled from the caller themself.
    function deposit(address token, address to, uint256 amount) external {
        require(allowedToken[token], "token not allowed");
        IERC20(token).transferFrom(msg.sender, to, amount);
    }

    // `from` is a parameter but is pinned to the caller.
    function depositFor(address token, address from, address to, uint256 amount) external {
        require(from == msg.sender, "from must be caller");
        IERC20(token).transferFrom(from, to, amount);
    }

    // Approval goes to a fixed, deploy-time spender.
    function createCampaign(address token, uint256 amount) external {
        IERC20(token).approve(LOCKER, amount);
    }
}
