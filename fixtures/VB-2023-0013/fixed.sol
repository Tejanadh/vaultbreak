// SPDX-License-Identifier: MIT
// ILLUSTRATIVE FIXTURE (original code, not taken from any real contract).
pragma solidity ^0.8.20;

interface IVault {
    function getPoolTokens(bytes32 poolId)
        external view returns (address[] memory tokens, uint256[] memory balances, uint256 lastChangeBlock);
    function manageUserBalance(bytes[] memory ops) external payable;
}

interface IERC20Like {
    function totalSupply() external view returns (uint256);
}

interface IGuardLib {
    function ensureNotInVaultContext(address vault) external view;
}

contract SaferLpOracle {
    IVault public immutable VAULT;
    IGuardLib public immutable GUARD;
    bytes32 public immutable POOL_ID;
    address public immutable LP;

    constructor(IVault v, IGuardLib g, bytes32 id, address lp) {
        VAULT = v;
        GUARD = g;
        POOL_ID = id;
        LP = lp;
    }

    // Variant 1: state-mutating on purpose, so a guarded Vault call reverts mid-callback.
    function getPrice() external returns (uint256) {
        VAULT.manageUserBalance(new bytes[](0));
        (, uint256[] memory balances, ) = VAULT.getPoolTokens(POOL_ID);
        uint256 total;
        for (uint256 i = 0; i < balances.length; i++) total += balances[i];
        return total * 1e18 / IERC20Like(LP).totalSupply();
    }

    // Variant 2: view, but explicitly asserts the Vault is not mid-call.
    function getPriceView() external view returns (uint256) {
        GUARD.ensureNotInVaultContext(address(VAULT));
        (, uint256[] memory balances, ) = VAULT.getPoolTokens(POOL_ID);
        uint256 total;
        for (uint256 i = 0; i < balances.length; i++) total += balances[i];
        return total * 1e18 / IERC20Like(LP).totalSupply();
    }
}
