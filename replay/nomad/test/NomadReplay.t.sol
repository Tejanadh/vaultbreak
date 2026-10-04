// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

// Replays the Nomad process transaction that was read from Ethereum.
// The DeFiHackLabs PoC is not copied. It is only a reference:
// https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/NomadBridge_exp.sol
// Run from this directory:
//   forge test --fork-url https://eth.drpc.org --fork-block-number 15259100 -vv

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}

interface Vm {
    function transact(bytes32 txHash) external;
}

contract NomadReplayTest {
    Vm constant vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    address constant WBTC = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;
    address constant RECIPIENT = 0xa8C83B1b30291A3a1a118058b5445cC83041Cd9d;
    bytes32 constant PROCESS_TX =
        0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460;

    function test_process_tx_moves_wbtc() public {
        uint256 beforeBal = IERC20(WBTC).balanceOf(RECIPIENT);
        vm.transact(PROCESS_TX);
        uint256 afterBal = IERC20(WBTC).balanceOf(RECIPIENT);
        // The process-tx receipt has one WBTC Transfer of 10000000000 raw units
        // (8 decimals) from the BridgeRouter to this recipient.
        require(afterBal - beforeBal == 10_000_000_000, "wbtc delta");
    }
}
