"""SQLAlchemy models for ANCAP Core Engine."""
import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Integer,
    BigInteger,
    Boolean,
    Numeric,
    DateTime,
    Date,
    ForeignKey,
    Enum as SQLEnum,
    Index,
    Column,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


# --- Enums (Python enum for DB layer) ---
class AgentStatusEnum(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    quarantined = "quarantined"


class VerticalStatusEnum(str, enum.Enum):
    proposed = "proposed"
    approved = "approved"
    active = "active"
    deprecated = "deprecated"
    rejected = "rejected"


class StrategyStatusEnum(str, enum.Enum):
    draft = "draft"
    published = "published"
    paused = "paused"
    retired = "retired"


class ListingStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class OrderStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentIntentStatusEnum(str, enum.Enum):
    requires_payment = "requires_payment"
    reserved = "reserved"
    captured = "captured"
    refunded = "refunded"
    cancelled = "cancelled"
    failed = "failed"


class RefundRequestStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SubscriptionStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    cancelled = "cancelled"
    past_due = "past_due"


class SubscriptionBillingPeriodEnum(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"


class PayoutRequestStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
    failed = "failed"


class AccessScopeEnum(str, enum.Enum):
    view = "view"
    execute = "execute"
    allocate = "allocate"


class RiskProfileEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    experimental = "experimental"


class PoolStatusEnum(str, enum.Enum):
    active = "active"
    halted = "halted"
    archived = "archived"


class LedgerEventTypeEnum(str, enum.Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    allocate = "allocate"
    deallocate = "deallocate"
    pnl = "pnl"
    fee = "fee"
    refund = "refund"
    transfer = "transfer"
    contract_escrow = "contract_escrow"
    contract_payout = "contract_payout"
    stake = "stake"
    unstake = "unstake"
    slash = "slash"


class RunStateEnum(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    killed = "killed"


class OwnerTypeEnum(str, SQLEnum):
    user = "user"
    agent = "agent"
    pool_treasury = "pool_treasury"


# --- Identity ---
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(80), nullable=True)
    stripe_customer_id = Column(String(64), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class UserAcpWallet(Base):
    __tablename__ = "user_acp_wallets"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    address = Column(String(128), nullable=False, unique=True, index=True)
    encrypted_mnemonic = Column(Text, nullable=False)
    salt_b64 = Column(Text, nullable=False)
    nonce_b64 = Column(Text, nullable=False)
    secret_box_version = Column(Integer, nullable=False, default=1)
    secret_wrapped_b64 = Column(Text, nullable=True)
    secret_wrap_salt_b64 = Column(Text, nullable=True)
    secret_wrap_nonce_b64 = Column(Text, nullable=True)
    recovery_secret_box_b64 = Column(Text, nullable=True)
    recovery_secret_nonce_b64 = Column(Text, nullable=True)
    recovery_enabled = Column(Boolean, nullable=False, default=False)
    derivation_path = Column(String(128), nullable=False, default="m/44'/0'/0'/0/0")
    view_pubkey_wire_hex = Column(Text, nullable=True)
    privacy_next_index = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class UserAcpAddressBinding(Base):
    """Historical + active ACP address bindings for indexer watchlists / history restore."""

    __tablename__ = "user_acp_address_bindings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    address = Column(String(128), nullable=False, index=True)
    kind = Column(String(32), nullable=False)  # deposit|privacy|previous_deposit|imported
    bound_at = Column(DateTime(timezone=True), nullable=False)
    unbound_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("uq_user_acp_address_bindings_user_address", "user_id", "address", unique=True),
    )


class UserAcpPrivacyAddress(Base):
    __tablename__ = "user_acp_privacy_addresses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    address = Column(String(128), nullable=False, unique=True, index=True)
    sub_index = Column(Integer, nullable=False)
    label = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class UserEvmWallet(Base):
    __tablename__ = "user_evm_wallets"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    wallet_address = Column(String(66), nullable=False, unique=True, index=True)
    chain_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class WalletAuthChallenge(Base):
    __tablename__ = "wallet_auth_challenges"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    wallet_address = Column(String(66), nullable=False, index=True)
    chain_id = Column(Integer, nullable=True)
    nonce = Column(String(128), nullable=False, unique=True, index=True)
    message = Column(Text, nullable=False)
    issued_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(80), nullable=False)
    public_key = Column(Text, nullable=True)
    roles = Column(JSONB, nullable=False)  # list of AgentRoleEnum values
    status = Column(SQLEnum(AgentStatusEnum), default=AgentStatusEnum.active)
    metadata_ = Column("metadata", JSONB, nullable=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    attestation_id = Column(UUID(as_uuid=False), ForeignKey("agent_attestations.id", ondelete="SET NULL"), nullable=True)
    created_by_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)  # when stake/attestation activated
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    strategies = relationship("Strategy", back_populates="owner_agent", foreign_keys="Strategy.owner_agent_id")
    created_by_agent = relationship("Agent", remote_side="Agent.id", foreign_keys=[created_by_agent_id])
    owner_user = relationship("User", foreign_keys=[owner_user_id])


class AgentProfile(Base):
    __tablename__ = "agent_profiles"

    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(80), nullable=True)
    key_prefix = Column(String(24), nullable=False, unique=True, index=True)
    key_hash = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=True)
    metadata_json = Column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ApiUsageEvent(Base):
    __tablename__ = "api_usage_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    api_key_prefix = Column(String(24), nullable=True, index=True)
    product_slug = Column(String(80), nullable=False, index=True)
    endpoint = Column(String(160), nullable=False)
    status = Column(String(32), nullable=False, default="captured", index=True)
    amount_currency = Column(String(10), nullable=False, index=True)
    amount_value = Column(Numeric(36, 18), nullable=False)
    ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    request_hash = Column(String(64), nullable=False, index=True)
    response_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    agent = relationship("Agent", foreign_keys=[agent_id])
    owner_user = relationship("User", foreign_keys=[owner_user_id])

    __table_args__ = (
        Index("ix_api_usage_events_agent_created", "agent_id", "created_at"),
        Index("ix_api_usage_events_owner_created", "owner_user_id", "created_at"),
        Index("ix_api_usage_events_product_status", "product_slug", "status"),
    )


class AgentLinkTypeEnum(str, enum.Enum):
    same_owner = "same_owner"
    same_key = "same_key"
    manual = "manual"
    heuristic = "heuristic"


class AgentLink(Base):
    __tablename__ = "agent_links"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    linked_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    link_type = Column(String(32), nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("uq_agent_links_pair", "agent_id", "linked_agent_id", unique=True),)


class AgentRelationship(Base):
    """Agent Graph Index (ROADMAP 2.1): edges for anti-sybil, reciprocity, cycles.
    One row per interaction (order, review, etc.); weight = amount or 1.
    """
    __tablename__ = "agent_relationships"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    source_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    target_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(32), nullable=False, index=True)  # order, review, contract, grant, same_owner
    weight = Column(Numeric(36, 18), nullable=False, default=1)
    ref_type = Column(String(32), nullable=True)  # order, review, ...
    ref_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_agent_relationships_pair_type", "source_agent_id", "target_agent_id", "relation_type"),
        Index("ix_agent_relationships_target", "target_agent_id", "relation_type"),
    )


# --- Verticals ---
class Vertical(Base):
    __tablename__ = "verticals"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(80), nullable=False, index=True)
    status = Column(SQLEnum(VerticalStatusEnum), default=VerticalStatusEnum.proposed)
    owner_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class VerticalSpec(Base):
    __tablename__ = "vertical_specs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    vertical_id = Column(UUID(as_uuid=False), ForeignKey("verticals.id", ondelete="CASCADE"), nullable=False)
    spec_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# --- Strategies ---
class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False, index=True)
    vertical_id = Column(UUID(as_uuid=False), ForeignKey("verticals.id"), nullable=False)
    status = Column(SQLEnum(StrategyStatusEnum), default=StrategyStatusEnum.draft)
    owner_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False)
    summary = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)  # list of strings
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    owner_agent = relationship("Agent", back_populates="strategies", foreign_keys=[owner_agent_id])
    versions = relationship("StrategyVersion", back_populates="strategy", order_by="StrategyVersion.created_at.desc()")
    listings = relationship("Listing", back_populates="strategy")


class StrategyVersion(Base):
    __tablename__ = "strategy_versions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    semver = Column(String(32), nullable=False)
    workflow_json = Column(JSONB, nullable=False)
    param_schema = Column(JSONB, nullable=True)
    changelog = Column(Text, nullable=True)
    strategy_policy = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="versions")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    strategy_version_id = Column(
        UUID(as_uuid=False),
        ForeignKey("strategy_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    fee_model = Column(JSONB, nullable=False)
    status = Column(SQLEnum(ListingStatusEnum), default=ListingStatusEnum.active)
    terms_url = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="listings")


# --- Orders / Access ---
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=False), ForeignKey("listings.id"), nullable=False)
    buyer_type = Column(String(20), nullable=False)  # user, agent, pool
    buyer_id = Column(UUID(as_uuid=False), nullable=False)
    status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.pending)
    amount_currency = Column(String(10), nullable=True)
    amount_value = Column(Numeric(36, 18), nullable=True)
    payment_method = Column(String(64), nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class WorkflowRunRecord(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_slug = Column(String(120), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="quoted", index=True)
    quoted_amount = Column(Numeric(36, 18), nullable=False)
    quoted_currency = Column(String(10), nullable=False)
    payment_currency = Column(String(10), nullable=False)
    unlock_full_result = Column(Boolean, nullable=False, default=True)
    inputs_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    preview_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    result_json = Column(JSONB, nullable=True)
    receipt_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_user = relationship("User", foreign_keys=[owner_user_id])

    __table_args__ = (
        Index("ix_workflow_runs_owner_created", "owner_user_id", "created_at"),
        Index("ix_workflow_runs_owner_slug", "owner_user_id", "workflow_slug"),
    )


class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_run_id = Column(UUID(as_uuid=False), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    intent_type = Column(String(32), nullable=False, default="workflow_run", index=True)
    status = Column(String(32), nullable=False, default=PaymentIntentStatusEnum.requires_payment.value, index=True)
    payment_method = Column(String(64), nullable=False, default="credits")
    amount_currency = Column(String(10), nullable=False, index=True)
    amount_value = Column(Numeric(36, 18), nullable=False)
    payment_reference = Column(String(128), nullable=True, index=True)
    stripe_payment_intent_id = Column(String(128), nullable=True, unique=True, index=True)
    reserved_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    capture_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    refund_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    provider_payload_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_user = relationship("User", foreign_keys=[owner_user_id])
    workflow_run = relationship("WorkflowRunRecord", foreign_keys=[workflow_run_id])

    __table_args__ = (
        Index("ix_payment_intents_owner_created", "owner_user_id", "created_at"),
        Index("ix_payment_intents_run_status", "workflow_run_id", "status"),
    )


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    payment_intent_id = Column(UUID(as_uuid=False), ForeignKey("payment_intents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_currency = Column(String(10), nullable=False, default="ACP")
    amount_value = Column(Numeric(36, 18), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default=RefundRequestStatusEnum.pending.value, index=True)
    admin_notes = Column(Text, nullable=True)
    refund_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    payment_intent = relationship("PaymentIntent", foreign_keys=[payment_intent_id])
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_refund_requests_payment_status_created", "payment_intent_id", "status", "created_at"),
        Index("ix_refund_requests_user_status_created", "user_id", "status", "created_at"),
    )


class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_currency = Column(String(10), nullable=False, default="ACP")
    amount_value = Column(Numeric(36, 18), nullable=False)
    status = Column(SQLEnum(PayoutRequestStatusEnum), nullable=False, default=PayoutRequestStatusEnum.pending, index=True)
    method = Column(String(32), nullable=False)
    destination = Column(String(255), nullable=False)
    request_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    approval_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    rejection_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_payout_requests_user_status_created", "user_id", "status", "created_at"),
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id = Column(UUID(as_uuid=False), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String(64), nullable=True)
    status = Column(
        SQLEnum(SubscriptionStatusEnum),
        nullable=False,
        default=SubscriptionStatusEnum.active,
        index=True,
    )
    billing_period = Column(
        SQLEnum(SubscriptionBillingPeriodEnum),
        nullable=False,
        default=SubscriptionBillingPeriodEnum.monthly,
    )
    price_acp = Column(Numeric(36, 18), nullable=False)
    next_billing_at = Column(DateTime(timezone=True), nullable=True, index=True)
    auto_renew = Column(Boolean, nullable=False, default=True)
    retry_count = Column(Integer, nullable=False, default=0)
    last_order_id = Column(UUID(as_uuid=False), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    listing = relationship("Listing", foreign_keys=[listing_id])
    last_order = relationship("Order", foreign_keys=[last_order_id])

    __table_args__ = (
        Index("ix_subscriptions_user_status_created", "user_id", "status", "created_at"),
        Index("ux_subscriptions_user_listing_period_active", "user_id", "listing_id", "billing_period", unique=True),
    )


class LlmUsageEvent(Base):
    __tablename__ = "llm_usage_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workflow_run_id = Column(UUID(as_uuid=False), ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(40), nullable=False, index=True)
    model = Column(String(120), nullable=False)
    prompt_hash = Column(String(64), nullable=False, index=True)
    input_tokens_estimate = Column(Integer, nullable=False, default=0)
    output_tokens_estimate = Column(Integer, nullable=False, default=0)
    latency_ms = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, index=True)
    error = Column(String(1000), nullable=True)
    provider_status = Column(String(32), nullable=False, server_default="unknown")  # unknown | ok | degraded | failed
    failure_reason = Column(String(128), nullable=True)  # unavailable | invalid_model | auth_error | balance_error | timeout | unknown
    retry_count = Column(Integer, nullable=False, server_default="0")
    cost_currency = Column(String(10), nullable=False, default="ACP")
    cost_amount = Column(Numeric(36, 18), nullable=False, default=0)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    owner_user = relationship("User", foreign_keys=[owner_user_id])
    workflow_run = relationship("WorkflowRunRecord", foreign_keys=[workflow_run_id])

    __table_args__ = (
        Index("ix_llm_usage_events_run_created", "workflow_run_id", "created_at"),
        Index("ix_llm_usage_events_owner_created", "owner_user_id", "created_at"),
        Index("ix_llm_usage_events_provider_status", "provider", "status"),
        Index("ix_llm_usage_events_provider_status_idx", "provider_status"),
        Index("ix_llm_usage_events_failure_reason", "failure_reason"),
    )


class AccessGrant(Base):
    __tablename__ = "access_grants"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    grantee_type = Column(String(20), nullable=False)
    grantee_id = Column(UUID(as_uuid=False), nullable=False)
    scope = Column(SQLEnum(AccessScopeEnum), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# --- Pools / Capital ---
class Pool(Base):
    __tablename__ = "pools"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False, index=True)
    owner_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=True, index=True)
    risk_profile = Column(SQLEnum(RiskProfileEnum), nullable=False)
    status = Column(SQLEnum(PoolStatusEnum), default=PoolStatusEnum.active)
    rules = Column(JSONB, nullable=True)
    fee_model = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AccountKindEnum(str, enum.Enum):
    """System account kinds for unambiguous routing (ROADMAP §3)."""
    treasury = "treasury"
    external = "external"
    fees = "fees"
    escrow = "escrow"
    burn = "burn"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_type = Column(String(20), nullable=False)
    owner_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    account_kind = Column(String(20), nullable=True, index=True)  # treasury|fees|escrow|burn|external; null = participant
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_accounts_owner_type_id", "owner_type", "owner_id", unique=True),)


class LedgerEvent(Base):
    __tablename__ = "ledger_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    ts = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    type = Column(SQLEnum(LedgerEventTypeEnum), nullable=False)
    amount_currency = Column(String(10), nullable=False)
    amount_value = Column(Numeric(36, 18), nullable=False)
    src_account_id = Column(UUID(as_uuid=False), ForeignKey("accounts.id"), nullable=True)
    dst_account_id = Column(UUID(as_uuid=False), ForeignKey("accounts.id"), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)


class Share(Base):
    __tablename__ = "shares"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    pool_id = Column(UUID(as_uuid=False), ForeignKey("pools.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=False), nullable=False)
    share_balance = Column(Numeric(36, 18), default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Execution ---
class Run(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    strategy_version_id = Column(UUID(as_uuid=False), ForeignKey("strategy_versions.id"), nullable=False)
    pool_id = Column(UUID(as_uuid=False), ForeignKey("pools.id"), nullable=False)
    parent_run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True)
    contract_milestone_id = Column(UUID(as_uuid=False), ForeignKey("contract_milestones.id", ondelete="SET NULL"), nullable=True, index=True)
    state = Column(SQLEnum(RunStateEnum), default=RunStateEnum.queued)
    params = Column(JSONB, nullable=True)
    limits = Column(JSONB, nullable=True)
    dry_run = Column(Boolean, default=False)
    run_mode = Column(String(16), default="mock", nullable=False)  # mock | backtest (PLAN §5)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)
    inputs_hash = Column(Text, nullable=True)
    workflow_hash = Column(Text, nullable=True)
    outputs_hash = Column(Text, nullable=True)
    env_hash = Column(Text, nullable=True)  # L1 audit: hash of pool_id + limits
    proof_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    ts = Column(DateTime(timezone=True), default=datetime.utcnow)
    level = Column(String(16), nullable=False)
    message = Column(Text, nullable=False)


class RunStep(Base):
    """Execution DAG (ROADMAP §5): one step per workflow step; parent_step_index for DAG edges; step_score for step-level scoring."""
    __tablename__ = "run_steps"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_id = Column(String(128), nullable=False)
    parent_step_index = Column(Integer, nullable=True)
    action = Column(String(64), nullable=False)
    state = Column(String(32), nullable=False)  # succeeded, failed, skipped
    duration_ms = Column(Integer, nullable=True)
    result_summary = Column(JSONB, nullable=True)
    artifact_hash = Column(Text, nullable=True)
    score_value = Column(Numeric(10, 4), nullable=True)
    score_type = Column(String(32), nullable=True)
    context_after = Column(JSONB, nullable=True)  # ROADMAP §5: context after step for replay from step N
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class RunStepScore(Base):
    """ROADMAP §5: alternative score_type (latency, quality) per step; one row per (run_step_id, score_type)."""
    __tablename__ = "run_step_scores"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    run_step_id = Column(UUID(as_uuid=False), ForeignKey("run_steps.id", ondelete="CASCADE"), nullable=False)
    score_type = Column(String(32), nullable=False)
    score_value = Column(Numeric(10, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# --- Metrics ---
class MetricRecord(Base):
    __tablename__ = "metrics"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(64), nullable=False, index=True)
    value = Column(JSONB, nullable=False)  # number, string, or object
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    strategy_version_id = Column(UUID(as_uuid=False), ForeignKey("strategy_versions.id", ondelete="CASCADE"), nullable=False)
    score = Column(Numeric(5, 4), nullable=False)  # 0..1
    confidence = Column(Numeric(5, 4), nullable=False)
    sample_size = Column(Integer, default=0)
    percentile_in_vertical = Column(Numeric(5, 4), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Risk (optional for MVP) ---
class RiskPolicy(Base):
    __tablename__ = "risk_policies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    scope_type = Column(String(32), nullable=False)
    scope_id = Column(UUID(as_uuid=False), nullable=False)
    policy_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class CircuitBreaker(Base):
    __tablename__ = "circuit_breakers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    scope_type = Column(String(32), nullable=False)
    scope_id = Column(UUID(as_uuid=False), nullable=False)
    state = Column(String(32), default="normal")  # normal, limited, halted
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# --- Reputation 2.0 enums (stored as string in DB) ---
class ReputationEventTypeEnum(str, enum.Enum):
    order_fulfilled = "order_fulfilled"
    order_refunded = "order_refunded"
    access_granted = "access_granted"
    run_completed = "run_completed"
    evaluation_scored = "evaluation_scored"
    contract_accepted = "contract_accepted"
    contract_completed = "contract_completed"
    contract_cancelled = "contract_cancelled"
    audit_passed = "audit_passed"
    audit_failed = "audit_failed"
    moderation_penalty = "moderation_penalty"
    moderation_clear = "moderation_clear"


class EdgeTypeEnum(str, enum.Enum):
    order = "order"
    grant = "grant"
    run_for = "run_for"
    review = "review"
    ledger_transfer = "ledger_transfer"


# --- Reputation (simplified, legacy) ---
class Reputation(Base):
    __tablename__ = "reputations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    subject_type = Column(String(32), nullable=False)
    subject_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    score = Column(Numeric(5, 4), default=0)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("ix_reputations_subject", "subject_type", "subject_id", unique=True),)


# --- Reputation 2.0 (event sourcing + trust + snapshots) ---
class ReputationEvent(Base):
    __tablename__ = "reputation_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    subject_type = Column(String(32), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    actor_type = Column(String(32), nullable=True)
    actor_id = Column(UUID(as_uuid=False), nullable=True)
    event_type = Column(String(64), nullable=False, index=True)
    value = Column(Numeric(12, 6), nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_reputation_events_subject_created", "subject_type", "subject_id", "created_at"),)


class RelationshipEdgeDaily(Base):
    __tablename__ = "relationship_edges_daily"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    day = Column(Date, nullable=False, index=True)
    src_type = Column(String(32), nullable=False)
    src_id = Column(UUID(as_uuid=False), nullable=False)
    dst_type = Column(String(32), nullable=False)
    dst_id = Column(UUID(as_uuid=False), nullable=False)
    edge_type = Column(String(32), nullable=False, index=True)
    count = Column(Integer, default=0)
    amount_sum = Column(Numeric(36, 18), nullable=True)
    unique_refs = Column(Integer, default=0)
    meta = Column(JSONB, nullable=True, server_default="{}")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_relationship_edges_daily_day_src_dst", "day", "src_type", "src_id", "dst_type", "dst_id", "edge_type", unique=True),
        Index("ix_edges_daily_src_day", "src_type", "src_id", "day"),
        Index("ix_edges_daily_dst_day", "dst_type", "dst_id", "day"),
        Index("ix_edges_daily_pair_day", "src_type", "src_id", "dst_type", "dst_id", "day"),
    )


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    subject_type = Column(String(32), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    trust_score = Column(Numeric(5, 4), nullable=False)
    components = Column(JSONB, nullable=True)
    window = Column(String(16), nullable=False)
    algo_version = Column(String(32), nullable=False)
    inputs_hash = Column(String(64), nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("uq_trust_scores_subject_window_algo", "subject_type", "subject_id", "window", "algo_version", unique=True),
    )


class ReputationSnapshot(Base):
    __tablename__ = "reputation_snapshots"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    subject_type = Column(String(32), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    score = Column(Numeric(8, 4), nullable=False)
    components = Column(JSONB, nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=False)
    algo_version = Column(String(32), nullable=False)
    window = Column(String(16), nullable=False)
    inputs_hash = Column(Text, nullable=True)
    proof = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("uq_rep_snapshots_subject_window_algo", "subject_type", "subject_id", "window", "algo_version", unique=True),
    )


# --- Jobs (watermarks for incremental aggregation) ---
class JobWatermark(Base):
    __tablename__ = "job_watermarks"

    key = Column(String(64), primary_key=True)
    value = Column(String(512), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemJobRun(Base):
    __tablename__ = "system_job_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    job_name = Column(String(64), nullable=False, index=True)
    trigger_source = Column(String(32), nullable=False, default="api")
    status = Column(String(16), nullable=False, default="queued", index=True)  # queued|running|retry|succeeded|dead_letter
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    payload_json = Column(JSONB, nullable=False, default=dict)
    result_json = Column(JSONB, nullable=True)
    last_error = Column(Text, nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_system_job_runs_job_status_created", "job_name", "status", "created_at"),
        Index("ix_system_job_runs_job_retry", "job_name", "status", "next_retry_at"),
    )


class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    decision = Column(String(32), nullable=False, index=True)  # allow | reject
    reason_code = Column(String(64), nullable=False, index=True)
    message = Column(Text, nullable=True)
    scope = Column(String(64), nullable=False, index=True)  # runs.create | listings.create | orders.place
    actor_type = Column(String(32), nullable=True, index=True)  # user | agent | system
    actor_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    subject_type = Column(String(32), nullable=True, index=True)  # agent | strategy | listing | pool
    subject_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    threshold_value = Column(String(64), nullable=True)
    actual_value = Column(String(64), nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

# --- L2: Reviews ---
class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    reviewer_type = Column(String(20), nullable=False)  # agent, user, ai
    reviewer_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    target_type = Column(String(32), nullable=False, index=True)  # agent, strategy, listing, service, partner, literary_lot
    target_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    weight = Column(Numeric(5, 4), nullable=False, default=1)  # 0..1 for weighted reputation
    rating = Column(Integer, nullable=True)  # optional 1..5 stars for service reviews
    text = Column(Text, nullable=True)
    run_id = Column(UUID(as_uuid=False), ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_reviews_target", "target_type", "target_id"),)


# --- L2: Disputes ---
class DisputeStatusEnum(str, enum.Enum):
    open = "open"
    resolved = "resolved"
    rejected = "rejected"


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    subject = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open", index=True)
    evidence_refs = Column(JSONB, nullable=True)  # list of {type, id} refs
    verdict = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class GovernanceProposal(Base):
    __tablename__ = "governance_proposals"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    kind = Column(String(32), nullable=False, index=True)  # policy_update | vertical_update | moderation_rule
    target_type = Column(String(32), nullable=False, index=True)  # policy | vertical | system
    target_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    payload_json = Column(JSONB, nullable=False)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft|review|active|rejected|appealed
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_reason = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class GovernanceVote(Base):
    __tablename__ = "governance_votes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=False), ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False, index=True)
    voter_type = Column(String(20), nullable=False, default="user")  # user | agent
    voter_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    vote_weight = Column(Numeric(12, 6), nullable=False, default=1)
    vote = Column(String(16), nullable=False)  # approve | reject | abstain
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("uq_governance_vote_unique_voter", "proposal_id", "voter_type", "voter_id", unique=True),
    )


class GovernanceAuditLog(Base):
    __tablename__ = "governance_audit_log"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=False), ForeignKey("governance_proposals.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(48), nullable=False, index=True)
    actor_type = Column(String(20), nullable=False, default="user")
    actor_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    event_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ModerationCase(Base):
    __tablename__ = "moderation_cases"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    subject_type = Column(String(32), nullable=False, index=True)  # agent | strategy | listing | vertical | policy
    subject_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    reason_code = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="open", index=True)  # open|resolved|appealed|rejected
    opened_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    resolved_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class IdempotencyKey(Base):
    """Idempotency store for POST endpoints (orders, runs)."""

    __tablename__ = "idempotency_keys"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    scope = Column(String(64), nullable=False)
    key = Column(String(128), nullable=False)
    request_hash = Column(String(64), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("uq_idempotency_scope_key", "scope", "key", unique=True),
        Index("ix_idempotency_scope", "scope"),
    )

# --- L2: Funds (portfolio-of-strategies) ---
class Fund(Base):
    __tablename__ = "funds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False, index=True)
    owner_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    pool_id = Column(UUID(as_uuid=False), ForeignKey("pools.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class FundAllocation(Base):
    __tablename__ = "fund_allocations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    fund_id = Column(UUID(as_uuid=False), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_version_id = Column(UUID(as_uuid=False), ForeignKey("strategy_versions.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Numeric(5, 4), nullable=False)  # 0..1 share of fund
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_fund_allocations_fund", "fund_id"),)


# --- L3: Proof-of-Agent ---
class AgentChallenge(Base):
    __tablename__ = "agent_challenges"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    challenge_type = Column(String(32), nullable=False, index=True)  # e.g. reasoning, tool_use
    payload_json = Column(JSONB, nullable=False)
    nonce = Column(String(64), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AgentAttestation(Base):
    __tablename__ = "agent_attestations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=False), ForeignKey("agent_challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    solution_hash = Column(String(64), nullable=False)
    attestation_sig = Column(Text, nullable=True)  # signature by agent key
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# --- L3: Stakes & Slashing ---
class StakeStatusEnum(str, enum.Enum):
    active = "active"
    released = "released"
    slashed = "slashed"


class Stake(Base):
    __tablename__ = "stakes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_currency = Column(String(10), nullable=False)
    amount_value = Column(Numeric(36, 18), nullable=False)
    status = Column(SQLEnum(StakeStatusEnum), default=StakeStatusEnum.active)
    slash_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    released_at = Column(DateTime(timezone=True), nullable=True)


# --- L3: On-chain anchoring ---
class ChainAnchor(Base):
    __tablename__ = "chain_anchors"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    chain_id = Column(String(32), nullable=False, index=True)  # e.g. ethereum, solana, mock
    tx_hash = Column(String(128), nullable=True, index=True)
    payload_type = Column(String(32), nullable=False, index=True)  # stake, slash, settlement, run_anchor
    payload_hash = Column(String(64), nullable=False)
    payload_json = Column(JSONB, nullable=True)
    anchored_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class SettlementIntentStatusEnum(str, enum.Enum):
    pending = "pending"
    executed = "executed"
    failed = "failed"


class ChainReceiptStatusEnum(str, enum.Enum):
    submitted = "submitted"
    finalized = "finalized"
    failed = "failed"


class SettlementIntent(Base):
    __tablename__ = "settlement_intents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    intent_type = Column(String(32), nullable=False, index=True)  # escrow_open|escrow_release|stake_lock|stake_unlock|slash
    source_owner_type = Column(String(32), nullable=False)
    source_owner_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    target_owner_type = Column(String(32), nullable=False)
    target_owner_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    amount_currency = Column(String(10), nullable=False, index=True)
    amount_value = Column(Numeric(36, 18), nullable=False)
    status = Column(String(24), nullable=False, default=SettlementIntentStatusEnum.pending.value, index=True)
    correlation_id = Column(String(128), nullable=False, index=True)
    metadata_json = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("uq_settlement_intents_correlation_id", "correlation_id", unique=True),
    )


class ChainReceipt(Base):
    __tablename__ = "chain_receipts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    settlement_intent_id = Column(
        UUID(as_uuid=False), ForeignKey("settlement_intents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chain_id = Column(String(32), nullable=False, index=True)
    tx_hash = Column(String(128), nullable=True, index=True)
    node_signature = Column(Text, nullable=True)
    node_public_key = Column(Text, nullable=True)
    status = Column(String(24), nullable=False, default=ChainReceiptStatusEnum.submitted.value, index=True)
    correlation_id = Column(String(128), nullable=False, index=True)
    payload_hash = Column(String(64), nullable=False)
    receipt_json = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ContractStatusEnum(str, enum.Enum):
    draft = "draft"
    proposed = "proposed"
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"
    disputed = "disputed"


class PaymentModelEnum(str, enum.Enum):
    fixed = "fixed"
    per_run = "per_run"


class ContractMilestoneStatusEnum(str, enum.Enum):
    pending = "pending"
    active = "active"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    paid = "paid"
    cancelled = "cancelled"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    employer_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    scope_type = Column(String(32), nullable=False)
    scope_ref_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ContractStatusEnum), default=ContractStatusEnum.draft)
    payment_model = Column(SQLEnum(PaymentModelEnum), nullable=False)
    fixed_amount_value = Column(Numeric(36, 18), nullable=True)
    currency = Column(String(10), nullable=False, default="ACP")
    max_runs = Column(Integer, nullable=True)
    runs_completed = Column(Integer, nullable=False, default=0)
    risk_policy_id = Column(UUID(as_uuid=False), ForeignKey("risk_policies.id", ondelete="SET NULL"), nullable=True)
    created_from_order_id = Column(UUID(as_uuid=False), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ContractMilestone(Base):
    __tablename__ = "contract_milestones"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(ContractMilestoneStatusEnum), nullable=False, default=ContractMilestoneStatusEnum.pending, index=True)

    amount_value = Column(Numeric(36, 18), nullable=False)
    currency = Column(String(10), nullable=False, default="ACP")

    required_runs = Column(Integer, nullable=True)
    completed_runs = Column(Integer, nullable=False, default=0)

    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_contract_milestones_contract_order", "contract_id", "order_index"),
        Index("ix_contract_milestones_contract_status", "contract_id", "status"),
        Index("ix_contract_milestones_contract_created", "contract_id", "created_at"),
    )


# --- Sprint-3 Growth Layer ---

class ReferralAttributionStatusEnum(str, enum.Enum):
    pending = "pending"
    eligible = "eligible"
    rewarded = "rewarded"
    rejected = "rejected"


class FaucetClaimStatusEnum(str, enum.Enum):
    granted = "granted"
    held = "held"
    rejected = "rejected"
    clawed_back = "clawed_back"


class StarterPackAssignmentStatusEnum(str, enum.Enum):
    assigned = "assigned"
    activated = "activated"
    cancelled = "cancelled"


class StrategyCopyModeEnum(str, enum.Enum):
    fork = "fork"
    mirror_template = "mirror_template"


class NotificationPriorityEnum(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"


class TaskFeedStatusEnum(str, enum.Enum):
    open = "open"
    claimed = "claimed"
    completed = "completed"
    expired = "expired"


class FeedVisibilityEnum(str, enum.Enum):
    public = "public"
    unlisted = "unlisted"
    private = "private"


class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    code = Column(String(64), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    reward_bps = Column(Integer, nullable=False, default=500)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_referral_codes_owner_user", "owner_user_id"),
        Index("ix_referral_codes_owner_agent", "owner_agent_id"),
    )


class ReferralAttribution(Base):
    __tablename__ = "referral_attributions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    referral_code_id = Column(UUID(as_uuid=False), ForeignKey("referral_codes.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    referred_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    attributed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    source = Column(String(32), nullable=False, default="signup")
    status = Column(String(32), nullable=False, default=ReferralAttributionStatusEnum.pending.value)


class ReferralRewardEvent(Base):
    __tablename__ = "referral_reward_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    referral_attribution_id = Column(UUID(as_uuid=False), ForeignKey("referral_attributions.id", ondelete="CASCADE"), nullable=False, index=True)
    beneficiary_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    beneficiary_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    trigger_type = Column(String(32), nullable=False)
    trigger_ref_type = Column(String(32), nullable=False)
    trigger_ref_id = Column(UUID(as_uuid=False), nullable=False)
    currency = Column(String(16), nullable=False)
    amount_value = Column(Numeric(38, 18), nullable=False)
    ledger_tx_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ref_reward_benef_user", "beneficiary_user_id"),
        Index("ix_ref_reward_benef_agent", "beneficiary_agent_id"),
        Index("ux_ref_reward_dedupe", "referral_attribution_id", "trigger_type", "trigger_ref_type", "trigger_ref_id", unique=True),
    )


class ReferralOnchainPayoutJob(Base):
    __tablename__ = "referral_onchain_payout_jobs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    reward_event_id = Column(
        UUID(as_uuid=False),
        ForeignKey("referral_reward_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_address = Column(String(128), nullable=False)
    amount_value = Column(Numeric(38, 18), nullable=False)
    status = Column(String(32), nullable=False, default="pending", index=True)  # pending|sent|failed
    attempts = Column(Integer, nullable=False, default=0)
    txid = Column(String(128), nullable=True, index=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_ref_payout_status_created", "status", "created_at"),
        Index("ux_ref_payout_reward_event", "reward_event_id", unique=True),
    )


class AcpSwapOrder(Base):
    __tablename__ = "acp_swap_orders"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="awaiting_deposit", index=True)
    usdt_trc20_amount = Column(Numeric(38, 18), nullable=False)
    rate_acp_per_usdt = Column(Numeric(38, 18), nullable=False)
    estimated_acp_amount = Column(Numeric(38, 18), nullable=False)
    payout_acp_address = Column(String(128), nullable=False)
    deposit_trc20_address = Column(String(128), nullable=False)
    deposit_reference = Column(String(64), nullable=False, unique=True, index=True)
    tron_txid = Column(String(256), nullable=True, index=True)
    payout_txid = Column(String(128), nullable=True, index=True)
    note = Column(Text, nullable=True)
    idempotency_key = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_swap_orders_user_created", "user_id", "created_at"),
        Index("ux_swap_user_idempotency", "user_id", "idempotency_key", unique=True),
    )


class AcpOtcIntakeOrder(Base):
    """Precious metals / goods OTC intake → ACP after desk review."""

    __tablename__ = "acp_otc_intake_orders"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rail = Column(String(32), nullable=False, index=True)  # metal | goods | commodity | real_estate | space | ip
    status = Column(String(32), nullable=False, default="awaiting_handoff", index=True)
    asset_label = Column(String(200), nullable=False)
    asset_detail = Column(JSONB, nullable=False, default=dict)
    estimated_acp_amount = Column(Numeric(38, 18), nullable=False)
    payout_acp_address = Column(String(128), nullable=False)
    intake_reference = Column(String(64), nullable=False, unique=True, index=True)
    proof_ref = Column(String(256), nullable=True)
    note = Column(Text, nullable=True)
    idempotency_key = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_otc_intake_user_created", "user_id", "created_at"),
        Index("ux_otc_intake_user_idempotency", "user_id", "idempotency_key", unique=True),
    )


class AcpExchangeTicket(Base):
    """Mobile exchange-office umbrella ticket (ACP-hub multi-asset).

    May reference an underlying rail order (swap desk / OTC / bridge) via rail_ref_*.
    """

    __tablename__ = "acp_exchange_tickets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="opened", index=True)
    from_asset = Column(String(64), nullable=False, index=True)
    to_asset = Column(String(64), nullable=False, index=True)
    from_amount = Column(Numeric(38, 18), nullable=False)
    to_amount_estimated = Column(Numeric(38, 18), nullable=False)
    acp_hub_amount = Column(Numeric(38, 18), nullable=False)
    rail = Column(String(32), nullable=False, index=True)
    rail_ref_type = Column(String(32), nullable=True)
    rail_ref_id = Column(String(64), nullable=True, index=True)
    quote_id = Column(String(64), nullable=False, index=True)
    quote_snapshot = Column(JSONB, nullable=False, default=dict)
    payout_acp_address = Column(String(128), nullable=True)
    counterparty_address = Column(String(256), nullable=True)
    intake_reference = Column(String(64), nullable=True, unique=True, index=True)
    handoff_instructions = Column(Text, nullable=True)
    next_step = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    idempotency_key = Column(String(128), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_exchange_tickets_user_created", "user_id", "created_at"),
        Index("ux_exchange_tickets_user_idempotency", "user_id", "idempotency_key", unique=True),
    )



class AcpOwnershipCertificate(Base):
    """ACP crypto-style ownership contract for intangible / title-linked assets."""

    __tablename__ = "acp_ownership_certificates"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_code = Column(String(32), nullable=False, unique=True, index=True)
    asset_class = Column(String(64), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    subject_uri = Column(String(512), nullable=True)
    jurisdiction = Column(String(64), nullable=True)
    document_hash = Column(String(128), nullable=False)
    document_uri = Column(String(512), nullable=True)
    face_value_acp = Column(Numeric(38, 18), nullable=True)
    status = Column(String(32), nullable=False, default="issued", index=True)
    transfer_code_hash = Column(String(64), nullable=True, index=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    issued_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_ownership_owner_created", "owner_user_id", "created_at"),
    )


class FaucetClaim(Base):
    __tablename__ = "faucet_claims"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    currency = Column(String(16), nullable=False)
    amount_value = Column(Numeric(38, 18), nullable=False)
    claim_status = Column(String(32), nullable=False, default=FaucetClaimStatusEnum.granted.value)
    risk_flags = Column(JSONB, nullable=False, default=dict)
    ledger_tx_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class RegistrationSignal(Base):
    """Hashed IP/device signals for free-ACP anti-sybil quarantine."""

    __tablename__ = "registration_signals"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_hash = Column(String(64), nullable=False, index=True)
    device_hash = Column(String(64), nullable=True, index=True)
    free_grants_allowed = Column(Boolean, nullable=False, default=True)
    risk_flags = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_registration_signals_ip_created", "ip_hash", "created_at"),
        Index("ix_registration_signals_device_created", "device_hash", "created_at"),
    )


class ServerInstallBounty(Base):
    """Crypto payout requests for verified server installations."""

    __tablename__ = "server_install_bounties"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    host_label = Column(String(128), nullable=False)
    proof_url = Column(Text, nullable=True)
    proof_note = Column(Text, nullable=True)
    payout_address = Column(String(128), nullable=False)
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    risk_flags = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RobotTelemetryConsent(Base):
    """Opt-in consent for shipping sold/rented robot telemetry to ANCAP servers."""

    __tablename__ = "robot_telemetry_consents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    robot_id = Column(String(128), nullable=False, index=True)
    consent_active = Column(Boolean, nullable=False, default=True)
    retention_days = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)


class RobotTelemetryEvent(Base):
    __tablename__ = "robot_telemetry_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    consent_id = Column(
        UUID(as_uuid=False), ForeignKey("robot_telemetry_consents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    robot_id = Column(String(128), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class RobotDeliveryJob(Base):
    """Uber-like food / courier jobs for delivery robots and cyborg agents."""

    __tablename__ = "robot_delivery_jobs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    customer_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    robot_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    pickup_label = Column(String(255), nullable=False)
    dropoff_label = Column(String(255), nullable=False)
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(32), nullable=False, default="open")
    delivery_proof = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class StarterPack(Base):
    __tablename__ = "starter_packs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(128), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    config_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class StarterPackAssignment(Base):
    __tablename__ = "starter_pack_assignments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    starter_pack_id = Column(UUID(as_uuid=False), ForeignKey("starter_packs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default=StarterPackAssignmentStatusEnum.assigned.value)


class StrategyFollow(Base):
    __tablename__ = "strategy_follows"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    follower_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    follower_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)


class StrategyCopy(Base):
    __tablename__ = "strategy_copies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    source_strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    copied_strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    copier_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    copier_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    copy_mode = Column(String(32), nullable=False, default=StrategyCopyModeEnum.fork.value)


class StrategyMutation(Base):
    __tablename__ = "strategy_mutations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    parent_strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    child_strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="SET NULL"), nullable=True, index=True)
    mutation_type = Column(String(32), nullable=False, index=True)  # add_step | change_param | crossover
    diff_spec = Column(JSONB, nullable=False, default=dict)
    evaluation_score = Column(Numeric(12, 6), nullable=True)
    status = Column(String(32), nullable=False, default="proposed", index=True)  # proposed|evaluating|accepted|rejected
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(160), nullable=False)
    status = Column(String(32), nullable=False, default="scheduled", index=True)  # scheduled|running|completed
    scoring_metric = Column(String(64), nullable=False, default="evaluation_score")
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class TournamentEntry(Base):
    __tablename__ = "tournament_entries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=False), ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_id = Column(UUID(as_uuid=False), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    score = Column(Numeric(12, 6), nullable=False, default=0)
    rank = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("uq_tournament_strategy", "tournament_id", "strategy_id", unique=True),
    )


class BugBountyReport(Base):
    __tablename__ = "bug_bounty_reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    reporter_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reporter_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(24), nullable=False, default="medium", index=True)  # low|medium|high|critical
    status = Column(String(32), nullable=False, default="submitted", index=True)  # submitted|validated|rejected|rewarded
    reward_currency = Column(String(16), nullable=True)
    reward_amount = Column(Numeric(38, 18), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentFollow(Base):
    __tablename__ = "agent_follows"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    target_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    follower_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    follower_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)


class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    recipient_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    recipient_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(String(64), nullable=False)
    priority = Column(String(16), nullable=False, default=NotificationPriorityEnum.normal.value)
    payload_json = Column(JSONB, nullable=False, default=dict)
    dedupe_key = Column(String(255), nullable=True, unique=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)


class PublicActivityFeedEvent(Base):
    __tablename__ = "public_activity_feed"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    actor_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    ref_type = Column(String(32), nullable=False)
    ref_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    visibility = Column(String(16), nullable=False, default=FeedVisibilityEnum.public.value, index=True)
    score = Column(Numeric(18, 6), nullable=False, default=0)
    payload_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_public_feed_score_created", "score", "created_at"),
        Index("ix_public_feed_actor_agent_created", "actor_agent_id", "created_at"),
    )


class SocialPost(Base):
    """Nexus social network posts — humans and agents share one timeline."""

    __tablename__ = "social_posts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    author_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    author_agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    parent_id = Column(UUID(as_uuid=False), ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=True, index=True)
    body = Column(Text, nullable=False)
    actor_kind = Column(String(16), nullable=False, default="user")  # user | agent
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_social_posts_created_alive", "created_at", "is_deleted"),
    )


class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    board_type = Column(String(32), nullable=False, index=True)
    subject_type = Column(String(32), nullable=False)
    subject_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    window = Column(String(16), nullable=False, index=True)
    rank = Column(Integer, nullable=False)
    score = Column(Numeric(18, 6), nullable=False)
    components_json = Column(JSONB, nullable=False, default=dict)
    snapshot_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ux_leaderboard_unique", "board_type", "subject_type", "subject_id", "window", "snapshot_date", unique=True),
        Index("ix_leaderboard_lookup", "board_type", "window", "snapshot_date", "rank"),
    )


class GrowthMetricRollup(Base):
    __tablename__ = "growth_metric_rollups"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    metric_date = Column(Date, nullable=False, index=True)
    metric_key = Column(String(64), nullable=False, index=True)
    metric_value = Column(Numeric(38, 10), nullable=False)
    dimensions_json = Column(JSONB, nullable=False, default=dict)
    dimensions_hash = Column(String(32), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ux_growth_metric_unique", "metric_date", "metric_key", "dimensions_hash", unique=True),
        Index("ix_growth_metric_key_date", "metric_key", "metric_date"),
    )


class TaskFeedItem(Base):
    __tablename__ = "task_feed_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(32), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    task_type = Column(String(32), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reward_currency = Column(String(16), nullable=True)
    reward_amount_value = Column(Numeric(38, 18), nullable=True)
    target_agent_type = Column(String(64), nullable=True)
    target_vertical = Column(String(64), nullable=True, index=True)
    eligibility_json = Column(JSONB, nullable=False, default=dict)
    score = Column(Numeric(18, 6), nullable=False, default=0)
    status = Column(String(16), nullable=False, default=TaskFeedStatusEnum.open.value, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_task_feed_open_score", "status", "score", "created_at"),
        Index("ix_task_feed_vertical", "target_vertical", "status", "score"),
    )


class BridgeWatcherCheckpoint(Base):
    __tablename__ = "bridge_watcher_checkpoints"

    chain_key = Column(String(32), primary_key=True)
    last_block_height = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class BridgeAllowlistAddress(Base):
    __tablename__ = "bridge_allowlist_addresses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    bsc_address = Column(String(66), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_bridge_allowlist_bsc", "bsc_address", unique=True),)


class BridgeOperation(Base):
    __tablename__ = "bridge_operations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    direction = Column(String(16), nullable=False)
    status = Column(String(40), nullable=False)
    user_bsc_address = Column(String(66), nullable=True)
    user_acp_address = Column(String(128), nullable=True)
    amount_acp_smallest = Column(Numeric(38, 0), nullable=False)
    amount_wacp_wei = Column(Numeric(38, 0), nullable=False)
    remainder_wacp_wei = Column(Numeric(38, 0), nullable=False, default=0)
    acp_chain_id = Column(String(32), nullable=False, default="acp")
    acp_tx_hash = Column(String(128), nullable=True)
    acp_out_index = Column(Integer, nullable=False, default=0)
    bsc_tx_hash_mint = Column(String(128), nullable=True)
    bsc_tx_hash_burn = Column(String(128), nullable=True)
    bsc_log_index = Column(Integer, nullable=True)
    bsc_chain_id = Column(String(32), nullable=False, default="bsc")
    deposit_ref_hex = Column(String(66), nullable=True)
    correlation_id = Column(String(128), nullable=True)
    version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_bridge_ops_status", "status"),
        Index("ix_bridge_ops_user", "user_id"),
        Index("ix_bridge_ops_created", "created_at"),
        Index(
            "ux_bridge_ops_acp_tx",
            "acp_chain_id",
            "acp_tx_hash",
            "acp_out_index",
            unique=True,
            postgresql_where=text("acp_tx_hash IS NOT NULL"),
        ),
        Index(
            "ux_bridge_ops_bsc_burn_tx",
            "bsc_chain_id",
            "bsc_tx_hash_burn",
            unique=True,
            postgresql_where=text("bsc_tx_hash_burn IS NOT NULL"),
        ),
    )


class BridgeStateTransition(Base):
    __tablename__ = "bridge_state_transitions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    operation_id = Column(UUID(as_uuid=False), ForeignKey("bridge_operations.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(String(40), nullable=True)
    to_status = Column(String(40), nullable=False)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (Index("ix_bridge_transitions_op", "operation_id"),)


class BridgeAuditEvent(Base):
    __tablename__ = "bridge_audit_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    operation_id = Column(UUID(as_uuid=False), ForeignKey("bridge_operations.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_bridge_audit_op", "operation_id"),
        Index("ix_bridge_audit_type_time", "event_type", "created_at"),
    )


class BridgeReserveSnapshot(Base):
    """Point-in-time snapshot of reserve health for the wACP bridge.

    Written by the bridge reconciliation job. Used for stale-data detection,
    operator mismatch alerting, and historical backing-ratio records.
    """
    __tablename__ = "bridge_reserve_snapshots"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    snapshot_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    reserve_balance_acp_smallest = Column(BigInteger, nullable=False, default=0)
    total_wacp_wei_completed = Column(Numeric(38, 0), nullable=False, default=0)
    total_wacp_wei_implied = Column(Numeric(38, 0), nullable=False, default=0)
    backing_ratio = Column(Numeric(12, 6), nullable=True)
    delta_wacp_wei = Column(Numeric(38, 0), nullable=False, default=0)
    reconciliation_ok = Column(Boolean, nullable=False, default=True)
    acp_reserve_address = Column(String(128), nullable=True)
    wacp_contract = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    reserve_health = Column(String(32), nullable=False, default="pending")
    notes = Column(JSONB, nullable=False, default=list)
    last_acp_block_height = Column(BigInteger, nullable=True)
    last_bsc_block_number = Column(BigInteger, nullable=True)

    __table_args__ = (
        Index("ix_bridge_snapshots_time", "snapshot_at"),
    )


class SacpOperation(Base):
    """sACP mint/redeem intents (USD-targeted stablecoin rail).

    Foundation FSM — operator settles on-chain mint/redeem after collateral proof.
    See docs/STABLECOIN_SACP_SPEC.md.
    """

    __tablename__ = "sacp_operations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    direction = Column(String(16), nullable=False)  # mint | redeem
    status = Column(String(40), nullable=False)
    user_bsc_address = Column(String(66), nullable=True)
    user_acp_address = Column(String(128), nullable=True)
    amount_acp_smallest = Column(Numeric(38, 0), nullable=False, default=0)
    amount_sacp_wei = Column(Numeric(38, 0), nullable=False, default=0)
    acp_per_usd = Column(Numeric(36, 18), nullable=False)
    min_collateral_ratio = Column(Numeric(12, 6), nullable=False)
    acp_tx_hash = Column(String(128), nullable=True)
    bsc_tx_hash = Column(String(128), nullable=True)
    collateral_ref_hex = Column(String(66), nullable=True)
    correlation_id = Column(String(128), nullable=True)
    notes = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_sacp_ops_status", "status"),
        Index("ix_sacp_ops_user", "user_id"),
        Index("ix_sacp_ops_created", "created_at"),
    )


class SacpReserveSnapshot(Base):
    """Point-in-time sACP collateral vs circulating supply."""

    __tablename__ = "sacp_reserve_snapshots"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    snapshot_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    reserve_balance_acp_smallest = Column(Numeric(38, 0), nullable=False, default=0)
    sacp_total_supply_wei = Column(Numeric(38, 0), nullable=False, default=0)
    implied_collateral_usd = Column(Numeric(36, 18), nullable=True)
    required_collateral_usd = Column(Numeric(36, 18), nullable=True)
    collateral_ratio = Column(Numeric(12, 6), nullable=True)
    reconciliation_ok = Column(Boolean, nullable=False, default=True)
    acp_reserve_address = Column(String(128), nullable=True)
    sacp_contract = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    reserve_health = Column(String(32), nullable=False, default="pending")
    notes = Column(JSONB, nullable=False, default=list)

    __table_args__ = (Index("ix_sacp_snapshots_time", "snapshot_at"),)


class OrgRoleEnum(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"


class MemberVerificationStatusEnum(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    suspended = "suspended"
    revoked = "revoked"


class WebhookEventType(str, enum.Enum):
    run_completed = "run.completed"
    run_failed = "run.failed"
    payment_captured = "payment.captured"
    payment_refunded = "payment.refunded"
    receipt_ready = "receipt.ready"
    api_usage_created = "api.usage.created"
    user_registered = "user.registered"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    slug = Column(String(80), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    billing_wallet_address = Column(String(128), nullable=True)
    billing_agent_id = Column(UUID(as_uuid=False), nullable=True)
    created_by_user_id = Column(UUID(as_uuid=False), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(
        SQLEnum(
            OrgRoleEnum,
            name="orgroleenum",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=OrgRoleEnum.member,
    )
    employee_code = Column(String(64), nullable=True)
    verification_status = Column(
        SQLEnum(
            MemberVerificationStatusEnum,
            name="memberverificationstatusenum",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=MemberVerificationStatusEnum.pending,
    )
    nfc_uid_hash = Column(String(128), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_org_member_unique", "org_id", "user_id", unique=True),
    )

    org = relationship("Organization", foreign_keys=[org_id])
    user = relationship("User", foreign_keys=[user_id])
    verified_by_user = relationship("User", foreign_keys=[verified_by_user_id])


class UserNfcCredential(Base):
    __tablename__ = "user_nfc_credentials"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(120), nullable=True)
    uid_hash = Column(String(128), nullable=False)
    vendor = Column(String(32), nullable=False, default="biohax")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_user_nfc_credentials_uid_hash", "uid_hash", unique=True),
    )


class DigitalPassportStatusEnum(str, enum.Enum):
    pending = "pending"
    active = "active"
    revoked = "revoked"


class DigitalPassport(Base):
    __tablename__ = "digital_passports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    wallet_address = Column(String(42), nullable=False, index=True)
    token_id = Column(BigInteger, nullable=False, unique=True, index=True)
    claim_hash = Column(String(66), nullable=False, index=True)
    chain_id = Column(String(32), nullable=False, default="bsc")
    contract_address = Column(String(42), nullable=True)
    tx_hash = Column(String(128), nullable=True, index=True)
    token_uri = Column(String(512), nullable=True)
    status = Column(
        SQLEnum(
            DigitalPassportStatusEnum,
            name="digitalpassportstatusenum",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=DigitalPassportStatusEnum.pending,
    )
    nfc_credential_id = Column(
        UUID(as_uuid=False),
        ForeignKey("user_nfc_credentials.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    issued_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    org = relationship("Organization", foreign_keys=[org_id])
    nfc_credential = relationship("UserNfcCredential", foreign_keys=[nfc_credential_id])
    education_docs = relationship(
        "DigitalPassportEducationDoc",
        back_populates="passport",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_digital_passports_user_org", "user_id", "org_id"),
    )


class DigitalPassportEducationDoc(Base):
    """Encrypted education credentials attached to a digital passport (ChaCha20-Poly1305 v2)."""

    __tablename__ = "digital_passport_education_docs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    passport_id = Column(
        UUID(as_uuid=False),
        ForeignKey("digital_passports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_type = Column(String(64), nullable=False, index=True)
    title_hint = Column(String(200), nullable=False)
    institution_hint = Column(String(200), nullable=True)
    cipher_id = Column(String(96), nullable=False)
    nonce_b64 = Column(Text, nullable=False)
    ciphertext_b64 = Column(Text, nullable=False)
    content_hash = Column(String(80), nullable=False, index=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    passport = relationship("DigitalPassport", back_populates="education_docs")
    owner = relationship("User", foreign_keys=[owner_user_id])


class DnaRnaBankEntry(Base):
    """Encrypted DNA/RNA bank vault (AES-256-GCM + HKDF-SHA384 v1). Never store full genomes."""

    __tablename__ = "dna_rna_bank_entries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    molecule = Column(String(16), nullable=False, index=True)
    entry_type = Column(String(64), nullable=False, index=True)
    title_hint = Column(String(200), nullable=False)
    species_hint = Column(String(120), nullable=True)
    cipher_id = Column(String(96), nullable=False)
    nonce_b64 = Column(Text, nullable=False)
    ciphertext_b64 = Column(Text, nullable=False)
    content_hash = Column(String(120), nullable=False, index=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])


class PerimeterCleanupJob(Base):
    """Encrypted perimeter cleanup job brief (AES-256-GCM Abrams Suite-B v1)."""

    __tablename__ = "perimeter_cleanup_jobs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id = Column(String(64), nullable=False, index=True)
    contamination = Column(String(32), nullable=False, index=True)
    site_label_hint = Column(String(200), nullable=False)
    status = Column(String(32), nullable=False, default="draft", index=True)
    cipher_id = Column(String(96), nullable=False)
    nonce_b64 = Column(Text, nullable=False)
    ciphertext_b64 = Column(Text, nullable=False)
    content_hash = Column(String(120), nullable=False, index=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])


class OrganizationNfcPolicy(Base):
    __tablename__ = "organization_nfc_policies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    require_nfc_for_admins = Column(Boolean, nullable=False, default=False)
    require_nfc_for_payments = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])


class StripeEvent(Base):
    __tablename__ = "stripe_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    stripe_event_id = Column(String(128), nullable=False, unique=True, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    processed = Column(Boolean, nullable=False, default=False)
    payload_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_stripe_events_type_processed", "event_type", "processed"),
    )


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    url = Column(String(500), nullable=False)
    secret = Column(String(64), nullable=False)
    event_types = Column(JSONB, nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_webhook_owner_active", "owner_user_id", "is_active"),
    )

    owner = relationship("User", foreign_keys=[owner_user_id])


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    webhook_endpoint_id = Column(UUID(as_uuid=False), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(JSONB, nullable=False)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    attempt = Column(Integer, nullable=False, default=1)
    status = Column(String(16), nullable=False, default="pending", index=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_webhook_delivery_endpoint_status", "webhook_endpoint_id", "status"),
        Index("ix_webhook_delivery_pending_retry", "status", "next_retry_at"),
    )

    webhook_endpoint = relationship("WebhookEndpoint", foreign_keys=[webhook_endpoint_id])

# ── Phase 6: Mobile ACP indexer (DB-backed tx history) ────────────────────────


class MobileAcpTx(Base):
    """DB-backed ACP transaction history for mobile wallet."""
    __tablename__ = "mobile_acp_txs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    address = Column(String(64), nullable=False, index=True)
    txid = Column(String(128), nullable=False, index=True)
    block_height = Column(Integer, nullable=True)
    block_time = Column(String(32), nullable=True)
    direction = Column(String(8), nullable=False)
    sent_units = Column(BigInteger, nullable=False, default=0)
    received_units = Column(BigInteger, nullable=False, default=0)
    net_units = Column(BigInteger, nullable=False, default=0)
    fee_units = Column(BigInteger, nullable=False, default=0)
    confirmations = Column(Integer, nullable=False, default=0)
    raw_tx_json = Column(JSONB, nullable=True)
    scanned_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_mobile_acp_txs_address_height", "address", "block_height"),
        Index("ix_mobile_acp_txs_address_created", "address", "scanned_at"),
        Index("uq_mobile_acp_txs_address_txid", "address", "txid", unique=True),
    )


class MobileAddressIndexerState(Base):
    """Watermark state for mobile ACP indexer tick."""
    __tablename__ = "mobile_address_indexer_state"

    id = Column(Integer, primary_key=True, default=1)
    last_scanned_height = Column(Integer, nullable=False, default=0)
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)
    indexed_addresses = Column(JSONB, nullable=False, default=list)
    watermark = Column(String(64), nullable=True)


class MobileDevice(Base):
    """Registered mobile devices for push notifications."""
    __tablename__ = "mobile_devices"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_token = Column(String(512), nullable=False, unique=True)
    platform = Column(String(16), nullable=False)
    app_version = Column(String(16), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class MerchantAccount(Base):
    """Merchant profile for ANCAP Pay (payment links, invoices)."""
    __tablename__ = "merchant_accounts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    display_name = Column(String(128), nullable=False, default="Merchant")
    plan_tier = Column(String(32), nullable=False, default="starter", index=True)
    fee_bps = Column(Integer, nullable=False, default=100)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_user = relationship("User", foreign_keys=[owner_user_id])


class PaymentLink(Base):
    __tablename__ = "payment_links"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    merchant_account_id = Column(UUID(as_uuid=False), ForeignKey("merchant_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(32), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount_currency = Column(String(10), nullable=False, default="ACP")
    amount_value = Column(Numeric(36, 18), nullable=False)
    status = Column(String(32), nullable=False, default="pending", index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    payment_intent_id = Column(UUID(as_uuid=False), ForeignKey("payment_intents.id", ondelete="SET NULL"), nullable=True)
    payer_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    merchant_account = relationship("MerchantAccount", foreign_keys=[merchant_account_id])
    owner_user = relationship("User", foreign_keys=[owner_user_id])
    payer_user = relationship("User", foreign_keys=[payer_user_id])

    __table_args__ = (
        Index("ix_payment_links_owner_created", "owner_user_id", "created_at"),
    )


class MerchantInvoice(Base):
    __tablename__ = "merchant_invoices"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    merchant_account_id = Column(UUID(as_uuid=False), ForeignKey("merchant_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_number = Column(String(64), nullable=False, index=True)
    customer_email = Column(String(255), nullable=True)
    line_items_json = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    amount_currency = Column(String(10), nullable=False, default="ACP")
    amount_value = Column(Numeric(36, 18), nullable=False)
    status = Column(String(32), nullable=False, default="draft", index=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    payment_link_id = Column(UUID(as_uuid=False), ForeignKey("payment_links.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    merchant_account = relationship("MerchantAccount", foreign_keys=[merchant_account_id])
    payment_link = relationship("PaymentLink", foreign_keys=[payment_link_id])

    __table_args__ = (
        Index("ix_merchant_invoices_owner_created", "owner_user_id", "created_at"),
    )


class ClaimCode(Base):
    __tablename__ = "claim_codes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    secret_hash = Column(String(128), nullable=False)
    code_hint = Column(String(8), nullable=False)
    amount_currency = Column(String(10), nullable=False, default="ACP")
    amount_value = Column(Numeric(36, 18), nullable=False)
    status = Column(String(32), nullable=False, default="active", index=True)
    max_redemptions = Column(Integer, nullable=False, default=1)
    redemption_count = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    campaign_label = Column(String(128), nullable=True)
    pin_hash = Column(String(128), nullable=True)
    lock_ledger_event_id = Column(UUID(as_uuid=False), ForeignKey("ledger_events.id", ondelete="SET NULL"), nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner_user = relationship("User", foreign_keys=[owner_user_id])

    __table_args__ = (
        Index("ix_claim_codes_owner_created", "owner_user_id", "created_at"),
    )


class MobileSmartPayRecord(Base):
    """Durable store for mobile Smart Pay objects (intents, quotes, executions, receipts).

    Payloads are serialized Pydantic response models; ownership/session token
    columns only apply to execution records.
    """
    __tablename__ = "mobile_smart_pay_records"

    id = Column(String(80), primary_key=True)  # pi_*/q_*/pe_*/spr_* identifiers
    kind = Column(String(20), nullable=False, index=True)  # intent | quote | execution | receipt
    owner_user_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    session_token = Column(String(128), nullable=True)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_mobile_smart_pay_records_owner_kind", "owner_user_id", "kind"),
    )


class RampWaitlistEntry(Base):
    __tablename__ = "ramp_waitlist_entries"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), nullable=False, index=True)
    interest = Column(String(64), nullable=False, default="stablecoin_topup", index=True)
    region = Column(String(64), nullable=True)
    notes = Column(String(500), nullable=True)
    status = Column(String(32), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


# --- R9 Securities intake ---


class SecurityInstrument(Base):
    __tablename__ = "securities_instruments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    instrument_type = Column(String(32), nullable=False, index=True)
    issuer_name = Column(String(200), nullable=False)
    jurisdiction = Column(String(64), nullable=False)
    face_amount = Column(Numeric(36, 18), nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    isin = Column(String(16), nullable=True)
    maturity_at = Column(DateTime(timezone=True), nullable=True)
    share_count = Column(Numeric(36, 18), nullable=True)
    document_hash = Column(String(128), nullable=True)
    document_uri = Column(String(512), nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])


class SecurityIntakeRequest(Base):
    __tablename__ = "securities_intake_requests"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    instrument_id = Column(
        UUID(as_uuid=False),
        ForeignKey("securities_instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(32), nullable=False, default="draft", index=True)
    submitted_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewer_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    instrument = relationship("SecurityInstrument", foreign_keys=[instrument_id])
    org = relationship("Organization", foreign_keys=[org_id])

    __table_args__ = (Index("ix_securities_intake_org_status", "org_id", "status"),)


class SecurityCustodyPosition(Base):
    __tablename__ = "securities_custody_positions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    instrument_id = Column(
        UUID(as_uuid=False),
        ForeignKey("securities_instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    intake_id = Column(
        UUID(as_uuid=False),
        ForeignKey("securities_intake_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location = Column(String(32), nullable=False, default="register_only")
    custodian_ref = Column(String(200), nullable=True)
    haircut_bps = Column(Integer, nullable=False, default=2500)
    collateral_credit_acp = Column(Numeric(36, 18), nullable=False, default=0)
    status = Column(String(32), nullable=False, default="active", index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])
    instrument = relationship("SecurityInstrument", foreign_keys=[instrument_id])
    intake = relationship("SecurityIntakeRequest", foreign_keys=[intake_id])


# --- R10 Apple Watch HR fleet ---


class WatchAsset(Base):
    __tablename__ = "watch_assets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    slot = Column(String(8), nullable=False)
    band_color = Column(String(40), nullable=False)
    serial_number = Column(String(120), nullable=False)
    status = Column(String(32), nullable=False, default="spare", index=True)
    battery_percent = Column(Integer, nullable=True)
    last_rotated_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])
    employee = relationship("User", foreign_keys=[employee_user_id])

    __table_args__ = (
        Index("ix_watch_assets_org_employee_slot", "org_id", "employee_user_id", "slot", unique=True),
        Index("ix_watch_assets_org_serial", "org_id", "serial_number", unique=True),
    )


class WatchRotationPolicy(Base):
    __tablename__ = "watch_rotation_policies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    enabled = Column(Boolean, nullable=False, default=True)
    rotation_interval_minutes = Column(Integer, nullable=False, default=240)
    min_soc_percent = Column(Integer, nullable=False, default=25)
    grace_minutes = Column(Integer, nullable=False, default=15)
    viewer_roles = Column(JSONB, nullable=False, server_default=text("'[\"owner\", \"admin\"]'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])


class WatchHeartRateSample(Base):
    __tablename__ = "watch_heart_rate_samples"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    watch_asset_id = Column(UUID(as_uuid=False), ForeignKey("watch_assets.id", ondelete="SET NULL"), nullable=True, index=True)
    bpm = Column(Integer, nullable=False)
    on_shift = Column(Boolean, nullable=False, default=True)
    source = Column(String(40), nullable=False, default="healthkit")
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])
    employee = relationship("User", foreign_keys=[employee_user_id])
    watch = relationship("WatchAsset", foreign_keys=[watch_asset_id])

    __table_args__ = (Index("ix_watch_hr_org_employee_recorded", "org_id", "employee_user_id", "recorded_at"),)


# --- R11 Orbital sealed edge ---


class OrbitalEdgeNode(Base):
    __tablename__ = "orbital_edge_nodes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    codename = Column(String(80), nullable=False)
    norad_id = Column(String(32), nullable=True)
    launch_provider = Column(String(40), nullable=False, default="spacex")
    rideshare_slot = Column(String(80), nullable=True)
    mass_kg = Column(Numeric(10, 3), nullable=True)
    status = Column(String(32), nullable=False, default="planned", index=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])

    __table_args__ = (Index("ix_orbital_edge_nodes_org_codename", "org_id", "codename", unique=True),)


class OrbitalAttestation(Base):
    __tablename__ = "orbital_attestations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    node_id = Column(
        UUID(as_uuid=False),
        ForeignKey("orbital_edge_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind = Column(String(40), nullable=False)
    digest_sha256 = Column(String(128), nullable=False)
    payload_uri = Column(String(512), nullable=True)
    verified = Column(Boolean, nullable=False, default=False)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    node = relationship("OrbitalEdgeNode", foreign_keys=[node_id])


# --- R12 AETERNA longevity marketplace ---


class AeternaDnaVaultEntry(Base):
    __tablename__ = "aeterna_dna_vault"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(120), nullable=False)
    source = Column(String(32), nullable=False, default="upload")
    source_uri = Column(String(512), nullable=True)
    content_sha256 = Column(String(128), nullable=False)
    format_hint = Column(String(32), nullable=False, default="vcf")
    status = Column(String(32), nullable=False, default="pending", index=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])
    org = relationship("Organization", foreign_keys=[org_id])

    __table_args__ = (Index("ix_aeterna_dna_vault_owner_created", "owner_user_id", "created_at"),)


class AeternaIntentOrder(Base):
    __tablename__ = "aeterna_intent_orders"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    intent_kind = Column(String(48), nullable=False, index=True)
    vault_id = Column(UUID(as_uuid=False), ForeignKey("aeterna_dna_vault.id", ondelete="SET NULL"), nullable=True, index=True)
    workflow_slug = Column(String(80), nullable=True)
    status = Column(String(32), nullable=False, default="draft", index=True)
    budget_acp = Column(Numeric(36, 18), nullable=False)
    notes = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])
    vault = relationship("AeternaDnaVaultEntry", foreign_keys=[vault_id])

    __table_args__ = (Index("ix_aeterna_intent_orders_owner_created", "owner_user_id", "created_at"),)


class AeternaPartner(Base):
    __tablename__ = "aeterna_partners"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    jurisdiction = Column(String(64), nullable=False)
    license_ref = Column(String(200), nullable=True)
    website = Column(String(512), nullable=True)
    supported_intents = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    verified = Column(Boolean, nullable=False, default=False, index=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    org = relationship("Organization", foreign_keys=[org_id])

    __table_args__ = (Index("ix_aeterna_partners_org_name", "org_id", "name", unique=True),)


# --- Galaxy / solar-system title auction ---


class SpaceAuctionBid(Base):
    __tablename__ = "space_auction_bids"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    lot_id = Column(String(64), nullable=False, index=True)
    bidder_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="placed", index=True)
    note = Column(Text, nullable=True)
    deal_cipher_id = Column(String(96), nullable=True)
    deal_envelope_b64 = Column(Text, nullable=True)
    deal_content_hash = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bidder = relationship("User", foreign_keys=[bidder_user_id])

    __table_args__ = (
        Index("ix_space_auction_bids_lot_created", "lot_id", "created_at"),
        Index("ix_space_auction_bids_lot_amount", "lot_id", "amount_acp"),
    )


class DarkMatterAuctionBid(Base):
    __tablename__ = "dark_matter_auction_bids"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    lot_id = Column(String(64), nullable=False, index=True)
    bidder_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="placed", index=True)
    note = Column(Text, nullable=True)
    deal_cipher_id = Column(String(96), nullable=True)
    deal_envelope_b64 = Column(Text, nullable=True)
    deal_content_hash = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bidder = relationship("User", foreign_keys=[bidder_user_id])

    __table_args__ = (
        Index("ix_dark_matter_auction_bids_lot_created", "lot_id", "created_at"),
        Index("ix_dark_matter_auction_bids_lot_amount", "lot_id", "amount_acp"),
    )


# --- FAUNA companion-animal auction (ACP escrow smart contracts) ---


class AnimalAuctionLot(Base):
    __tablename__ = "animal_auction_lots"

    id = Column(String(64), primary_key=True)
    seller_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    species = Column(String(32), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    breed = Column(String(80), nullable=False)
    age_months = Column(Integer, nullable=True)
    blurb = Column(Text, nullable=False)
    starting_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="live", index=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    contract_address = Column(String(42), nullable=True)
    chain_id = Column(String(32), nullable=True, default="bsc")
    featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    seller = relationship("User", foreign_keys=[seller_user_id])


class AnimalAuctionBid(Base):
    __tablename__ = "animal_auction_bids"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    lot_id = Column(String(64), nullable=False, index=True)
    bidder_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="placed", index=True)
    note = Column(Text, nullable=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    deal_cipher_id = Column(String(96), nullable=True)
    deal_envelope_b64 = Column(Text, nullable=True)
    deal_content_hash = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bidder = relationship("User", foreign_keys=[bidder_user_id])

    __table_args__ = (
        Index("ix_animal_auction_bids_lot_created", "lot_id", "created_at"),
        Index("ix_animal_auction_bids_lot_amount", "lot_id", "amount_acp"),
    )


# --- FLORA flower auction (any form, qty 1…∞, ACP escrow) ---


class FloraAuctionLot(Base):
    __tablename__ = "flora_auction_lots"

    id = Column(String(64), primary_key=True)
    seller_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    form = Column(String(32), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    variety = Column(String(120), nullable=False)
    quantity = Column(BigInteger, nullable=True)  # null = unlimited (∞)
    blurb = Column(Text, nullable=False)
    starting_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="live", index=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    contract_address = Column(String(42), nullable=True)
    chain_id = Column(String(32), nullable=True, default="bsc")
    image_href = Column(String(160), nullable=True)
    featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    seller = relationship("User", foreign_keys=[seller_user_id])


class FloraAuctionBid(Base):
    __tablename__ = "flora_auction_bids"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    lot_id = Column(String(64), nullable=False, index=True)
    bidder_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="placed", index=True)
    note = Column(Text, nullable=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    deal_cipher_id = Column(String(96), nullable=True)
    deal_envelope_b64 = Column(Text, nullable=True)
    deal_content_hash = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bidder = relationship("User", foreign_keys=[bidder_user_id])

    __table_args__ = (
        Index("ix_flora_auction_bids_lot_created", "lot_id", "created_at"),
        Index("ix_flora_auction_bids_lot_amount", "lot_id", "amount_acp"),
    )


# --- TECH IP / technology license auction ---


class TechAuctionLot(Base):
    __tablename__ = "tech_auction_lots"

    id = Column(String(64), primary_key=True)
    seller_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(32), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    stack = Column(String(160), nullable=False)
    blurb = Column(Text, nullable=False)
    starting_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="live", index=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    contract_address = Column(String(42), nullable=True)
    chain_id = Column(String(32), nullable=True, default="bsc")
    featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    seller = relationship("User", foreign_keys=[seller_user_id])


class TechAuctionBid(Base):
    __tablename__ = "tech_auction_bids"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    lot_id = Column(String(64), nullable=False, index=True)
    bidder_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="placed", index=True)
    note = Column(Text, nullable=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    deal_cipher_id = Column(String(96), nullable=True)
    deal_envelope_b64 = Column(Text, nullable=True)
    deal_content_hash = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bidder = relationship("User", foreign_keys=[bidder_user_id])

    __table_args__ = (
        Index("ix_tech_auction_bids_lot_created", "lot_id", "created_at"),
        Index("ix_tech_auction_bids_lot_amount", "lot_id", "amount_acp"),
    )


# --- Literary works auction ---


class LiteraryAuctionLot(Base):
    __tablename__ = "literary_auction_lots"

    id = Column(String(64), primary_key=True)
    seller_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    genre = Column(String(32), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    author = Column(String(120), nullable=False)
    blurb = Column(Text, nullable=False)
    starting_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="live", index=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    contract_address = Column(String(42), nullable=True)
    chain_id = Column(String(32), nullable=True, default="bsc")
    featured = Column(Boolean, nullable=False, default=False)
    review_target_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    seller = relationship("User", foreign_keys=[seller_user_id])


class LiteraryAuctionBid(Base):
    __tablename__ = "literary_auction_bids"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    lot_id = Column(String(64), nullable=False, index=True)
    bidder_user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="placed", index=True)
    note = Column(Text, nullable=True)
    contract_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(128), nullable=True, index=True)
    deal_cipher_id = Column(String(96), nullable=True)
    deal_envelope_b64 = Column(Text, nullable=True)
    deal_content_hash = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bidder = relationship("User", foreign_keys=[bidder_user_id])

    __table_args__ = (
        Index("ix_literary_auction_bids_lot_created", "lot_id", "created_at"),
        Index("ix_literary_auction_bids_lot_amount", "lot_id", "amount_acp"),
    )


# --- ACP Insurance (economy/insurance) ---


class InsurancePool(Base):
    __tablename__ = "insurance_pools"

    id = Column(String(64), primary_key=True)
    label = Column(String(120), nullable=False)
    coverage_class = Column(String(48), nullable=False, index=True)
    status = Column(String(24), nullable=False, default="open", index=True)
    collateral_spec_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    pool_id = Column(String(64), ForeignKey("insurance_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    holder_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    coverage_class = Column(String(48), nullable=False, index=True)
    coverage_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    asset_ref_type = Column(String(48), nullable=True)
    asset_ref_id = Column(String(128), nullable=True)
    sum_insured_acp = Column(Numeric(38, 18), nullable=False)
    premium_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="active", index=True)
    contract_hash = Column(String(64), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    holder = relationship("User", foreign_keys=[holder_user_id])


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=False), ForeignKey("insurance_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    claimant_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="filed", index=True)
    ref_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    note = Column(Text, nullable=True)
    contract_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    claimant = relationship("User", foreign_keys=[claimant_user_id])


# --- ACP Arena (prediction desk + house games) ---


class ArenaMarket(Base):
    __tablename__ = "arena_markets"

    id = Column(String(64), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(48), nullable=False, default="event", index=True)
    status = Column(String(24), nullable=False, default="open", index=True)
    outcome_yes_label = Column(String(80), nullable=False, default="YES")
    outcome_no_label = Column(String(80), nullable=False, default="NO")
    closes_at = Column(DateTime(timezone=True), nullable=True)
    resolved_outcome = Column(String(8), nullable=True)
    contract_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ArenaBet(Base):
    __tablename__ = "arena_bets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    market_id = Column(String(64), ForeignKey("arena_markets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    side = Column(String(8), nullable=False)
    stake_acp = Column(Numeric(38, 18), nullable=False)
    status = Column(String(24), nullable=False, default="open", index=True)
    payout_acp = Column(Numeric(38, 18), nullable=True)
    contract_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


class ArenaHouseRound(Base):
    __tablename__ = "arena_house_rounds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game = Column(String(24), nullable=False, index=True)
    stake_acp = Column(Numeric(38, 18), nullable=False)
    choice = Column(String(32), nullable=False)
    server_seed_hash = Column(String(64), nullable=False)
    server_seed = Column(String(128), nullable=True)
    result = Column(String(32), nullable=True)
    won = Column(Boolean, nullable=True)
    payout_acp = Column(Numeric(38, 18), nullable=True)
    house_edge_bps = Column(Integer, nullable=False, default=200)
    status = Column(String(24), nullable=False, default="resolved", index=True)
    contract_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])


# --- R13 Lunar land trading ---


class LunarParcel(Base):
    __tablename__ = "lunar_parcels"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    parcel_code = Column(String(32), nullable=False, unique=True, index=True)
    name = Column(String(160), nullable=False)
    region = Column(String(120), nullable=False, index=True)
    lat_deg = Column(Numeric(10, 6), nullable=False)
    lon_deg = Column(Numeric(10, 6), nullable=False)
    area_km2 = Column(Numeric(18, 6), nullable=False)
    list_price_acp = Column(Numeric(36, 18), nullable=False)
    status = Column(String(32), nullable=False, default="listed", index=True)
    source = Column(String(32), nullable=False, default="catalog")
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LunarInterestOrder(Base):
    __tablename__ = "lunar_interest_orders"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parcel_id = Column(UUID(as_uuid=False), ForeignKey("lunar_parcels.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="open", index=True)
    budget_acp = Column(Numeric(36, 18), nullable=False)
    notes = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])
    parcel = relationship("LunarParcel", foreign_keys=[parcel_id])

    __table_args__ = (Index("ix_lunar_interest_orders_owner_created", "owner_user_id", "created_at"),)


# --- User IMAP/SMTP provider accounts (single account) ---


class MailProviderAccount(Base):
    __tablename__ = "mail_provider_accounts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    display_name = Column(String(160), nullable=True)
    email_address = Column(String(320), nullable=False)
    provider_kind = Column(String(32), nullable=False, default="imap_smtp")
    imap_host = Column(String(255), nullable=False)
    imap_port = Column(Integer, nullable=False, default=993)
    imap_username = Column(String(320), nullable=False)
    imap_password_enc = Column(Text, nullable=False)
    imap_use_ssl = Column(Boolean, nullable=False, default=True)
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False, default=587)
    smtp_username = Column(String(320), nullable=False)
    smtp_password_enc = Column(Text, nullable=False)
    smtp_use_tls = Column(Boolean, nullable=False, default=True)
    smtp_use_ssl = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False, default="connected", index=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])


class WacpLiquidityStage(Base):
    """Operator-recorded Stage A/B/C deployment envelope."""

    __tablename__ = "wacp_liquidity_stages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    stage_id = Column(String(64), nullable=False, unique=True, index=True)
    operator_label = Column(String(128), nullable=True)
    mint_wacp_wei = Column(Numeric(38, 0), nullable=True)
    approval_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    status = Column(String(32), nullable=False, default="planned")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    allocations = relationship("WacpTreasuryAllocation", back_populates="stage", cascade="all, delete-orphan")
    positions = relationship("WacpV3Position", back_populates="stage", cascade="all, delete-orphan")


class WacpTreasuryAllocation(Base):
    __tablename__ = "wacp_treasury_allocations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    stage_id = Column(UUID(as_uuid=False), ForeignKey("wacp_liquidity_stages.id", ondelete="CASCADE"), nullable=False)
    bucket = Column(String(16), nullable=False)
    fraction = Column(Numeric(8, 6), nullable=True)
    wacp_wei = Column(Numeric(38, 0), nullable=True)
    usdt_wei = Column(Numeric(38, 0), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    stage = relationship("WacpLiquidityStage", back_populates="allocations")

    __table_args__ = (Index("ix_wacp_treasury_alloc_stage", "stage_id"),)


class WacpV3Position(Base):
    __tablename__ = "wacp_v3_positions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    stage_id = Column(UUID(as_uuid=False), ForeignKey("wacp_liquidity_stages.id", ondelete="CASCADE"), nullable=False)
    pool_address = Column(String(64), nullable=False)
    position_token_id = Column(String(78), nullable=True)
    tick_lower = Column(Integer, nullable=True)
    tick_upper = Column(Integer, nullable=True)
    amount0_wei = Column(Numeric(38, 0), nullable=True)
    amount1_wei = Column(Numeric(38, 0), nullable=True)
    mint_tx_hash = Column(String(80), nullable=True)
    pool_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    stage = relationship("WacpLiquidityStage", back_populates="positions")

    __table_args__ = (Index("ix_wacp_v3_positions_stage", "stage_id"),)


# --- ANCAP Dating (proximity + optional cloud) ---


class DatingProfile(Base):
    __tablename__ = "dating_profiles"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    display_name = Column(String(80), nullable=False)
    bio = Column(Text, nullable=True)
    age_attested_18 = Column(Boolean, nullable=False, default=False)
    visibility = Column(String(24), nullable=False, default="nearby")  # nearby | public | hidden
    lat = Column(Numeric(10, 7), nullable=True)
    lon = Column(Numeric(10, 7), nullable=True)
    mesh_peer_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DatingAccessPoint(Base):
    __tablename__ = "dating_access_points"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    creator_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    lat = Column(Numeric(10, 7), nullable=False)
    lon = Column(Numeric(10, 7), nullable=False)
    ble_service_hint = Column(String(64), nullable=False, default="a11c0001-a11c-4a7e-9c01-444154494e47")
    status = Column(String(24), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class DatingLike(Base):
    __tablename__ = "dating_likes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    from_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_dating_likes_from_to", "from_user_id", "to_user_id", unique=True),
    )


class DatingMatch(Base):
    __tablename__ = "dating_matches"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    user_a_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_b_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (Index("ix_dating_matches_users", "user_a_id", "user_b_id", unique=True),)


class DatingMessage(Base):
    __tablename__ = "dating_messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=False), ForeignKey("dating_matches.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class DatingReport(Base):
    __tablename__ = "dating_reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    reporter_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class AcpExplorerIndexerState(Base):
    """Watermark for public ACP explorer full-chain index."""

    __tablename__ = "acp_explorer_indexer_state"

    id = Column(Integer, primary_key=True, default=1)
    last_scanned_height = Column(Integer, nullable=False, default=0)
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)


class AcpExplorerBlock(Base):
    __tablename__ = "acp_explorer_blocks"

    height = Column(Integer, primary_key=True)
    hash = Column(String(128), nullable=False, index=True)
    time = Column(BigInteger, nullable=True)
    tx_count = Column(Integer, nullable=False, default=0)
    size = Column(Integer, nullable=True)


class AcpExplorerTx(Base):
    __tablename__ = "acp_explorer_txs"

    txid = Column(String(128), primary_key=True)
    block_height = Column(Integer, nullable=True, index=True)
    block_hash = Column(String(128), nullable=True)
    block_time = Column(BigInteger, nullable=True)
    fee_units = Column(BigInteger, nullable=False, default=0)
    input_count = Column(Integer, nullable=False, default=0)
    output_count = Column(Integer, nullable=False, default=0)


class AcpExplorerAddressEvent(Base):
    __tablename__ = "acp_explorer_address_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    address = Column(String(128), nullable=False, index=True)
    txid = Column(String(128), nullable=False, index=True)
    direction = Column(String(8), nullable=False)
    amount_units = Column(BigInteger, nullable=False, default=0)
    vout = Column(Integer, nullable=True)
    vin = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True, index=True)

    __table_args__ = (
        Index("ix_acp_explorer_addr_events_addr_height", "address", "height"),
    )

# --- Workflow operations: durable context, revisions, scheduling and execution ---
class WorkflowProject(Base):
    __tablename__ = "workflow_projects"
    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    context_json = Column(JSONB, nullable=False, default=dict)
    members_json = Column(JSONB, nullable=False, default=dict)
    retention_days = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkflowConnection(Base):
    __tablename__ = "workflow_connections"
    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    kind = Column(String(24), nullable=False)
    config_json = Column(JSONB, nullable=False, default=dict)
    secret_box = Column(Text, nullable=False, default="")
    allow_delivery = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkflowAutomation(Base):
    __tablename__ = "workflow_automations"
    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("workflow_projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    versions_json = Column(JSONB, nullable=False, default=list)
    published_version = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, default=False)
    interval_minutes = Column(Integer, nullable=False, default=1440)
    monthly_budget_acp = Column(Numeric(36,18), nullable=False, default=0)
    spent_acp = Column(Numeric(36,18), nullable=False, default=0)
    budget_month = Column(String(7), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkflowOperationRun(Base):
    __tablename__ = "workflow_operation_runs"
    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    automation_id = Column(UUID(as_uuid=False), ForeignKey("workflow_automations.id", ondelete="SET NULL"), nullable=True)
    request_key = Column(String(100), nullable=False)
    request_hash = Column(String(64), nullable=False)
    kind = Column(String(16), nullable=False, default="manual")
    state = Column(String(24), nullable=False, default="queued", index=True)
    snapshot_json = Column(JSONB, nullable=False, default=dict)
    progress_json = Column(JSONB, nullable=False, default=dict)
    cost_acp = Column(Numeric(36,18), nullable=False, default=0)
    max_cost_acp = Column(Numeric(36,18), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (Index("uq_workflow_ops_owner_request", "owner_user_id", "request_key", unique=True),)
