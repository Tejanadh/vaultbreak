// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
// Shape: a view-typed LP price read from external pool state mid-update.
pragma solidity ^0.8.20;

interface IVault {
    function getPoolTokens(bytes32 poolId)
        external view returns (address[] memory tokens, uint256[] memory balances, uint256 lastChangeBlock);
}

interface IERC20Like {
    function totalSupply() external view returns (uint256);
}

interface ICurvePool {
    function get_virtual_price() external view returns (uint256);
}

contract VulnerableLpOracle {
    IVault public immutable VAULT;
    bytes32 public immutable POOL_ID;
    address public immutable LP;
    ICurvePool public immutable CURVE;

    constructor(IVault v, bytes32 id, address lp, ICurvePool c) {
        VAULT = v;
        POOL_ID = id;
        LP = lp;
        CURVE = c;
    }

    // Reads balances and supply that can be momentarily inconsistent if called
    // from inside the pool's own ETH-payout callback.
    function getPrice() external view returns (uint256) {
        (, uint256[] memory balances, ) = VAULT.getPoolTokens(POOL_ID);
        uint256 total;
        for (uint256 i = 0; i < balances.length; i++) total += balances[i];
        return total * 1e18 / IERC20Like(LP).totalSupply();
    }

    function curveLpPrice() public view returns (uint256) {
        return CURVE.get_virtual_price();
    }
}
