type TokenomicsBucket = {
  key: string;
  label: string;
  acp: string;
  utxo_count: number;
};

export type WalletBalance = {
  address: string;
  units: string;
  acp: string;
  utxo_count?: number;
  on_chain_acp?: string | null;
  on_chain_at_deposit_acp?: string | null;
  ledger_credits_acp?: string | null;
  platform_ledger_acp?: string | null;
  headline_acp?: string | null;
  primary_acp?: string | null;
  primary_kind?:
    | "on_chain"
    | "platform_credits"
    | "operator_total"
    | "chain_supply"
    | null;
  balance_status?: string | null;
  probe_status?: "live" | "degraded" | "unavailable" | null;
  in_work_acp?: string;
  in_work_staked_acp?: string;
  in_work_ledger_acp?: string;
  staked_acp?: string | null;
  reserved_total_acp?: string | null;
  available_acp?: string;
  withdrawable_now_acp?: string | null;
  withdraw_source?: "personal_utxo" | "custodial_hot" | "none" | null;
  platform_credits_acp?: string | null;
  operator_hot_live_acp?: string | null;
  operator_controlled_live_acp?: string | null;
  chain_supply_acp?: string | null;
  supply_cap_acp?: string | null;
  supply_invariant_ok?: boolean | null;
  tokenomics_buckets?: TokenomicsBucket[] | null;
  view_mode?: "user" | "operator_hot" | null;
  vested_unlocked_acp?: string;
  vested_locked_acp?: string;
  balance_note?: string;
  chain_height?: number | null;
};

export type ChainTransaction = {
  txid: string;
  block_height: number;
  block_time: string;
  confirmations: number;
  direction: "in" | "out" | "self";
  sent_units: string;
  sent_acp: string;
  received_units: string;
  received_acp: string;
  net_units: string;
  net_acp: string;
};
