# CoinGecko listing playbook — ANCAP rails (wACP / ACP / sACP)

Status: **ready to submit for wACP only after liquidity is raised**. Native ACP and sACP are not CoinGecko-listable yet for the reasons below.

## Place now (no CoinGecko approval)

These are already usable / self-hosted — see also <https://ancap.cloud/markets> and <https://ancap.cloud/listings.json>:

| Surface | Status | Link |
| --- | --- | --- |
| PancakeSwap trade-by-address | Live | [swap wACP/USDT](https://pancakeswap.finance/swap?inputCurrency=0x55d398326f99059fF775485246999027B3197955&outputCurrency=0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402) |
| DexTools | Live | [pair explorer](https://www.dextools.io/app/en/bnb/pair-explorer/0xf391ca2bcbab93afa23326ebf1e35db950841601) |
| GeckoTerminal | Indexed | [pool](https://www.geckoterminal.com/bsc/pools/0xf391ca2bcbab93afa23326ebf1e35db950841601) |
| BscScan | Live | [token](https://bscscan.com/token/0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402) |
| GoPlus | Live | [token security](https://gopluslabs.io/token-security/56/0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402) |
| ANCAP token list (Uniswap schema) | Self-hosted | <https://ancap.cloud/tokenlist.json> |
| Placement matrix | Self-hosted | [PUBLIC_PLACEMENT_MATRIX.md](./listings/PUBLIC_PLACEMENT_MATRIX.md) |
| Trust Wallet Assets | Pack ready | `docs/listings/trustwallet-smartchain-wacp/` |
| DexScreener | Waiting on volume | Auto after non-dust trades |
| CoinGecko coin page | Waiting on liquidity + Partners form | This playbook |

Official CoinGecko guides:
- [How to list a new cryptocurrency](https://support.coingecko.com/hc/en-us/articles/7291312302617-How-to-List-a-New-Cryptocurrency-on-CoinGecko)
- [Self-serve request form](https://support.coingecko.com/hc/en-us/articles/33084534107289-Guide-to-the-CoinGecko-Self-Serve-Request-Form)
- [Public verification post](https://support.coingecko.com/hc/en-us/articles/23725417857817-Verification-Guide-for-Listing-Update-Requests-on-CoinGecko)
- Partners hub: <https://www.coingecko.com/en/request-form> (or Partners Platform → Request & Listing → **New Coin/Token Listing**)

---

## Critical naming rule

Do **not** apply as ticker **`ACP`**.

- CoinGecko already lists an unrelated asset as **ACP** ([Arena Of Faith](https://www.coingecko.com/en/coins/arena-of-faith)).
- Official ANCAP BSC market asset is **`wACP`** (Wrapped ACP), BEP-20.
- Native **ACP** is the ANCAP L1 coin (`acp1…`) — not an EVM contract; CoinGecko cannot treat it as a BEP-20 listing.
- **sACP** — submit only after mainnet deploy + tracked market (see `docs/STABLECOIN_SACP_SPEC.md`).

List as:
- **Name:** Wrapped ACP  
- **Symbol:** wACP  
- **Network:** BNB Smart Chain (BEP-20)

---

## Current market truth (blocker)

GeckoTerminal already indexes the token (not yet linked to a CoinGecko coin id):

| Field | Value |
| --- | --- |
| Token | `0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402` |
| Pool | `wACP / USDT` PancakeSwap V2 `0xF391ca2bcBaB93Afa23326ebF1e35DB950841601` |
| GeckoTerminal pool | <https://www.geckoterminal.com/bsc/pools/0xf391ca2bcbab93afa23326ebf1e35db950841601> |
| GeckoTerminal API | `GET https://api.geckoterminal.com/api/v2/networks/bsc/tokens/0x349797e2f1a4fd722af2db181ab1c4ed7606f402` |
| `coingecko_coin_id` | `null` (not on CoinGecko yet) |
| Pool reserve (approx) | ~**$1** USD — **insufficient** |
| 24h volume | **$0** |

**Do not submit an Active Listing until** the PancakeSwap pool has meaningful depth and recurring trades (practical floor: at least several thousand USD reserves and non-zero daily volume over multiple days). CoinGecko rejects idle / dust pools.

Bootstrap liquidity playbook: [WACP_LIQUIDITY_V3_PLAYBOOK.md](./WACP_LIQUIDITY_V3_PLAYBOOK.md), [pancakeswap-listing-playbook.md](./pancakeswap-listing-playbook.md).

---

## Fill sheet — New Coin/Token Listing (wACP)

Copy into the CoinGecko Partners form.

### Identity
- Request type: **New Coin/Token Listing**
- Listing mode: **Active Listing** (only after liquidity) or **Preview** if CoinGecko still offers pre-launch for your account
- Coin/token name: `Wrapped ACP`
- Symbol: `wACP`
- Asset platform: `BNB Smart Chain`
- Contract address: `0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402`
- Decimals: `18`
- BscScan: <https://bscscan.com/token/0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402>
- Source (repo): `contracts/bridge-bsc/src/WACP.sol`

### Markets
- Primary market: PancakeSwap V3 `wACP/USDT` (after deployment); V2 pair remains reference
- Pair / pool: `0xF391ca2bcBaB93Afa23326ebF1e35DB950841601`
- Swap deep-link: <https://pancakeswap.finance/swap?inputCurrency=0x55d398326f99059fF775485246999027B3197955&outputCurrency=0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402>
- Liquidity pool UI: <https://pancakeswap.finance/liquidity/pool/bsc/0xF391ca2bcBaB93Afa23326ebF1e35DB950841601>
- GeckoTerminal: <https://www.geckoterminal.com/bsc/pools/0xf391ca2bcbab93afa23326ebf1e35db950841601>

### Project links
- Website: <https://ancap.cloud>
- Docs: <https://ancap.cloud/docs/wacp>
- Bridge: <https://ancap.cloud/docs/wacp/bridge>
- Reserve proof: <https://ancap.cloud/docs/wacp/reserve> · API `/api/v1/wacp/reserve-proof`
- Risks: <https://ancap.cloud/docs/wacp/risks>
- Contracts: <https://ancap.cloud/docs/wacp/contracts>
- Explorer (ACP L1 context): <https://ancap.cloud/acp>
- Whitepaper (platform): <https://ancap.cloud/whitepaper>
- ACP asset paper: repo `docs/WHITEPAPER_ACP.md` / published whitepaper routes
- Legal / market data: <https://ancap.cloud/legal/market-data>
- X: <https://x.com/ancap24news>
- Telegram: <https://t.me/ancap24news>
- GitHub: <https://github.com/ancapcloud/ancap>

### Branding
- Logo file: `frontend-app/public/wacp-logo.png`
- Public URL: <https://ancap.cloud/wacp-logo.png>
- CoinGecko wants square PNG ≥ **200×200** (prefer 512×512). Upscale/export a clean 512 PNG before attach if the current asset is too small/pixelated.

### Short description (EN)
> Wrapped ACP (wACP) is the official BEP-20 representation of ACP on BNB Smart Chain. It is minted and burned at **1 ACP ↔ 10 wACP** via the ANCAP bridge gateway so ACP can settle against BSC DeFi rails (starting with PancakeSwap wACP/USDT). Native ACP remains the ANCAP chain accounting unit; wACP is the wrapped market form. Not investment advice.

### Additional notes for reviewers
- Distinct from CoinGecko’s existing “ACP / Arena Of Faith” listing — different project, contract, and chain.
- Bridge gateway: `0x57c24FF77B23a82328cb88914D4FD4EEBd93321b`
- Official address index: <https://ancap.cloud> docs → `docs/OFFICIAL_CONTRACT_ADDRESSES.md`
- Circulating / max supply: report from bridge + reserve APIs at submission time; do not invent FDV.

---

## Public verification post (required)

Post from the **official** X account linked on the website (`@ancap24news`), then paste the post URL into the CoinGecko form.

Draft (fill Request ID after CoinGecko emails it):

```text
ANCAP is submitting Wrapped ACP (wACP) for listing on CoinGecko.

Contract (BSC): 0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402
GeckoTerminal: https://www.geckoterminal.com/bsc/pools/0xf391ca2bcbab93afa23326ebf1e35db950841601
Website: https://ancap.cloud
Docs: https://ancap.cloud/docs/wacp

CoinGecko Request ID: CLXXXXX
Contact: @ancap24news · support@ancap.cloud
```

After you receive `CL…` / `CU…` by email, reply in the same thread/post with the exact Request ID (per CoinGecko verification guide).

---

## Operator checklist

1. [ ] Seed PancakeSwap `wACP/USDT` liquidity (non-dust) and generate real volume for several days  
2. [ ] Confirm BscScan contract verification + logo clarity (512 PNG)  
3. [ ] Publish verification post on `@ancap24news`  
4. [ ] Submit Partners form with this fill sheet  
5. [ ] Reply with Request ID on the verification post  
6. [ ] After CoinGecko assigns a coin id, set env `COINGECKO_WACP_COIN_ID=<id>` (see `app/services/coingecko.py`) so `/v1/market/prices` uses the official CoinGecko feed  
7. [ ] sACP: separate listing only after DeploySacp + market  
8. [ ] Native ACP: only if/when CoinGecko supports the ANCAP L1 market feed

---

## What code already does

- Home ticker shows ACP / wACP / sACP + majors via `/api/v1/market/prices`.
- Until a CoinGecko coin id exists, wACP USD prefers **GeckoTerminal DEX spot** for the official pool, with desk rate as fallback.
- Legal disclosure: `/legal/market-data`.
