# ACP / wACP Crypto-Asset Whitepaper

Last updated: 2026-10-04  
Canonical public page: https://ancap.cloud/whitepaper/acp  
BscScan / token-update whitepaper URL: https://ancap.cloud/whitepaper/acp  
Project whitepaper: https://ancap.cloud/whitepaper

ACP is the primary ANCAP platform asset for paid AI-workflow execution, platform credits,
creator earnings, paid API metering, and proof receipts.

**wACP** is the official wrapped ACP token on **BNB Smart Chain (BSC)**. Bridge ratio
**1 ACP ↔ 10 wACP** (cutover 2026-10-04). It is a reserve-backed representation of ACP for
EVM wallets, DEX pairs, and explorer listings. It is **not** a separate native supply.

## Official BSC identities

- Token: **wACP** (WACP)
- Network: BSC mainnet
- Contract: `0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402`
- Explorer: https://bscscan.com/token/0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402
- Bridge gateway: `0x57c24FF77B23a82328cb88914D4FD4EEBd93321b`
- 32×32 SVG logo (BscScan token update): https://ancap.cloud/wacp-logo-32.svg
- Bridge UI: https://ancap.cloud/bridge/acp-bsc
- Docs: https://ancap.cloud/docs/wacp

## Intended Utility

- Workflow settlement: ACP prices paid workflow runs.
- Paid API metering: API calls can debit ACP credits.
- Creator earnings: workflow creators can earn ACP from successful paid runs.
- Proof receipts: receipts can include ACP amount, workflow slug, input hash, result
  manifest, and proof URL.
- Platform accounting: for ANCAP pricing, 1 ACP is treated as 1 internal accounting unit.
  This is not a fiat peg, redemption promise, or guarantee of market value.
- Cross-chain access: wACP lets users hold ACP utility on BSC while reserves are managed
  through the documented bridge and reserve-proof surfaces.

## Technical Scope

The live implementation may include native ACP, wrapped ACP (wACP on BSC), custodial wallet
balances, and bridge components. Before treating any third-party token as official, verify
the full contract address against https://ancap.cloud and
https://ancap.cloud/docs/wacp/contracts.

Decimal note: ACP uses 8 decimals on the ANCAP chain; wACP on BSC uses 18 decimals with
the conversion target `wacp_wei = acp_smallest_unit * 10^11` (decimal pad × wrap 1 ACP ↔ 10 wACP).

Reserve invariant (target): minted wACP on BSC must not exceed locked/custodied ACP reserve
minus operational buffer. Public proofs: https://ancap.cloud/docs/wacp/reserve

## Risk Factors

- ACP / wACP may have limited liquidity and utility outside ANCAP.
- Crypto assets can be volatile and may lose value.
- Wallet, key-management, network, bridge, custody, or smart-contract failures can cause loss.
- Regulatory treatment can change by jurisdiction.
- AI workflow outputs can be incomplete or wrong and need human review.
- Bridging between ACP and wACP introduces custody, oracle/indexer, and operator operational risk.

## Regulatory Notice

Crypto-asset rules differ by country. In the EU, Regulation (EU) 2023/1114 on Markets in
Crypto-assets (MiCA) creates a framework for crypto-asset issuers and service providers.
ANCAP should obtain jurisdiction-specific legal review before any public token offer,
exchange listing, custody, promotion, or cross-border service launch.

## No Investment Promise

ANCAP does not promise income, yield, buybacks, redemption, appreciation, or investment
returns. ACP / wACP are described for platform utility and accounting inside ANCAP.
