// ILLUSTRATIVE Anchor fixture. Not Wormhole source.
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct VulnerableWithdraw<'info> {
    pub authority: AccountInfo<'info>,
    pub payer: AccountInfo<'info>,
    #[account(mut)]
    pub vault: Account<'info, Vault>,
}

pub struct Vault {
    pub balance: u64,
}
