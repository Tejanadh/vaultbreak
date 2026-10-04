// ILLUSTRATIVE Anchor fixture. Not Cashio source.
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct VulnerableMint<'info> {
    /// CHECK: missing owner
    pub bank: UncheckedAccount<'info>,
    /// CHECK: missing owner
    pub collateral: UncheckedAccount<'info>,
    pub authority: Signer<'info>,
}
