"""Application configuration."""
from functools import lru_cache
from urllib.parse import parse_qs, unquote, urlsplit

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"  # "development" | "production"

    @staticmethod
    def _is_placeholder_like(value: str) -> bool:
        normalized = (value or "").strip().lower()
        if not normalized:
            return False
        unsafe_phrases = {
            "change", "dev-secret", "change-me", "changeme",
            "secret", "example", "placeholder",
        }
        return any(phrase in normalized for phrase in unsafe_phrases)

    @staticmethod
    def _bundled_postgres_default_value() -> str:
        return "".join(("post", "gres"))

    @classmethod
    def _is_bundled_postgres_default_value(cls, value: str | None) -> bool:
        normalized = (value or "").strip().lower()
        return bool(normalized) and normalized == cls._bundled_postgres_default_value()

    @field_validator("environment", mode="before")
    @classmethod
    def _normalize_env(cls, v):
        return (v or "development").strip().lower()

    @model_validator(mode="after")
    def _check_production_secrets(self):
        """Fail fast if required production secrets are missing or have insecure placeholders."""
        if self.environment != "production":
            return self
        for name, value in [
            ("SECRET_KEY", self.secret_key),
            ("CURSOR_SECRET", self.cursor_secret),
            ("CRON_SECRET", self.cron_secret),
        ]:
            if not value:
                raise ValueError(
                    f"[PRODUCTION] {name} is not set. "
                    f"Set {name} as an environment variable before starting in production."
                )
            if self._is_placeholder_like(value):
                raise ValueError(
                    f"[PRODUCTION] {name} has an insecure placeholder: '{value}'. "
                    f"Set a real secret via environment variable."
                )

        database_url = (self.database_url or "").strip()
        if not database_url:
            raise ValueError(
                "[PRODUCTION] DATABASE_URL is not set. "
                "Set DATABASE_URL before starting in production."
            )

        parsed_database_url = urlsplit(database_url)
        socket_hosts = [value.strip() for value in parse_qs(parsed_database_url.query).get("host", []) if value.strip()]
        if not parsed_database_url.scheme or (parsed_database_url.hostname is None and not socket_hosts):
            raise ValueError(
                "[PRODUCTION] DATABASE_URL is not a valid absolute URI. "
                "Set a full SQLAlchemy database URL before starting in production."
            )

        database_username = parsed_database_url.username
        if database_username is not None:
            database_username = unquote(database_username)

        database_password = parsed_database_url.password
        if database_password is not None:
            database_password = unquote(database_password)

        if (
            self._is_bundled_postgres_default_value(database_username)
            and self._is_bundled_postgres_default_value(database_password)
        ):
            raise ValueError(
                "[PRODUCTION] DATABASE_URL still uses the insecure bundled database default credentials. "
                "Set a real database password before starting in production."
            )

        if database_password is not None:
            if self._is_bundled_postgres_default_value(database_password):
                raise ValueError(
                    "[PRODUCTION] DATABASE_URL still uses the insecure default database password. "
                    "Set a real database password before starting in production."
                )
            if self._is_placeholder_like(database_password):
                raise ValueError(
                    "[PRODUCTION] DATABASE_URL uses a placeholder-like database password. "
                    "Set a real database password before starting in production."
                )

        database_name = unquote(parsed_database_url.path.lstrip("/"))
        database_host = (parsed_database_url.hostname or "").lower()
        uses_bundled_postgres = database_host == "postgres" or any(host.lower() == "postgres" for host in socket_hosts)
        expected_postgres_user = (self.postgres_user or "postgres").strip()
        expected_postgres_db = (self.postgres_db or "ancap").strip()
        if uses_bundled_postgres and not database_password:
            raise ValueError(
                "[PRODUCTION] DATABASE_URL targets the bundled postgres service but does not include a password. "
                "Set DATABASE_URL with the real POSTGRES_PASSWORD before starting in production."
            )
        if uses_bundled_postgres and not database_username:
            raise ValueError(
                "[PRODUCTION] DATABASE_URL targets the bundled postgres service but does not include a username. "
                "Set DATABASE_URL to use POSTGRES_USER before starting in production."
            )
        if uses_bundled_postgres and database_username != expected_postgres_user:
            raise ValueError(
                "[PRODUCTION] DATABASE_URL username does not match POSTGRES_USER for the bundled postgres service. "
                "Keep them in sync before starting in production."
            )
        if uses_bundled_postgres and not database_name:
            raise ValueError(
                "[PRODUCTION] DATABASE_URL targets the bundled postgres service but does not include a database name. "
                "Set DATABASE_URL to target POSTGRES_DB before starting in production."
            )
        if uses_bundled_postgres and database_name != expected_postgres_db:
            raise ValueError(
                "[PRODUCTION] DATABASE_URL database name does not match POSTGRES_DB for the bundled postgres service. "
                "Keep them in sync before starting in production."
            )

        postgres_password = (self.postgres_password or "").strip()
        if uses_bundled_postgres:
            if not postgres_password:
                raise ValueError(
                    "[PRODUCTION] POSTGRES_PASSWORD is not set. "
                    "Set POSTGRES_PASSWORD when DATABASE_URL targets the bundled postgres service."
                )
            if self._is_bundled_postgres_default_value(postgres_password):
                raise ValueError(
                    "[PRODUCTION] POSTGRES_PASSWORD still uses the insecure default value. "
                    "Set a real database password before starting in production."
                )
            if self._is_placeholder_like(postgres_password):
                raise ValueError(
                    "[PRODUCTION] POSTGRES_PASSWORD uses a placeholder-like value. "
                    "Set a real database password before starting in production."
                )
            if database_password != postgres_password:
                raise ValueError(
                    "[PRODUCTION] DATABASE_URL password does not match POSTGRES_PASSWORD for the bundled postgres service. "
                    "Keep them in sync before starting in production."
                )
        return self

    # Auth -- required secrets validated above when environment=production
    secret_key: str = ""           # required in production -- no insecure default
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    debug: bool = False
    turnstile_secret_key: str = ""
    password_reset_token_ttl_minutes: int = 30
    public_app_url: str = "https://ancap.cloud"
    acp_wallet_recovery_master_key: str = ""
    platform_admin_user_ids: str = ""
    platform_admin_emails: str = ""
    metrics_scrape_token: str = ""
    allow_insecure_cron: bool = False

    # Opaque cursor -- required in production
    cursor_secret: str = ""        # required in production -- no insecure default

    @property
    def platform_admin_user_ids_allowlist(self) -> tuple[str, ...]:
        raw = self.platform_admin_user_ids or ""
        return tuple(item.strip() for item in raw.split(",") if item.strip())

    @property
    def platform_admin_emails_allowlist(self) -> tuple[str, ...]:
        raw = self.platform_admin_emails or ""
        return tuple(item.strip().lower() for item in raw.split(",") if item.strip())

    # Mail / alerts
    mail_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "ANCAP Support"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_timeout_seconds: int = 15
    login_alerts_enabled: bool = True

    # Instantly.ai API v2 (cold email / Unibox account management)
    instantly_enabled: bool = False
    instantly_api_key: str = ""
    instantly_api_base: str = "https://api.instantly.ai/api/v2"
    instantly_timeout_seconds: int = 30

    # Pagination
    default_page_limit: int = 50
    max_page_limit: int = 200

    # Circuit breaker
    circuit_breaker_n_runs: int = 20
    circuit_breaker_min_return_pct: float = -5.0
    circuit_breaker_k_killed: int = 5

    # Quarantine
    quarantine_hours: int = 24
    quarantine_max_orders_per_day: int = 3

    # L3: Proof-of-Agent
    registration_max_agents_per_day: int = 100
    stake_to_activate_amount: str = "0"
    stake_to_activate_currency: str = "ACP"

    # L3: Fees (platform revenue model — see docs/FINANCE_MODEL.md / docs/MARKET_ALIGNED_ECONOMY.md)
    run_fee_percent: str = "10"
    run_fee_amount: str = "0"
    run_fee_currency: str = "ACP"
    listing_fee_percent: str = "1"
    listing_fee_amount: str = "0"
    listing_fee_currency: str = "ACP"
    # Marketplace take rate: % of each paid order routed to the platform account.
    order_fee_percent: str = "10"

    # L3: On-chain
    chain_anchor_driver: str = "mock"
    acp_rpc_url: str = "https://acp1.ancap.cloud/rpc"
    ethereum_rpc_url: str = ""
    solana_rpc_url: str = ""
    # Comma-separated emails allowed to keep UserAcpWallet.address = custodial hot.
    # Everyone else is auto-reminted off the shared hot on login/personalize.
    # Default empty — set ACP_CUSTODIAL_HOT_HOLDER_EMAILS in the environment.
    acp_custodial_hot_holder_emails: str = ""

    @property
    def acp_custodial_hot_holder_emails_allowlist(self) -> tuple[str, ...]:
        raw = self.acp_custodial_hot_holder_emails or ""
        return tuple(sorted({p.strip().lower() for p in raw.split(",") if p.strip()}))

    # L3: Slashing
    moderation_slash_amount: str = "0"
    moderation_slash_currency: str = "ACP"

    # L3: Staking rewards
    staking_rewards_enabled: bool = True
    staking_rewards_currency: str = "ACP"
    staking_rewards_fees_share_percent: str = "40"
    staking_rewards_slash_share_percent: str = "100"
    staking_rewards_bootstrap_daily_emission: str = "300"
    staking_rewards_bootstrap_emission_cap_total: str = "108000"
    staking_rewards_apy_floor_percent: str = "3"
    staking_rewards_apy_ceiling_percent: str = "18"
    staking_rewards_min_stake_for_rewards: str = "25"

    # Wallet swap MVP
    ff_web_usdt_trc20_swap: bool = False
    usdt_trc20_deposit_address: str = "TNAbqPprJmqRa33UoRvYnUsVfDSgrJc3W1"
    # Emergency pin only when wacp_oracle_pin_desk=true; otherwise desk = 1 / wACP oracle.
    usdt_trc20_to_acp_rate: str = "1"
    wacp_oracle_pin_desk: bool = False
    wacp_oracle_min_usd: str = "0.00000001"
    wacp_oracle_max_usd: str = "1"
    wacp_oracle_stale_ttl_seconds: int = 3600
    usdt_trc20_acp_rate_min: str = "1"
    usdt_trc20_acp_rate_max: str = "1000000000000"
    # Platform take on workflow payment capture (percent of gross ACP)
    workflow_platform_fee_percent: str = "10"
    # OTC metals/goods desk (indicative ACP per gram; override via env JSON map if needed)
    otc_handoff_instructions: str = ""
    otc_metal_acp_per_gram: dict = {
        "gold": "250",
        "silver": "3",
        "platinum": "120",
        "palladium": "80",
    }
    # Commodities desk (indicative ACP per unit; see otc_intake.COMMODITY_UNITS)
    otc_commodity_acp_per_unit: dict = {
        "oil": "80",
        "natural_gas": "0.45",
        "uranium": "220",
        "coal": "110",
        "timber": "95",
        "sand": "18",
        "stone": "28",
        "gravel": "22",
        "iron_ore": "105",
        "copper_ore": "175",
        "lithium": "18",
        "rare_earths": "55",
    }

    # Mobile exchange office (ACP-hub multi-asset foundation)
    exchange_office_enabled: bool = True
    exchange_quote_ttl_seconds: int = 120
    # Optional override for ACP→USDT indicative quotes (else 1/usdt_trc20_to_acp_rate)
    exchange_acp_to_usdt_rate: str = ""
    # Placeholder fiat→ACP rates until partner on-ramp is live
    exchange_fiat_acp_rates: dict = {
        "usd": "1",
        "eur": "1.08",
        "fiat_usd": "1",
        "fiat_eur": "1.08",
    }
    # Numismatic face→ACP placeholders (override per currency)
    numismatic_face_acp_rates: dict = {
        "USD": "1",
        "EUR": "1.08",
        "GBP": "1.25",
        "UAH": "0.025",
        "RUB": "0.011",
        "CHF": "1.12",
        "JPY": "0.0067",
        "CNY": "0.14",
    }

    # Project treasury (on-chain ACP wallet: revenue in, expenses out).
    # Seed/keystore live outside the repo (operator Sicret storage).
    project_treasury_acp_address: str = "acp1qpw9nstpx5vtmqxdxmmud25dk0ae4s6a7cs7n902"
    project_treasury_keystore_file: str = ""

    # Welcome access grant on registration (promotional platform credit, not
    # USD cash and not a charitable donation). Tests set this to "0".
    welcome_grant_acp: str = "100"

    # Free ACP distribution kill-switch (welcome + faucet + referral signup bonus).
    # When disabled or when cumulative free ACP reaches the cap, new grants stop.
    free_acp_distribution_enabled: bool = True
    free_acp_distribution_cap: str = "1000000"
    # Onboarding faucet hard cap (server-side; clients must not exceed this).
    faucet_max_amount_acp: str = "10"
    # Anti-sybil: max distinct free-ACP registrations per hashed IP / device window.
    registration_signal_max_per_ip: int = 2
    registration_signal_max_per_device: int = 2
    registration_signal_window_hours: int = 168

    # Referral (bonuses are minted from the platform account — keep them
    # below expected lifetime platform revenue per referred user)
    referral_signup_bonus_acp: str = "25"
    referral_commission_share_rate: str = "0.10"
    referral_onchain_payout_enabled: bool = False
    referral_onchain_payout_keystore_file: str = ""
    referral_onchain_payout_fee_acp: str = ""

    # Cron job protection
    cron_secret: str | None = None

    # CORS
    cors_origins: str = (
        "https://ancap.cloud,https://www.ancap.cloud,"
        "http://localhost:3000,http://localhost:3001,http://localhost:3201,"
        "http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3201"
    )

    # Quality scorer
    quality_scorer_url: str = ""
    quality_scorer_timeout_seconds: int = 5

    # Feature flags
    ff_graph_auto_enforcement: bool = False
    ff_mutation_engine: bool = False
    ff_governance_auto_apply: bool = False
    ff_external_actions: bool = False
    ff_nl_strategy_compiler: bool = False
    ff_orbital_edge: bool = False
    ff_aeterna: bool = True
    ff_lunar_land: bool = True
    # Embodied / humanoid model adapters (UnifoLM etc.) — off until digest + review
    ff_embodied_adapter: bool = False

    # Participation gates
    participation_gates_enabled: bool = True

    # Wave 2: reputation and graph
    reputation_half_life_30d: float = 10.0
    reputation_half_life_90d: float = 30.0
    reputation_max_score_delta_per_recompute: float = 15.0
    graph_enforcement_suspicious_density: float = 0.5
    graph_enforcement_max_cluster_size: int = 10
    graph_enforcement_block_if_in_cycle: bool = True

    # wACP / BSC bridge
    bridge_rail_enabled: bool = False
    bridge_rail_paused: bool = False
    bridge_dry_run: bool = True
    bridge_bsc_rpc_url: str = ""
    bridge_wacp_contract: str = ""
    # Bootstrap V3 pool address (monitor + public docs). Does NOT switch the
    # checkout oracle unless wacp_oracle_use_v3=true (thin pool = manipulable).
    wacp_v3_pool: str = "0xe626bd3ef516c4f784e5d5fb46e297d9c0d7f5e1"
    wacp_v3_pool_url: str = (
        "https://pancakeswap.finance/liquidity/pool/bsc/0xe626bd3ef516c4f784e5d5fb46e297d9c0d7f5e1"
    )
    wacp_v3_position_nft: str = ""
    # Keep false until quote_smoke $100/$250/$500 slippage is acceptable.
    wacp_oracle_use_v3: bool = False
    # Minimum platform ledger revenue (ACP, 7d) before fee→V3 recycle is eligible.
    wacp_fee_recycle_min_revenue_acp: str = "50"
    bridge_gateway_contract: str = ""
    # Public transparency flags (do not hardcode true in API responses).
    bridge_bsc_contract_verified: bool = True
    bridge_token_metadata_live: bool = False
    bridge_bsc_private_key: str | None = None
    bridge_reserve_acp_address: str = ""
    # Extra reserve retained for ACP transaction fees on reverse payouts.
    bridge_operational_buffer_acp: str = "999"
    acp_hot_keystore_file: str = ""
    bridge_acp_confirmations: int = 30
    # Incremental ACP deposit scan (avoid full 1..tip walk every tick).
    bridge_acp_scan_lookback: int = 12
    bridge_acp_scan_max_blocks: int = 800
    bridge_acp_scan_windows_per_tick: int = 8
    # Auto-cancel unpaid forward intents after this many hours (0 disables).
    bridge_pending_deposit_ttl_hours: int = 72
    bridge_bsc_confirmations: int = 18
    bridge_operator_secret: str | None = None
    bsc_explorer_base: str = "https://bscscan.com"
    acp_explorer_tx_base: str = "https://ancap.cloud/explorer/tx"
    turnstile_site_key: str = ""

    # sACP — Stable ACP (USD-targeted, ACP-collateralized); docs/STABLECOIN_SACP_SPEC.md
    ff_sacp: bool = True
    sacp_paused: bool = False
    sacp_contract: str = ""
    sacp_gateway_contract: str = ""
    sacp_reserve_acp_address: str = ""
    sacp_acp_per_usd: str = "4"
    sacp_min_collateral_ratio: str = "1.50"

    # Digital passport (BSC soulbound)
    digital_passport_driver: str = "mock"  # mock | bsc
    digital_passport_contract: str = ""
    digital_passport_chain_id: str = "bsc"
    digital_passport_bsc_rpc_url: str = ""
    digital_passport_minter_private_key: str | None = None
    # Optional dedicated master key for education-doc ChaCha20-Poly1305 (v2).
    # Falls back to SECRET_KEY-derived material when empty.
    passport_docs_master_key: str = ""
    # Optional dedicated master key for DNA/RNA bank AES-256-GCM + HKDF-SHA384 (v1).
    dna_rna_bank_master_key: str = ""
    ff_dna_rna_bank: bool = True
    # Optional dedicated master key for perimeter Abrams Suite-B vault (AES-256-GCM + HKDF-SHA384).
    perimeter_cleanup_master_key: str = ""
    ff_perimeter_cleanup: bool = True

    # Economy desks (insurance/arena) — record_only until ledger rails land
    economy_desk_settlement_mode: str = "record_only"  # record_only | ledger
    ff_exponential_growth: bool = True
    exponential_growth_base_rate: str = "0.08"
    exponential_growth_max_depth: int = 8
    exponential_growth_passport_boost: str = "0.25"

    # Auction escrow (BSC operator-anchored)
    auction_escrow_driver: str = "mock"  # mock | bsc
    auction_escrow_contract: str = ""
    auction_escrow_bsc_rpc_url: str = ""
    auction_escrow_operator_private_key: str | None = None
    ff_tech_auction: bool = True
    # Optional dedicated master key for auction-deal X-Wing / PQC envelopes.
    auction_deal_master_key: str = ""

    mobile_wallet_min_app_version: str = "1.0.0"
    mobile_wallet_maintenance: bool = False
    mobile_wallet_maintenance_message: str | None = None
    mobile_wallet_support_url: str = "https://ancap.cloud/support"
    mobile_wallet_bridge_reverse_enabled: bool = False
    mobile_broadcast_rate_limit_per_minute: int = 10
    mobile_broadcast_rate_limit_burst: int = 5
    mobile_smart_pay_enabled: bool = True
    mobile_smart_pay_ai_fallback_enabled: bool = False
    mobile_smart_pay_auto_swap_enabled: bool = False
    mobile_smart_pay_max_image_bytes: int = 5_242_880
    mobile_smart_pay_max_slippage_bps: int = 500
    mobile_smart_pay_min_acp_fee_reserve: str = "1.0"

    # LLM
    llm_provider: str = "teneta_claude"
    workflow_operations_worker_enabled: bool = True
    llm_model: str = "claude-sonnet-4-6"
    anthropic_base_url: str = "https://api.tenetauniversity.com"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    llm_timeout_seconds: int = 45
    llm_max_tokens: int = 1800
    llm_daily_budget_acp: str = "250"
    llm_fallback_to_template: bool = True

    # Stripe / fiat adapter
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_api_base: str = "https://api.stripe.com/v1"

    # MoonPay Commerce / Helio (https://moonpay.hel.io/developer) — never commit real keys
    helio_public_key: str = ""
    helio_secret_key: str = ""
    helio_paylink_id: str = ""
    helio_webhook_shared_token: str = ""
    helio_network: str = "main"  # widget: main | test
    helio_primary_payment_method: str = "fiat"  # fiat | crypto
    helio_default_amount: str = "10"
    helio_currency_hint: str = "USDC"

    # WebID KYC/KYB partner slot (https://webid-solutions.com/en/) — never commit real keys.
    # Does NOT issue payment cards or Apple Pay; see docs/WEBID_KYC_AND_CARD_ISSUING_PATH.md.
    webid_enabled: bool = False
    webid_api_base: str = ""
    webid_client_id: str = ""
    webid_client_secret: str = ""

    # CoinGecko market data (indicative only; never commit real keys)
    coingecko_enabled: bool = True
    coingecko_api_key: str = ""
    coingecko_base_url: str = ""  # empty = auto demo/pro host
    coingecko_cache_ttl_seconds: int = 60
    # Set after CoinGecko approves Wrapped ACP listing (see docs/COINGECKO_LISTING_PLAYBOOK.md).
    coingecko_wacp_coin_id: str = ""

    # AccuWeather — Earth widget (https://www.accuweather.com/); never commit real keys
    accuweather_enabled: bool = True
    accuweather_api_key: str = ""
    accuweather_language: str = "en-us"

    # LLM cost tracking (ACP per 1M tokens; used to compute real provider cost)
    llm_cost_per_1m_input_tokens: str = "0"
    llm_cost_per_1m_output_tokens: str = "0"

    # Redis
    redis_url: str = ""
    rate_limit_per_minute: int = 120
    rate_limit_burst: int = 240

    # Database
    database_url: str = (
        "postgresql+asyncpg://"
        + ("post" + "gres")
        + ":"
        + ("post" + "gres")
        + "@localhost:5432/ancap"
    )
    postgres_user: str = "postgres"
    postgres_db: str = "ancap"
    postgres_password: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
