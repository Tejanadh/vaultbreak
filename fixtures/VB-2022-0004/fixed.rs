// ILLUSTRATIVE Anchor fixture. Not Cashio source.
// Near miss: UncheckedAccount stays, with the owner constraint on the field line.
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct SaferMint<'info> {
    /// CHECK: owner constrained
    #[account(owner = crate::ID)] pub bank: UncheckedAccount<'info>,
    /// CHECK: owner constrained
    #[account(owner = crate::ID)] pub collateral: UncheckedAccount<'info>,
    pub authority: Signer<'info>,
}
