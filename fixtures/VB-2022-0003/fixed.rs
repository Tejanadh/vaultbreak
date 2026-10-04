// ILLUSTRATIVE Anchor fixture. Not Wormhole source.
// Near miss: the same AccountInfo type stays, with the signer constraint on the field line.
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct SaferWithdraw<'info> {
    #[account(signer)] pub authority: AccountInfo<'info>,
    #[account(signer)] pub payer: AccountInfo<'info>,
    #[account(mut)]
    pub vault: Account<'info, Vault>,
}

pub struct Vault {
    pub balance: u64,
}
