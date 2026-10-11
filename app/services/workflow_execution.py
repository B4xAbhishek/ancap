from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.schemas import Money, WorkflowBundlePublic, WorkflowCreditPackagePublic, WorkflowTemplatePublic


WORKFLOW_TEMPLATES: list[WorkflowTemplatePublic] = [
    WorkflowTemplatePublic(
        slug="token-listing-pack",
        title="Token Listing Pack",
        category="Launch",
        summary="Generate reusable listing answers for exchanges, token pages, and directories.",
        description="Creates short and long project copy, listing form answers, and exchange-friendly token descriptions.",
        price=Money(amount="10", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=20,
        preview_items=["Short project summary", "Listing answer preview", "Output structure"],
        output_items=["Token bio", "Project description", "Listing answers", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "status_timeline"],
        tags=["listing", "launch", "token"],
    ),
    WorkflowTemplatePublic(
        slug="crypto-campaign-builder",
        title="Crypto Campaign Builder",
        category="Marketing",
        summary="Build a launch or growth plan for Telegram, X, community actions, and referral loops.",
        description="Creates a structured 7/14/30-day campaign plan with messaging, actions, and execution checklist.",
        price=Money(amount="19", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=30,
        preview_items=["Campaign skeleton", "Channel mix", "Execution phases"],
        output_items=["Campaign plan", "Post ideas", "Contest mechanics", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "proof_metadata"],
        tags=["marketing", "growth", "campaign"],
    ),
    WorkflowTemplatePublic(
        slug="telegram-growth-kit",
        title="Telegram Growth Kit",
        category="Community",
        summary="Design a Telegram operating kit with rules, posting flow, onboarding, and moderation guidance.",
        description="Produces a practical operating pack for crypto communities that want cleaner growth and moderation structure.",
        price=Money(amount="12", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=25,
        preview_items=["Rule set preview", "Welcome flow preview", "Ops structure"],
        output_items=["Rules", "Welcome flow", "Moderator checklist", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "template_version", "completion_receipt"],
        tags=["telegram", "community", "moderation"],
    ),
    WorkflowTemplatePublic(
        slug="airdrop-bounty-builder",
        title="Airdrop / Bounty Builder",
        category="Campaigns",
        summary="Create tasks, reward logic, anti-sybil rules, and proof policy for bounty campaigns.",
        description="Helps teams structure incentive campaigns without turning them into low-quality spam farms.",
        price=Money(amount="15", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=30,
        preview_items=["Task structure", "Reward logic", "Verification outline"],
        output_items=["Task matrix", "Reward table", "Proof policy", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "verification_policy"],
        tags=["bounty", "airdrop", "campaign"],
    ),
    WorkflowTemplatePublic(
        slug="token-risk-report",
        title="Token Risk Report",
        category="Risk",
        summary="Produce a structured risk and trust snapshot for a token, wallet cluster, or liquidity setup.",
        description="Summarizes concentration, liquidity, trust signals, and operational flags into a usable risk report shell.",
        price=Money(amount="14", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=20,
        preview_items=["Risk summary", "Trust notes", "Flag categories"],
        output_items=["Risk snapshot", "Trust signals", "Operational flags", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "asset_reference", "status_timeline"],
        tags=["risk", "token", "intelligence"],
    ),
    WorkflowTemplatePublic(
        slug="token-launch-audit-pack",
        title="Token Launch Audit Pack",
        category="Audit",
        summary="Audit launch readiness across token narrative, liquidity proof, campaign plan, and trust signals.",
        description="Produces a launch-readiness audit with scoring, gaps, mitigation tasks, and a proof-backed delivery receipt.",
        price=Money(amount="79", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=55,
        preview_items=["Launch readiness score", "Gap matrix", "Priority fixes"],
        output_items=["Audit scorecard", "Launch risk matrix", "Fix backlog", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "provider_cost_estimate", "margin_snapshot", "status_timeline"],
        tags=["audit", "launch", "risk", "premium"],
    ),
    WorkflowTemplatePublic(
        slug="exchange-listing-submission-pack",
        title="Exchange Listing Submission Pack",
        category="Listings",
        summary="Prepare exchange-facing answers, due-diligence pack, market narrative, and submission checklist.",
        description="Creates a premium exchange listing submission pack designed for cleaner reviewer handoff and repeat submissions.",
        price=Money(amount="149", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["Exchange answer map", "Reviewer checklist", "Submission sequence"],
        output_items=["Exchange form answers", "Due-diligence packet", "Reviewer memo", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "listing_readiness", "margin_snapshot", "status_timeline"],
        tags=["listing", "exchange", "launch", "premium"],
    ),
    WorkflowTemplatePublic(
        slug="kol-telegram-campaign-builder",
        title="KOL / Telegram Campaign Builder",
        category="Growth",
        summary="Build KOL briefs, Telegram campaign mechanics, proof policy, and attribution-ready growth flow.",
        description="Packages a campaign that can be handed to community operators, Telegram admins, and KOL partners without losing proof discipline.",
        price=Money(amount="99", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=70,
        preview_items=["KOL brief preview", "Telegram funnel", "Attribution plan"],
        output_items=["KOL brief kit", "Telegram campaign plan", "Partner scripts", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "campaign_attribution", "margin_snapshot", "status_timeline"],
        tags=["kol", "telegram", "growth", "premium"],
    ),
    WorkflowTemplatePublic(
        slug="token-risk-report-pro",
        title="Token Risk Report Pro",
        category="Risk",
        summary="Create a pro-grade token risk report with scoring, evidence requests, wallet/liquidity checks, and buyer-ready summary.",
        description="Turns a lightweight token snapshot into a premium report with structured risks, evidence gaps, and recommended next checks.",
        price=Money(amount="59", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Pro risk score", "Evidence gaps", "Buyer-ready summary"],
        output_items=["Risk scorecard", "Evidence request list", "Liquidity and holder flags", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "asset_reference", "risk_score", "margin_snapshot", "status_timeline"],
        tags=["risk", "token", "report", "premium"],
    ),
    WorkflowTemplatePublic(
        slug="agent-api-readiness-pack",
        title="Agent API Readiness Pack",
        category="Developers",
        summary="Package a crypto API or workflow for AI-agent buyers with pricing, x402 metadata, docs, and spend controls.",
        description="Creates the commercial surface an external agent needs: endpoint offer, pricing copy, 402 response plan, curl examples, and receipt schema.",
        price=Money(amount="99", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=65,
        preview_items=["Endpoint offer map", "x402 payment shape", "Spend-control checklist"],
        output_items=["Developer offer page", "API pricing matrix", "x402 response plan", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "x402_payment_terms", "margin_snapshot", "status_timeline"],
        tags=["api", "x402", "agents", "premium"],
    ),
    WorkflowTemplatePublic(
        slug="ai-iso-governance-readiness-pack",
        title="AI / ISO Governance Readiness Pack",
        category="Governance",
        summary="Turn an AI workflow into an audit-ready operating pack with SOPs, risk controls, evidence, and corrective-action flow.",
        description="Maps AI execution, LLM supplier controls, proof receipts, audit trails, and ISO-inspired operating discipline into a practical governance packet. This is readiness support, not a certification guarantee.",
        price=Money(amount="149", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["AI capability map", "ISO-style control checklist", "Evidence and audit trail plan"],
        output_items=["AI governance memo", "SOP checklist", "Risk and control matrix", "Corrective-action plan", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "ai_governance_scope", "control_evidence_map", "status_timeline"],
        tags=["ai", "iso", "governance", "audit", "premium"],
        ai_system_card={
            "capability": "structured-generation",
            "capability_detail": "LLM-assisted generation of governance, audit, and compliance documentation",
            "supplier": {"provider": "Anthropic (Teneta)", "model": "claude-sonnet-4-6"},
            "fallback": "template-based shell with degraded_run=true when LLM is unavailable",
            "audit_evidence": ["prompt", "model", "provider_status", "output_hash", "receipt"],
            "corrective_action_plan": ["Owner assignment on degraded runs", "Human review for premium outputs", "Root cause logged in llm_usage_events"],
        },
    ),
    WorkflowTemplatePublic(
        slug="aeterna-dna-wellness-report",
        title="AETERNA DNA Wellness Report",
        category="AETERNA",
        summary="Turn a vaulted genome hash / VCF summary into an ACP-paid wellness annotation brief.",
        description="Produces a structured genomic wellness report shell from consented DNA vault metadata. Educational and consult-prep only — not a diagnosis and not a DIY editing protocol.",
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=["Trait annotation map", "Data-quality notes", "Partner handoff checklist"],
        output_items=["Wellness annotation brief", "Variant summary table", "Consent receipt", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "vault_hash_ref", "status_timeline"],
        tags=["aeterna", "dna", "wellness", "longevity"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-longevity-panel-brief",
        title="AETERNA Longevity Panel Brief",
        category="AETERNA",
        summary="Build a longevity planning brief for licensed-partner review from DNA vault + lifestyle inputs.",
        description="Creates a longevity panel brief with risk themes, monitoring suggestions, and clinic questions. No wet-lab protocols.",
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=55,
        preview_items=["Longevity theme map", "Monitoring cadence", "Clinic question list"],
        output_items=["Longevity brief", "Panel shortlist", "Partner referral memo", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "status_timeline"],
        tags=["aeterna", "longevity", "panel"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-pigmentation-consult-brief",
        title="AETERNA Pigmentation Consult Brief",
        category="AETERNA",
        summary="Prepare a pigmentation / eye-color consult brief for licensed clinical partners.",
        description="Structures goals, genetic context from vault metadata, and questions for a licensed consult. Does not provide CRISPR guide design or DIY enhancement steps.",
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=["Goal framing", "Genetic context notes", "Consult agenda"],
        output_items=["Consult brief", "Partner matching hints", "Risk/consent reminders", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "status_timeline"],
        tags=["aeterna", "pigmentation", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-telomere-panel-review",
        title="AETERNA Telomere Panel Review",
        category="AETERNA",
        summary="Review telomere-related panel results and produce a partner-ready interpretation shell.",
        description="Summarizes telomere panel inputs into an interpretation shell for clinician review. Not a treatment protocol.",
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=35,
        preview_items=["Panel summary", "Interpretation caveats", "Follow-up questions"],
        output_items=["Telomere review memo", "Caveats list", "Partner handoff", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "status_timeline"],
        tags=["aeterna", "telomere", "longevity"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-disease-risk-navigator",
        title="AETERNA Disease Risk Navigator",
        category="AETERNA",
        summary="Navigate disease-risk themes from consented genomic metadata into a clinician discussion guide.",
        description="Builds a disease-risk navigator for educational discussion with licensed providers. Explicitly not diagnostic.",
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Risk theme map", "Evidence gaps", "Clinician agenda"],
        output_items=["Risk navigator", "Evidence gap list", "Referral memo", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "vault_hash_ref", "status_timeline"],
        tags=["aeterna", "disease-risk", "clinical"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-molecular-aging-profile",
        title="AETERNA Molecular Aging Profile (15 axes)",
        category="AETERNA",
        summary="Map consented blood-RNA / PCR panel metadata onto 15 hallmark axes — configuration of aging, not one bio-age number.",
        description=(
            "Builds a partner-ready molecular aging profile across 15 hallmark themes "
            "(DNA repair, telomeres, epigenetics, proteostasis, autophagy, energy metabolism, "
            "senescence, stem-cell maintenance, mitochondria, inflammation, signaling, matrix, "
            "circadian/systemic, immune aging, nutrient sensing). "
            "Sex-aware framing preferred. Educational / licensed-consult prep only — "
            "not a diagnostic PCR assay and not a DIY wet-lab kit. "
            "Inspired by public research on multi-gene venous-blood RNA aging panels."
        ),
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=60,
        preview_items=["15-axis hallmark map", "Sex-aware caveats", "Partner discussion agenda"],
        output_items=[
            "Molecular aging profile brief",
            "Per-hallmark configuration table",
            "Monitoring / intervention discussion prompts",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "vault_hash_ref", "hallmark_count", "status_timeline"],
        tags=["aeterna", "longevity", "molecular-aging", "blood-rna", "hallmarks"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-stem-cell-organ-print",
        title="AETERNA Stem-Cell Organ Print",
        category="AETERNA",
        summary="Licensed-partner organ bioprint from autologous stem cells — wisdom-tooth DPSC fallback — 250,000 ACP per organ.",
        description=(
            "Settles 250,000 ACP per organ and issues a licensed-partner bioreactor handoff. "
        "Primary cell source: autologous stem cells. Fallback: dental pulp stem cells (DPSC) from a wisdom tooth. "
        "A dedicated DPSC biomaterial SKU (aeterna-dpsc-biomaterial, 65,000 ACP) expands DPSC into a construct; "
        "this organ-print SKU remains 250,000 ACP per organ. "
        "Printing occurs only in a licensed biochemical reactor operated by a verified partner. "
            "Not a home kit — no wet-lab protocol, CRISPR design, gene synthesis, or DIY cell culture."
        ),
        price=Money(amount="250000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["Cell-source intake", "Bioreactor partner match", "Per-organ ACP quote"],
        output_items=["Organ-print intake brief", "Cell-source plan", "Licensed bioreactor handoff", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "organ_unit_price_acp", "status_timeline"],
        tags=["aeterna", "organ-print", "stem-cells", "bioreactor"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-mrna-reprogramming-brief",
        title="AETERNA Partial Reprogramming Consult (mRNA / LNP literacy)",
        category="AETERNA",
        summary=(
            "Licensed-partner consult brief on partial cellular reprogramming via mRNA in lipid nanoparticles — "
            "public patent-literacy only, 1,000,000 ACP."
        ),
        description=(
            "Builds a partner-ready discussion brief on partial epigenetic reprogramming: "
            "deliver mRNA instructions so aged cells regain some youthful functions without becoming stem cells. "
            "Cites public USPTO notice-of-allowance journalism (Daewoong eTurna ionizable lipids, Aug 2026) "
            "as educational context. Not an approved drug, not an issued-patent warranty, and not a wet-lab kit. "
            "ANCAP does not provide lipid recipes, mRNA sequences, LNP formulation steps, or DIY enhancement protocols."
        ),
        price=Money(amount="1000000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Partial vs full reprogramming framing", "Delivery literacy (mRNA in LNP)", "Partner consult agenda"],
        output_items=[
            "Partial-reprogramming consult brief",
            "Public-citation caveats (allowance ≠ grant ≠ drug approval)",
            "Licensed-partner handoff checklist",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "status_timeline"],
        tags=["aeterna", "longevity", "mrna", "lnp", "reprogramming", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-vet-cat-cryo-restore",
        title="AETERNA Feline Tissue Cryoconservator-Restorer",
        category="AETERNA",
        summary=(
            "Licensed-veterinary-partner intake for a feline tissue cryoconservator-restorer "
            "(controlled-rate freeze, LN2 store, thaw/restore) — 75,000 ACP."
        ),
        description=(
            "Settles 75,000 ACP and issues a licensed-veterinary-partner brief for cat tissue banking: "
            "harvest of a small sample (skin, cartilage, fat, muscle, or stem-cell niche), controlled-rate "
            "freezing to about −150…−196 °C with cryoprotectant protocols, liquid-nitrogen storage, then "
            "planned thaw and partner-clinic return of tissue. Conceptual architecture only — ANCAP does not "
            "manufacture the chamber, does not practice veterinary medicine, and does not claim return-to-life "
            "or a survival-rate warranty. No wet-lab protocol, CRISPR design, or home cryo kit."
        ),
        price=Money(amount="75000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=60,
        preview_items=["Species/tissue intake", "Veterinary partner match", "Cryo-path consent pack"],
        output_items=[
            "Feline cryo-restore intake brief",
            "Licensed veterinary handoff",
            "Non-claim checklist (no resurrection / no survival %)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "species", "status_timeline"],
        tags=["aeterna", "veterinary", "feline", "cryo", "tissue-bank"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-vet-regen-pod",
        title="AETERNA Canine VET REGEN POD",
        category="AETERNA",
        summary=(
            "Licensed-veterinary-partner organ-transplant and regeneration chamber pathway for dogs "
            "(VET REGEN POD) — 180,000 ACP."
        ),
        description=(
            "Settles 180,000 ACP and issues a licensed-veterinary-partner brief for a canine organ pathway: "
            "organ bank at cryogenic temperature, 3D tissue bioprint assist, robot-assisted placement, "
            "stem-cell / growth-factor stimulation, and post-op monitoring inside a sealed veterinary chamber. "
            "Infographics illustrate intended partner architecture. ANCAP does not operate VET REGEN POD hardware, "
            "does not quote survival percentages or regeneration speed, and does not sell a home kit. "
            "Physical procedures occur only under a licensed veterinarian."
        ),
        price=Money(amount="180000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=75,
        preview_items=["Canine organ pathway intake", "Chamber partner match", "Immunocompatibility pack"],
        output_items=[
            "VET REGEN POD intake brief",
            "Licensed veterinary handoff",
            "Non-claim checklist (no resurrection / no survival %)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "species", "status_timeline"],
        tags=["aeterna", "veterinary", "canine", "organ-print", "regen-pod"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-vinci-light-chamber",
        title="AETERNA Vinci Light Chamber",
        category="AETERNA",
        summary=(
            "Licensed phototherapy-partner intake for a full-body LED / UVA / red / near-IR "
            "photobiomodulation chamber (Leonardo sunlight-health literacy) — 48,000 ACP."
        ),
        description=(
            "Settles 48,000 ACP and issues a licensed dermatology or phototherapy-partner brief for a "
            "full-body light-session chamber: red 620–680 nm and near-IR 780–950 nm as photobiomodulation "
            "literacy (cytochrome-c oxidase / ATP as public research framing, not a guaranteed effect), "
            "plus UVA 320–400 nm only under partner screening. Inspired by Leonardo da Vinci’s notes on "
            "sunlight and the body — not a reconstructed invention, not a verified Leonardo quote as a "
            "device spec, and not a museum replica. ANCAP does not manufacture the chamber, does not "
            "practice medicine, and does not claim safe tanning, vitamin-D treatment, wound closure, or "
            "anti-aging results. UV tanning is a known skin-cancer risk class. No home LED-array recipe."
        ),
        price=Money(amount="48000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=["Skin-type / contraindication intake", "Phototherapy partner match", "Session-protocol literacy pack"],
        output_items=[
            "Vinci light-chamber intake brief",
            "Licensed phototherapy handoff",
            "Non-claim checklist (no safe tan / no device CE-FDA claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "bands", "status_timeline"],
        tags=["aeterna", "photobiomodulation", "light-chamber", "leonardo", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-microwave-body-contouring",
        title="AETERNA Microwave Body Contouring",
        category="AETERNA",
        summary=(
            "Licensed aesthetic/dermatology-partner intake for contact-cooled microwave body contouring "
            "(2.45 / 5.8 GHz ISM applicator) — 52,000 ACP."
        ),
        description=(
            "Settles 52,000 ACP and issues a licensed dermatology or aesthetic-medicine partner brief for a "
            "contact-cooled microwave applicator in the 2.45 GHz / 5.8 GHz ISM bands. Public device literature "
            "discusses selective heating of adipocytes with surface cooling; AETERNA does not claim blebbing, "
            "macrophage clearance, lymphatic drainage, or a guaranteed contour change. Not liposuction, not a "
            "weight-loss program, not a marketed medical device, and not a CE/FDA product sold by ANCAP. "
            "Physical sessions occur only under a licensed clinician after screening (implants, pacemakers, "
            "pregnancy, metal, burns). No home microwave-antenna recipe."
        ),
        price=Money(amount="52000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=["Contraindication intake", "Aesthetic partner match", "Session-protocol literacy pack"],
        output_items=[
            "Microwave body-contouring intake brief",
            "Licensed aesthetic handoff",
            "Non-claim checklist (no lipo / no guaranteed fat loss / no device CE-FDA claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "bands", "status_timeline"],
        tags=["aeterna", "body-contouring", "microwave", "aesthetic", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-biofusion-micromanipulation",
        title="AETERNA BioFusion Micromanipulation Chamber",
        category="AETERNA",
        summary=(
            "Licensed-partner intake for a BioFusion micromanipulation chamber "
            "(IVF/ICSI, plant pollination, embryo observation, microorganism handling) — 88,000 ACP."
        ),
        description=(
            "Settles 88,000 ACP and issues a licensed-partner brief for a conceptual BioFusion chamber: "
            "temperature / pH / gas control, HEPA-UV enclosure, and sub-micron micromanipulators as architecture "
            "literacy. Rails: licensed assisted-reproduction clinic (IVF/ICSI), licensed agricultural research "
            "(plant pollination / hybridization), embryo-development observation as clinic protocol literacy, "
            "and licensed BSL-lab microorganism handling. ANCAP does not operate a fertility clinic, does not "
            "create or store embryos, does not guarantee pregnancy or a viable zygote, does not manufacture the "
            "cart, and does not sell gene-editing, CRISPR, pathogen, or home ICSI recipes. Infographic "
            "'genetic manipulations' copy is partner-lab literacy, not a product."
        ),
        price=Money(amount="88000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=55,
        preview_items=["Contraindication / jurisdiction intake", "ART or BSL partner match", "Non-claim protocol pack"],
        output_items=[
            "BioFusion micromanipulation intake brief",
            "Licensed lab / clinic handoff",
            "Non-claim checklist (no pregnancy / no embryo / no gene-edit / no device CE-FDA claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "rails", "status_timeline"],
        tags=["aeterna", "biofusion", "micromanipulation", "ivf", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-dpsc-biomaterial",
        title="AETERNA Wisdom-Tooth DPSC Biomaterial",
        category="AETERNA",
        summary=(
            "Licensed-bioreactor intake to expand autologous wisdom-tooth dental pulp stem cells (DPSC) "
            "into a biomaterial construct — 65,000 ACP."
        ),
        description=(
            "Settles 65,000 ACP and issues a licensed biochemical-reactor partner brief to harvest / receive "
            "wisdom-tooth dental pulp stem cells and expand them into a biomaterial construct (scaffold or "
            "tissue sheet). This is not a full organ print — that remains aeterna-stem-cell-organ-print at "
            "250,000 ACP per organ, where DPSC is the fallback cell source. ANCAP does not culture cells, "
            "does not practice dentistry or regenerative medicine, and does not claim an FDA/CE cell therapy "
            "or a guaranteed organ. No home culture kit, CRISPR design, or gene synthesis."
        ),
        price=Money(amount="65000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Dental / DPSC intake", "Bioreactor partner match", "Construct-goal consent pack"],
        output_items=[
            "DPSC biomaterial intake brief",
            "Licensed bioreactor handoff",
            "Non-claim checklist (not a full organ / not a cell-therapy approval)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "cell_source", "status_timeline"],
        tags=["aeterna", "dpsc", "wisdom-tooth", "biomaterial", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-vascular-care-plus",
        title="AETERNA Vascular Care+",
        category="AETERNA",
        summary=(
            "Licensed phlebology/aesthetic-partner intake for Vascular Care+ "
            "(anhydrous N2+O2 flow plus light-wave applicator) — 54,000 ACP."
        ),
        description=(
            "Settles 54,000 ACP and issues a licensed phlebology, vascular-medicine, or aesthetic-partner brief "
            "for a conceptual Vascular Care+ cart: controlled anhydrous nitrogen-oxygen flow plus a light-wave "
            "handpiece. Infographic copy about vessel dilation, oedema, varicose veins, or diabetic angiopathy "
            "is protocol literacy, not a guaranteed clinical result. ANCAP does not manufacture the cart, does "
            "not sell medical gases, does not treat thrombosis / DVT / pulmonary embolism, and does not claim "
            "CE/FDA device status. Physical sessions occur only under a licensed clinician after screening. "
            "No home gas-applicator recipe."
        ),
        price=Money(amount="54000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=["Contraindication / DVT intake", "Phlebology partner match", "Session-protocol literacy pack"],
        output_items=[
            "Vascular Care+ intake brief",
            "Licensed clinic handoff",
            "Non-claim checklist (no thrombosis treatment / no guaranteed varicose cure / no device CE-FDA claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "gas", "status_timeline"],
        tags=["aeterna", "vascular", "phlebology", "gas-light", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-vascular-care",
        title="AETERNA Vascular Care",
        category="AETERNA",
        summary=(
            "Licensed phlebology/aesthetic-partner intake for Vascular Care "
            "(ultrasound / radiofrequency / thermal applicator) — 58,000 ACP."
        ),
        description=(
            "Settles 58,000 ACP and issues a licensed phlebology, vascular-medicine, or aesthetic-partner brief "
            "for a conceptual Vascular Care cart combining ultrasound, radiofrequency, and thermal applicators. "
            "Infographic copy about vessel tone, oedema, or varicose diameter is protocol literacy, not a "
            "guaranteed result. Not surgery, not a marketed medical device, and not a CE/FDA product sold by "
            "ANCAP. Physical sessions occur only under a licensed clinician after screening. No home RF/US recipe."
        ),
        price=Money(amount="58000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=["Contraindication intake", "Phlebology partner match", "Session-protocol literacy pack"],
        output_items=[
            "Vascular Care intake brief",
            "Licensed clinic handoff",
            "Non-claim checklist (no surgery / no guaranteed vein result / no device CE-FDA claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "modalities", "status_timeline"],
        tags=["aeterna", "vascular", "phlebology", "ultrasound", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-transdermal-pistol",
        title="AETERNA Needle-Free Transdermal Pistol",
        category="AETERNA",
        summary=(
            "Licensed clinic-partner intake for a needle-free transdermal pistol "
            "(aerosol actives plus carrier gas) — 46,000 ACP."
        ),
        description=(
            "Settles 46,000 ACP and issues a licensed clinic-partner brief for a conceptual needle-free "
            "transdermal pistol: aerosol of actives plus carrier gas (CO2 / N2 / O2 literacy) across epithelium. "
            "Infographic copy about varicose veins, fat reduction, cosmetics, or joints is protocol literacy, "
            "not a guaranteed dose or outcome. ANCAP does not compound drugs, does not dispense prescriptions, "
            "does not sell the pistol, and does not claim CE/FDA device status. Physical sessions occur only "
            "under a licensed clinician with a lawful substance list. No home injection or mesotherapy kit."
        ),
        price=Money(amount="46000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=["Contraindication / substance-list intake", "Clinic partner match", "Non-claim protocol pack"],
        output_items=[
            "Transdermal pistol intake brief",
            "Licensed clinic handoff",
            "Non-claim checklist (no prescription / no compounding / no guaranteed dose / no device CE-FDA claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "delivery", "status_timeline"],
        tags=["aeterna", "transdermal", "needle-free", "aesthetic", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-m-receptor-subscription",
        title="AETERNA M-Receptor Delivery Subscription",
        category="AETERNA",
        summary=(
            "Licensed-clinic subscription for multimodal M-receptor delivery and neuromodulation literacy "
            "(patch, iontophoresis, inhaler, vagus-adjacent stimulation) — 12,000 ACP / month."
        ),
        description=(
            "Settles the first subscription period (12,000 ACP monthly; 32,000 quarterly; 108,000 annual) "
            "and issues a licensed-clinic partner brief for a conceptual multimodal system: transdermal patch, "
            "iontophoretic wrist module, inhaler/nebulizer, and vagus-adjacent neurostimulation. Infographic "
            "M1–M5 tables and scopolamine callouts are receptor literacy, not a dosing guide and not compounding. "
            "ANCAP does not manufacture the cart, does not compound or dispense muscarinic agonists/antagonists, "
            "and does not claim CE/FDA device status or treatment of Parkinson, asthma, COPD, arrhythmia, or "
            "intraocular pressure. Physical modules are used only under a licensed clinician after screening. "
            "Renewal is a subscription retainer — not hardware title and not a guaranteed clinical outcome."
        ),
        price=Money(amount="12000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=35,
        preview_items=[
            "Contraindication / lawful-substance intake",
            "Module match (patch / iontophoresis / inhaler / neuromodulation)",
            "Subscription period pack",
        ],
        output_items=[
            "M-receptor subscription intake brief",
            "Licensed clinic handoff",
            "Non-claim checklist (no compounding / no scopolamine recipe / no treatment claim / no device CE-FDA)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "billing", "modules", "status_timeline"],
        tags=["aeterna", "m-receptor", "subscription", "neuromodulation", "consult"],
        billing="subscription",
        subscription_price_monthly=Money(amount="12000", currency="ACP"),
        subscription_price_quarterly=Money(amount="32000", currency="ACP"),
        subscription_price_annual=Money(amount="108000", currency="ACP"),
    ),
    WorkflowTemplatePublic(
        slug="aeterna-oxygen-carrier",
        title="AETERNA Artificial Oxygen Carrier",
        category="AETERNA",
        summary=(
            "Licensed bioreactor / transfusion-medicine partner brief for hemoglobin-vesicle or "
            "perfluorocarbon-emulsion oxygen-carrier architecture literacy — 92,000 ACP."
        ),
        description=(
            "Settles 92,000 ACP and issues a licensed-partner brief for a conceptual oxygen-transfer particle: "
            "hemoglobin or PFC core, lipid or polymer shell, affinity regulators, buffers, and sterile-fill "
            "literacy. Infographic production steps, QC icons, and vial diagrams are architecture literacy, "
            "not a manufacturing SOP and not compounding. ANCAP does not produce blood substitutes, does not "
            "compound hemoglobin or perfluorocarbon emulsions, and does not claim CE/FDA oxygen-therapeutic "
            "status or a transfusion outcome. Physical manufacture and any clinical use occur only under a "
            "licensed bioreactor / transfusion-medicine partner after screening."
        ),
        price=Money(amount="92000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=[
            "Core path (hemoglobin vesicle vs PFC emulsion literacy)",
            "Licensed bioreactor partner match",
            "Non-claim protocol pack",
        ],
        output_items=[
            "Oxygen-carrier intake brief",
            "Licensed bioreactor handoff",
            "Non-claim checklist (no blood product / no hemoglobin or PFC recipe / no CE-FDA / no transfusion claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "oxygen-carrier", "hboC", "pfc", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-synthetic-blood-mamba",
        title="AETERNA Synthetic Blood / Black Mamba Architecture",
        category="AETERNA",
        summary=(
            "Licensed bioreactor / transfusion-medicine partner brief for synthetic-blood architecture "
            "with modified Black Mamba peptide literacy — 98,000 ACP."
        ),
        description=(
            "Settles 98,000 ACP and issues a licensed-partner brief for a conceptual multi-layer particle: "
            "oxygen-carrier core (hemoglobin or PFC), lipid shell, polymer mesh, modified Black Mamba "
            "peptide literacy, delivery vesicle, and immune-management sensors. Infographic stages and "
            "'controlled dose' callouts are architecture literacy, not a manufacturing SOP and not a toxin "
            "or dosing recipe. ANCAP does not produce blood substitutes, does not compound venom peptides, "
            "hemoglobin or perfluorocarbon emulsions, and does not claim CE/FDA therapeutic status. Physical "
            "manufacture and any clinical use occur only under a licensed bioreactor / transfusion-medicine "
            "partner after screening."
        ),
        price=Money(amount="98000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=[
            "Layer map (core / shell / mesh / peptide literacy)",
            "Licensed bioreactor partner match",
            "Non-claim protocol pack",
        ],
        output_items=[
            "Synthetic-blood / Black Mamba architecture intake brief",
            "Licensed bioreactor handoff",
            "Non-claim checklist (no blood product / no venom or HBOC-PFC recipe / no CE-FDA / no toxin SOP)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "synthetic-blood", "black-mamba", "hboC", "pfc", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-adhd-support",
        title="AETERNA ADHD / СДВГ Support Brief",
        category="AETERNA",
        summary=(
            "Licensed clinician partner brief for ADHD / СДВГ support literacy "
            "(attention, planning, emotion, school adaptation) — 42,000 ACP."
        ),
        description=(
            "Settles 42,000 ACP and issues a licensed-partner brief covering ADHD / СДВГ support "
            "literacy: attention and task completion, planning and impulse control, emotion regulation, "
            "peer skills, self-esteem, and comorbid-risk literacy. Infographic 'path to a billion' steps "
            "are motivational architecture, not a guaranteed academic or financial outcome. ANCAP does "
            "not diagnose ADHD, does not prescribe stimulants or other drugs, does not compound "
            "medications, and does not claim CE/FDA drug status. Clinical care occurs only under a "
            "licensed clinician after screening; caregivers retain decision rights with that clinician."
        ),
        price=Money(amount="42000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=[
            "Support theme map (attention / planning / emotion / school)",
            "Licensed clinician partner match",
            "Non-claim protocol pack",
        ],
        output_items=[
            "ADHD / СДВГ support intake brief",
            "Licensed clinician handoff",
            "Non-claim checklist (no diagnosis / no prescription / no stimulant recipe / no billionaire promise)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "adhd", "sdvg", "clinician", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-aurea-vita",
        title="AUREA Vita — quality of life & longevity brief",
        category="AETERNA",
        summary=(
            "Licensed lifestyle / longevity partner brief for rapid quality-of-life literacy: "
            "nutrition, sport, health, and longevity recommendations — 40 ACP."
        ),
        description=(
            "Settles 40 ACP and issues a licensed lifestyle / longevity / nutrition-sport partner brief "
            "for quality-of-life acceleration literacy: nutrition recommendations, sport and movement, "
            "everyday health hygiene, sleep and recovery, and longevity framing. ANCAP does not diagnose, "
            "does not prescribe, does not sell drugs or medical devices, and does not guarantee lifespan, "
            "weight, athletic, or clinical outcomes. Physical coaching or clinical care occurs only under "
            "a licensed partner after screening; the client retains decision rights with that partner."
        ),
        price=Money(amount="40", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=20,
        preview_items=[
            "Theme map (nutrition / sport / health / longevity)",
            "Licensed lifestyle partner match",
            "Non-claim protocol pack",
        ],
        output_items=[
            "AUREA Vita quality-of-life intake brief",
            "Licensed partner handoff",
            "Non-claim checklist (no diagnosis / no prescription / no lifespan guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "aurea-vita", "longevity", "nutrition", "sport", "health", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-down-syndrome-support",
        title="AETERNA Down Syndrome Support Brief",
        category="AETERNA",
        summary=(
            "Licensed developmental pediatrics / genetics partner brief for Down syndrome "
            "support literacy — 42,000 ACP. Not a cure."
        ),
        description=(
            "Settles 42,000 ACP and issues a licensed-partner brief covering Down syndrome support "
            "literacy: early intervention, family caregiver coordination, learning and skills "
            "adaptation, health-partner screening, and community peer-support literacy. ANCAP does "
            "not cure Down syndrome, does not diagnose trisomy 21, does not sell gene therapy or CRISPR, "
            "does not prescribe medications, and does not claim guaranteed developmental outcomes. "
            "Clinical care occurs only under a licensed clinician after screening; caregivers retain "
            "decision rights with that clinician."
        ),
        price=Money(amount="42000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=[
            "Support theme map (early intervention / family / learning)",
            "Licensed clinician partner match",
            "Non-claim protocol pack",
        ],
        output_items=[
            "Down syndrome support intake brief",
            "Licensed clinician handoff",
            "Non-claim checklist (no cure / no diagnosis / no gene therapy sold by ANCAP / no outcome guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "down-syndrome", "trisomy-21", "clinician", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-substance-coding",
        title="AETERNA Substance Coding Support Brief",
        category="AETERNA",
        summary=(
            "Licensed addiction-medicine / narcology / clinical-hypnosis partner brief for coding "
            "literacy (light, clinic-only substances, hypnosis) aimed at non-essential psychoactive "
            "dependence — 48,000 ACP. Not a coding session by ANCAP."
        ),
        description=(
            "Settles 48,000 ACP and issues a licensed-partner brief covering substance-coding support "
            "literacy: light-protocol themes, clinic-only substance protocol literacy, and clinical "
            "hypnosis literacy for psychoactive substances that are not necessary for life. ANCAP does "
            "not perform coding, does not guarantee abstinence, does not compound or sell controlled "
            "substances, does not sell hypnosis as entertainment, and does not replace emergency or "
            "psychiatric care. Clinical care occurs only under a licensed clinician after screening."
        ),
        price=Money(amount="48000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=[
            "Modality map (light / clinic substances / hypnosis literacy)",
            "Licensed clinician partner match",
            "Non-claim protocol pack",
        ],
        output_items=[
            "Substance-coding support intake brief",
            "Licensed clinician handoff",
            "Non-claim checklist (no ANCAP coding session / no abstinence guarantee / no controlled-substance sale)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "substance-coding", "narcology", "hypnosis", "clinician", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-pulmopure-subscription",
        title="AETERNA PulmoPure Lung-Care Subscription",
        category="AETERNA",
        summary=(
            "Licensed pulmonology / respiratory clinic subscription for PulmoPure gas-vibration and "
            "lavender-oil architecture literacy — 14,000 ACP / month."
        ),
        description=(
            "Settles the first subscription period (14,000 ACP monthly; 38,000 quarterly; 128,000 annual) "
            "and issues a licensed-clinic partner brief for a conceptual handheld lung-care system: silicone "
            "mouthpiece, gas-vibration generator, medical-gas mix literacy, lavender-oil atomizer, filter/"
            "cleaning unit, and Soft / Standard / Intensive mode literacy. Infographic before/after alveoli "
            "and 'clean lungs' slogans are protocol literacy, not a guaranteed clinical outcome. ANCAP does "
            "not manufacture PulmoPure, does not compound medical gases or ozone, does not sell a CE/FDA "
            "device, and does not claim tar clearance, cough cure, or safe home ozone inhalation. Physical "
            "sessions occur only under a licensed clinician after screening. Renewal is a subscription "
            "retainer — not hardware title."
        ),
        price=Money(amount="14000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=35,
        preview_items=[
            "Respiratory contraindication intake",
            "Mode match (Soft / Standard / Intensive literacy)",
            "Subscription period pack",
        ],
        output_items=[
            "PulmoPure subscription intake brief",
            "Licensed pulmonology / respiratory clinic handoff",
            "Non-claim checklist (no ozone therapy / no gas compounding / no CE-FDA / no clean-lungs guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "billing", "modules", "status_timeline"],
        tags=["aeterna", "pulmopure", "subscription", "pulmonology", "consult"],
        billing="subscription",
        subscription_price_monthly=Money(amount="14000", currency="ACP"),
        subscription_price_quarterly=Money(amount="38000", currency="ACP"),
        subscription_price_annual=Money(amount="128000", currency="ACP"),
    ),
    WorkflowTemplatePublic(
        slug="aeterna-installation-project",
        title="AETERNA Installation Project (Neonatal Nutrition + Hyperbaric)",
        category="AETERNA",
        summary=(
            "Licensed neonatology / infant-nutrition partner brief for high-protein milk-line and "
            "neonatal hyperbaric-chamber literacy — 72,000 ACP."
        ),
        description=(
            "Settles 72,000 ACP and issues a licensed-partner brief for Installation Project "
            "(Проект Установки): high-protein natural-synthetic infant milk production literacy "
            "(conceptual ~1,000 L/day; liquid and dry formats; GMP / medical-standards framing) and "
            "neonatal hyperbaric-chamber architecture literacy (1.5–2.0 ATA; 36–37 °C; 1–2 newborns; "
            "vitals monitoring). ANCAP does not manufacture infant formula, does not operate a dairy "
            "plant or NICU, does not sell a CE/FDA hyperbaric device, and does not claim guaranteed "
            "reduction of rickets, anemia, infection, or developmental delay. Physical production and "
            "clinical sessions remain with licensed partners after screening."
        ),
        price=Money(amount="72000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=[
            "Milk-line + hyperbaric theme map",
            "Licensed partner match",
            "Non-claim / GMP literacy pack",
        ],
        output_items=[
            "Installation Project intake brief",
            "Licensed neonatology / nutrition partner handoff",
            "Non-claim checklist (no formula sale / no home HBO / no CE-FDA claim / no guaranteed outcome)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "architecture", "status_timeline"],
        tags=["aeterna", "installation-project", "neonatal", "infant-nutrition", "hyperbaric", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="aeterna-dna-pheromone-perfume",
        title="AETERNA DNA-Matched Pheromone Perfume (1 Bottle)",
        category="AETERNA",
        summary=(
            "Licensed cosmetic / fragrance partner fill for a DNA-vault–informed pheromone perfume — "
            "sold per bottle at 8,900 ACP."
        ),
        description=(
            "Settles 8,900 ACP for exactly one bottle and issues a licensed cosmetic / fragrance partner "
            "handoff. An optional DNA-vault content hash may inform olfactory-profile literacy; genome bytes "
            "are never uploaded to ANCAP. Not a drug, not an aphrodisiac medical claim, not a guaranteed "
            "attraction or relationship outcome, not CE/FDA pheromone medicine, and not compounding of "
            "controlled substances. Physical bottle fill and labeling remain with the licensed partner."
        ),
        price=Money(amount="8900", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=30,
        preview_items=[
            "Vault-hash olfactory profile literacy (optional)",
            "Pheromone fragrance blend theme map",
            "1-bottle partner fill pack",
        ],
        output_items=[
            "DNA-matched perfume bottle intake brief",
            "Licensed cosmetic / fragrance partner handoff",
            "Non-claim checklist (no drug claim / no aphrodisiac guarantee / no CE-FDA / no genome upload)",
            "Proof receipt (qty = 1 bottle)",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "intent_kind", "unit", "quantity", "architecture", "status_timeline"],
        tags=["aeterna", "perfume", "pheromone", "dna", "cosmetic", "bottle"],
    ),
    WorkflowTemplatePublic(
        slug="counsel-jurisdiction-match",
        title="Worldwide Legal Counsel — Jurisdiction Match",
        category="Counsel",
        summary="Match licensed counsel in any covered country — from 3,900 ACP.",
        description=(
            "Settles ACP for a worldwide jurisdiction-match brief and licensed-counsel shortlist "
            "handoff. ANCAP is not a law firm, does not practice law, and does not form an "
            "attorney–client relationship. Local counsel remain independent."
        ),
        price=Money(amount="3900", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=35,
        preview_items=["Jurisdiction intake", "Licensed counsel shortlist", "Non-advice checklist"],
        output_items=[
            "Jurisdiction match brief",
            "Licensed counsel handoff pack",
            "Non-claim checklist (no law practice / no attorney–client with ANCAP / no outcome guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "jurisdiction", "status_timeline"],
        tags=["counsel", "legal", "jurisdiction", "worldwide", "handoff"],
    ),
    WorkflowTemplatePublic(
        slug="counsel-entity-setup",
        title="Worldwide Legal Counsel — Entity / Incorporation Brief",
        category="Counsel",
        summary="Entity setup intake + licensed local counsel handoff — from 8,900 ACP.",
        description=(
            "Settles ACP for an incorporation / entity-setup intake brief and licensed local "
            "counsel handoff anywhere covered by the desk. Not a ready-made company sold by ANCAP."
        ),
        price=Money(amount="8900", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=["Entity goals intake", "Jurisdiction options literacy", "Counsel handoff"],
        output_items=[
            "Entity setup intake brief",
            "Licensed counsel handoff",
            "Non-claim checklist",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "jurisdiction", "status_timeline"],
        tags=["counsel", "legal", "incorporation", "entity", "worldwide"],
    ),
    WorkflowTemplatePublic(
        slug="counsel-contract-review",
        title="Worldwide Legal Counsel — Contract Review Brief",
        category="Counsel",
        summary="Contract intake + licensed counsel review handoff — from 4,500 ACP.",
        description=(
            "Settles ACP for a structured contract-review intake and licensed-counsel handoff. "
            "ANCAP does not redline as your attorney."
        ),
        price=Money(amount="4500", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=["Contract intake checklist", "Risk theme map", "Counsel handoff"],
        output_items=[
            "Contract review intake brief",
            "Licensed counsel handoff",
            "Non-claim checklist",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["counsel", "legal", "contract", "review", "worldwide"],
    ),
    WorkflowTemplatePublic(
        slug="counsel-crypto-assets",
        title="Worldwide Legal Counsel — Crypto / Digital Assets Match",
        category="Counsel",
        summary="Crypto-assets counsel match for token / exchange / stablecoin rails — from 12,000 ACP.",
        description=(
            "Settles ACP for a crypto / digital-assets literacy pack and licensed counsel match. "
            "Not an investment prospectus or securities opinion from ANCAP."
        ),
        price=Money(amount="12000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Asset / activity map", "Regulatory theme literacy", "Counsel match"],
        output_items=[
            "Crypto assets counsel match brief",
            "Licensed counsel handoff",
            "Non-claim checklist",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "jurisdiction", "status_timeline"],
        tags=["counsel", "legal", "crypto", "digital-assets", "worldwide"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-install-intake",
        title="Starlink Installation — Standard Intake (NRW / DE)",
        category="StarlinkInstall",
        summary="Pay for real-world Starlink installation coordination — €153 catalog face (live ACP).",
        description=(
            "Settles ACP/wACP for a Starlink installation intake on ancap.cloud (Germany / NRW first). "
            "Catalog face €153 = €150 install + €3 platform fee (EUR≈USD sticker → live ACP via oracle). "
            "ANCAP is not an official Starlink reseller or Telekom. Mounting is performed by an "
            "independently qualified partner. Not a Jobcenter / AVGS funding guarantee."
        ),
        price=Money(amount="153", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["Site / region intake", "Partner match (NRW / DE)", "Escrow reserve"],
        output_items=[
            "Installation intake brief",
            "Verified installer handoff",
            "Non-claim checklist (no Starlink Inc. employment / no Baugenehmigung included / no AVGS promise)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "region_hint", "service_id", "status_timeline"],
        tags=["starlink", "field-service", "nrw", "germany", "installation"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-standard",
        title="Starlink Installation — Standard",
        category="StarlinkInstall",
        summary="Residential Starlink install coordination — €153 catalog face.",
        description=(
            "Residential kit mount intake with ACP/wACP escrow. Hardware sold separately by Starlink. "
            "Partner performs the mount; ANCAP coordinates payment."
        ),
        price=Money(amount="153", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["Residential site intake", "Partner schedule", "Escrow reserve"],
        output_items=["Install intake brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "region_hint", "status_timeline"],
        tags=["starlink", "field-service", "nrw", "residential"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-roof",
        title="Starlink Installation — Roof / Wall Mount",
        category="StarlinkInstall",
        summary="Roof or facade mount coordination — €203 catalog face.",
        description="Elevated mount intake. Building permits and roof safety remain with customer/partner.",
        price=Money(amount="203", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=120,
        preview_items=["Mount type intake", "Safety protocol note", "Escrow reserve"],
        output_items=["Roof mount intake brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["starlink", "field-service", "roof", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-business",
        title="Starlink Installation — Business",
        category="StarlinkInstall",
        summary="SME / site install coordination — €303 catalog face.",
        description="Business-site install intake with documented partner handoff. Complex sites may need follow-on quote.",
        price=Money(amount="303", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=150,
        preview_items=["Business site intake", "Partner match", "Escrow reserve"],
        output_items=["Business install brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["starlink", "field-service", "business", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-network",
        title="Starlink Installation — Network / Wi-Fi",
        category="StarlinkInstall",
        summary="Network and Wi-Fi configuration visit — €53 catalog face.",
        description="Router / Wi-Fi setup after the dish is online. Not an ISP contract sold by ANCAP.",
        price=Money(amount="53", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=45,
        preview_items=["LAN / Wi-Fi intake", "Partner visit", "Escrow reserve"],
        output_items=["Network config brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["starlink", "field-service", "network", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-mobile",
        title="Starlink Installation — Mobile / RV",
        category="StarlinkInstall",
        summary="Mobile / RV mount coordination — €183 catalog face.",
        description="Vehicle / RV mount intake where local rules allow.",
        price=Money(amount="183", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=100,
        preview_items=["Vehicle type intake", "Partner match", "Escrow reserve"],
        output_items=["Mobile install brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["starlink", "field-service", "mobile", "rv"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-relocate",
        title="Starlink Installation — Relocation",
        category="StarlinkInstall",
        summary="Relocation / reinstallation — €178 catalog face.",
        description="Move an existing kit and re-aim at a new site.",
        price=Money(amount="178", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=100,
        preview_items=["Old / new site intake", "Partner schedule", "Escrow reserve"],
        output_items=["Relocation brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["starlink", "field-service", "relocation"],
    ),
    WorkflowTemplatePublic(
        slug="starlink-troubleshoot",
        title="Starlink Installation — Troubleshooting",
        category="StarlinkInstall",
        summary="Troubleshooting & optimization visit — €83 catalog face.",
        description="Obstruction, cable, and performance troubleshooting visit.",
        price=Money(amount="83", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=60,
        preview_items=["Issue intake", "Partner visit", "Escrow reserve"],
        output_items=["Troubleshoot brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["starlink", "field-service", "troubleshoot"],
    ),
    WorkflowTemplatePublic(
        slug="it-pc-setup",
        title="Field services — PC / laptop setup",
        category="FieldServices",
        summary="OS install, transfer, and basic device setup — €123 catalog face.",
        description=(
            "Settles ACP/wACP for PC / laptop setup coordination (Germany / NRW first). "
            "Catalog face €123 = €120 labor + €3 platform fee. ANCAP is not an equipment reseller; "
            "partner performs the visit. Not a Jobcenter / AVGS funding guarantee."
        ),
        price=Money(amount="123", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["Device intake", "Partner match (NRW / DE)", "Escrow reserve"],
        output_items=["Setup intake brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "region_hint", "service_id", "status_timeline"],
        tags=["field-services", "it", "pc", "nrw", "germany"],
    ),
    WorkflowTemplatePublic(
        slug="it-device-repair",
        title="Field services — Device upgrade / repair visit",
        category="FieldServices",
        summary="Hardware upgrade or repair coordination — €93 catalog face.",
        description=(
            "Parts are not included unless quoted separately. Partner performs the visit; "
            "ANCAP coordinates payment. Catalog face €93 = €90 + €3 fee."
        ),
        price=Money(amount="93", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=75,
        preview_items=["Fault / upgrade intake", "Partner visit", "Escrow reserve"],
        output_items=["Repair intake brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "it", "repair", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="it-network-home",
        title="Field services — Home / small-office network",
        category="FieldServices",
        summary="Router / Wi-Fi / LAN setup visit — €83 catalog face.",
        description="Not an ISP contract sold by ANCAP. Catalog face €83 = €80 + €3 fee.",
        price=Money(amount="83", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=60,
        preview_items=["LAN / Wi-Fi intake", "Partner visit", "Escrow reserve"],
        output_items=["Network brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "it", "network", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="it-maintenance-visit",
        title="Field services — IT maintenance visit",
        category="FieldServices",
        summary="On-site IT maintenance / cleanup — €73 catalog face.",
        description="Catalog face €73 = €70 + €3 fee. Partner performs the visit.",
        price=Money(amount="73", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Maintenance intake", "Partner visit", "Escrow reserve"],
        output_items=["Maintenance brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "it", "maintenance", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="cam-cctv-install",
        title="Field services — CCTV camera install",
        category="FieldServices",
        summary="Camera mounting and basic wiring coordination — €183 catalog face.",
        description=(
            "Hardware sold separately. Electrical / height work remains with customer and partner. "
            "Catalog face €183 = €180 + €3 fee. Not an equipment reseller claim."
        ),
        price=Money(amount="183", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=120,
        preview_items=["Site / camera count intake", "Partner match", "Escrow reserve"],
        output_items=["CCTV install brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "cameras", "cctv", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="cam-nvr-config",
        title="Field services — NVR / recorder configuration",
        category="FieldServices",
        summary="NVR setup, remote access, retention basics — €103 catalog face.",
        description="Catalog face €103 = €100 + €3 fee. Not a surveillance monitoring subscription.",
        price=Money(amount="103", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=70,
        preview_items=["NVR brand / channel intake", "Partner visit", "Escrow reserve"],
        output_items=["NVR config brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "cameras", "nvr", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="cam-maintenance",
        title="Field services — CCTV maintenance",
        category="FieldServices",
        summary="Camera system check and cleaning visit — €78 catalog face.",
        description="Catalog face €78 = €75 + €3 fee.",
        price=Money(amount="78", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=55,
        preview_items=["Issue intake", "Partner visit", "Escrow reserve"],
        output_items=["Maintenance brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "cameras", "maintenance", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="solar-balcony-install",
        title="Field services — Balcony PV mount coordination",
        category="FieldServices",
        summary="Balcony solar panel mount literacy + partner coordination — €253 catalog face.",
        description=(
            "Catalog face €253 = €250 + €3 fee. ANCAP does not sell PV hardware and is not a "
            "grid-operator. Electrical connection and permits remain with licensed partners / customer. "
            "Partner literacy / install coordination only — not a yield guarantee."
        ),
        price=Money(amount="253", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=150,
        preview_items=["Balcony / kit intake", "Partner match", "Escrow reserve"],
        output_items=["Balcony PV brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "solar", "balcony", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="solar-panel-service",
        title="Field services — Solar panel service visit",
        category="FieldServices",
        summary="PV inspection / cleaning / troubleshooting coordination — €123 catalog face.",
        description="Catalog face €123 = €120 + €3 fee. Roof / height safety remains with partner.",
        price=Money(amount="123", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=90,
        preview_items=["Service intake", "Partner visit", "Escrow reserve"],
        output_items=["Solar service brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "solar", "service", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="panel-other-mount",
        title="Field services — Other panel mount coordination",
        category="FieldServices",
        summary="Non-PV / specialty panel mount literacy + partner — €153 catalog face.",
        description=(
            "Catalog face €153 = €150 + €3 fee. Covers coordination literacy for other panel types "
            "(e.g. thermal, specialty mounts) via partner — not equipment sales by ANCAP."
        ),
        price=Money(amount="153", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=100,
        preview_items=["Panel type intake", "Partner match", "Escrow reserve"],
        output_items=["Panel mount brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "panels", "mount", "nrw"],
    ),
    WorkflowTemplatePublic(
        slug="space-ai-orbit-intake",
        title="Field services — Orbital AI data-center placement (LEO / MEO)",
        category="FieldServices",
        summary="Orbit AI data-center placement coordination literacy — €12,003 catalog face.",
        description=(
            "Settles ACP/wACP for LEO / MEO AI compute / data-center placement coordination "
            "(catalog face €12,003 = €12,000 + €3 platform fee). ANCAP is not a launch provider, "
            "not SpaceX, and does not grant orbital slots or spectrum. Licensed partners perform "
            "any physical / regulatory work. Not an AGI/ASI-in-space claim."
        ),
        price=Money(amount="12003", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=180,
        preview_items=["Orbit class intake (LEO/MEO)", "Partner match", "Escrow reserve"],
        output_items=[
            "Orbital AI DC intake brief",
            "Partner handoff",
            "Non-claim checklist (no launch ticket / no slot grant / no AGI guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "region_hint", "service_id", "status_timeline"],
        tags=["field-services", "space", "orbital", "ai-datacenter", "leo"],
    ),
    WorkflowTemplatePublic(
        slug="space-ai-beyond-orbit",
        title="Field services — Beyond-orbit AI data-center placement",
        category="FieldServices",
        summary="GEO / cislunar / deep-space AI DC coordination literacy — €28,003 catalog face.",
        description=(
            "Catalog face €28,003 = €28,000 + €3 fee. Partner literacy for beyond-LEO AI data-center "
            "concepts. Export controls, spectrum, and launch manifests remain with licensed partners "
            "and the customer. Not a lunar land deed or Outer Space Treaty sovereignty claim."
        ),
        price=Money(amount="28003", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=210,
        preview_items=["Beyond-orbit class intake", "Partner match", "Escrow reserve"],
        output_items=["Beyond-orbit AI DC brief", "Partner handoff", "Non-claim checklist", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "space", "cislunar", "ai-datacenter"],
    ),
    WorkflowTemplatePublic(
        slug="space-ai-superintel-architecture",
        title="Field services — Orbital superintelligence architecture brief",
        category="FieldServices",
        summary="Sealed orbital / beyond-orbit superintelligence architecture literacy — €48,003 catalog face.",
        description=(
            "Catalog face €48,003 = €48,000 + €3 fee. High-assurance partner brief for sealed orbital "
            "edge / HSM control-plane themes framed as 'superintelligence' hosting literacy. "
            "ANCAP does not claim to operate AGI or ASI in space today."
        ),
        price=Money(amount="48003", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=240,
        preview_items=["Threat / assurance intake", "Partner match", "Escrow reserve"],
        output_items=[
            "Superintelligence orbital architecture brief",
            "Partner handoff",
            "Non-claim checklist (no AGI/ASI operation claim)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "status_timeline"],
        tags=["field-services", "space", "superintelligence", "orbital-edge"],
    ),

    WorkflowTemplatePublic(
        slug="stardust-extreme-weather-monitor",
        title="Stardust Extreme Weather Worldwide Monitor",
        category="StardustSRT",
        summary="Licensed partner brief for worldwide hurricane / storm / rainfall monitoring literacy — 18,000 ACP.",
        description=(
            "Settles 18,000 ACP and issues a licensed-partner brief for extreme-weather monitoring "
            "literacy worldwide. Not an official meteorological warning, not AccuWeather replacement, "
            "and not a storm-track guarantee. ANCAP is not affiliated with StardustSRT unless separately contracted."
        ),
        price=Money(amount="18000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=35,
        preview_items=["Region / hazard map", "Licensed partner match", "Non-claim pack"],
        output_items=[
            "Extreme weather monitor intake brief",
            "Licensed partner handoff",
            "Non-claim checklist (no official warning / no track guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "region_hint", "status_timeline"],
        tags=["stardust", "weather", "monitoring", "disaster", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="stardust-disaster-early-warning",
        title="Stardust Disaster Early-Warning Coordination",
        category="StardustSRT",
        summary="Seismic / tsunami / volcano / flood early-alert coordination literacy — 28,000 ACP.",
        description=(
            "Settles 28,000 ACP and issues a licensed-partner brief for multi-hazard early-warning "
            "coordination literacy. Not a government emergency system and not a guaranteed early alert."
        ),
        price=Money(amount="28000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=["Hazard theme map", "Alert audience literacy", "Partner match"],
        output_items=[
            "Disaster early-warning intake brief",
            "Licensed partner handoff",
            "Non-claim checklist (no government SOPs / no alert guarantee)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "hazard_themes", "status_timeline"],
        tags=["stardust", "disaster", "seismic", "tsunami", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="stardust-weather-control-global",
        title="Stardust Global Weather-Control Partner Brief",
        category="StardustSRT",
        summary=(
            "Worldwide weather-control architecture literacy (rainfall, storm dissipation, "
            "temperature, snow) — 58,000 ACP."
        ),
        description=(
            "Settles 58,000 ACP and issues a licensed-partner brief for global weather-control "
            "architecture literacy. UI toggles and satellite artwork are product literacy — not a "
            "live geoengineering console, not unilateral weather modification by ANCAP, and not a "
            "guaranteed rainfall or storm-dissipation outcome. Partner screening required under "
            "applicable environmental law."
        ),
        price=Money(amount="58000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=50,
        preview_items=["Control theme map", "Worldwide region desk", "Non-claim / partner pack"],
        output_items=[
            "Global weather-control intake brief",
            "Licensed partner handoff",
            "Non-claim checklist (no geoengineering console / no guaranteed weather outcome)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "control_modules", "status_timeline"],
        tags=["stardust", "weather-control", "geoengineering-literacy", "consult"],
    ),
    WorkflowTemplatePublic(
        slug="stardust-weather-control-subscription",
        title="Stardust Worldwide Weather-Control Subscription",
        category="StardustSRT",
        summary="Monthly ACP retainer for worldwide weather-control / earth-monitoring partner literacy — 45,000 ACP / month.",
        description=(
            "Settles 45,000 ACP per month and issues an ongoing licensed-partner coordination brief "
            "for worldwide weather-control and earth-monitoring literacy. Not a live weather remote "
            "control and not a guaranteed climate outcome."
        ),
        price=Money(amount="45000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=30,
        preview_items=["Monthly coordination brief", "Partner desk", "Non-claim pack"],
        output_items=[
            "Weather-control subscription period brief",
            "Licensed partner handoff",
            "Non-claim checklist",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "billing", "status_timeline"],
        tags=["stardust", "weather-control", "subscription", "consult"],
        billing="subscription",
        subscription_price_monthly=Money(amount="45000", currency="ACP"),
        subscription_price_quarterly=Money(amount="120000", currency="ACP"),
        subscription_price_annual=Money(amount="420000", currency="ACP"),
    ),

    WorkflowTemplatePublic(
        slug="market-direction-brief",
        title="Market Direction Brief",
        category="Markets",
        summary="LLM scenario analysis of near-term market direction, catalysts, and risk-of-upside / downside paths.",
        description="Uses large-model reasoning over user-supplied market context to outline bullish/base/bearish scenarios, key levels, and what would invalidate the thesis. Educational analysis only — not investment advice.",
        price=Money(amount="25", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=25,
        preview_items=["Direction scenarios", "Catalyst map", "Invalidation levels"],
        output_items=["Scenario brief", "Catalyst checklist", "Watchlist levels", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "status_timeline"],
        tags=["markets", "prediction", "ai", "analysis"],
    ),
    WorkflowTemplatePublic(
        slug="commodity-price-outlook",
        title="Commodity Price Outlook",
        category="Markets",
        summary="AI outlook for oil, gas, metals, timber, uranium, and other commodities — supply, demand, and quote momentum.",
        description="Builds a structured commodity outlook from user context (asset, region, horizon) with supply/demand drivers, quote-move scenarios, and desk-relevant risks. Not a guaranteed price forecast.",
        price=Money(amount="29", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=30,
        preview_items=["Supply/demand map", "Quote scenarios", "Desk risk notes"],
        output_items=["Commodity outlook", "Driver matrix", "Scenario paths", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "asset_reference", "status_timeline"],
        tags=["commodities", "oil", "gas", "uranium", "markets", "ai"],
    ),
    WorkflowTemplatePublic(
        slug="crypto-quote-momentum-scan",
        title="Crypto Quote Momentum Scan",
        category="Markets",
        summary="AI scan of crypto quote momentum, narrative heat, and upside/downside path probabilities from your inputs.",
        description="Produces a momentum and narrative scan for a token or market: relative strength framing, catalyst calendar, and scenario weights. Explicitly not trading signals or return promises.",
        price=Money(amount="22", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=20,
        preview_items=["Momentum framing", "Narrative heat", "Path weights"],
        output_items=["Momentum scan", "Narrative map", "Scenario weights", "Receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "asset_reference", "status_timeline"],
        tags=["crypto", "momentum", "quotes", "markets", "ai"],
    ),
    WorkflowTemplatePublic(
        slug="markets-ai-radar-pro",
        title="Markets AI Radar Pro",
        category="Markets",
        summary="Pro multi-asset radar: crypto + commodities quote paths, cross-asset contagion, and AI-ranked growth scenarios.",
        description="Premium multi-horizon radar combining user market notes with structured AI scenario ranking across assets. Includes monitoring checklist and evidence gaps. Not financial advice.",
        price=Money(amount="79", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=55,
        preview_items=["Cross-asset radar", "Ranked scenarios", "Monitoring checklist"],
        output_items=["Radar brief", "Ranked scenarios", "Contagion notes", "Evidence gaps", "Proof receipt"],
        receipt_items=["workflow_slug", "price_snapshot", "input_hash", "margin_snapshot", "status_timeline"],
        tags=["markets", "pro", "commodities", "crypto", "prediction", "ai"],
    ),
    WorkflowTemplatePublic(
        slug="entertainment-tesla-coil-party",
        title="Tesla Coil Party Desk Brief",
        category="Entertainment",
        summary=(
            "Licensed venue partner brief for a Tesla-coil spectacle party with complimentary "
            "Jack Daniel's hospitality literacy and jurisdiction-permitted adult substances only — 8,900 ACP."
        ),
        description=(
            "Settles 8,900 ACP and issues a licensed entertainment-venue partner brief for a Tesla-coil "
            "show party. Complimentary whiskey hospitality is framed as Jack Daniel's brand literacy where "
            "the venue holds a liquor licence — ANCAP is not affiliated with Jack Daniel's or Brown-Forman "
            "and does not hold a liquor licence. Age/ID gates (18+/21+ by jurisdiction) apply. "
            "Jurisdiction-permitted adult substances means only substances lawful for adults in the event "
            "locale under venue rules — ANCAP does not sell alcohol, cannabis, or controlled substances. "
            "High-voltage Tesla coil operation is venue-partner electrical safety literacy only — not a DIY "
            "coil kit and not a guaranteed show outcome."
        ),
        price=Money(amount="8900", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=30,
        preview_items=[
            "Venue / HV safety literacy map",
            "Age-gate + hospitality compliance pack",
            "Partner handoff checklist",
        ],
        output_items=[
            "Tesla coil party intake brief",
            "Licensed venue partner handoff",
            "Non-claim checklist (no Jack Daniel's affiliation / no ANCAP liquor licence / no controlled-substance sale / no DIY HV kit)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "architecture", "status_timeline"],
        tags=["entertainment", "tesla-coil", "party", "hospitality", "age-gated"],
    ),
    WorkflowTemplatePublic(
        slug="antique-fire-restore",
        title="Antique Fire Restore Desk Brief",
        category="Conservation",
        summary=(
            "Licensed conservation / metallurgy partner brief for antique restoration after "
            "total fire using reverse-combustion literacy — 42,000 ACP."
        ),
        description=(
            "Settles 42,000 ACP and issues a licensed conservation / metallurgy partner brief. "
            "Reverse-combustion and reduction chemistry themes are partner literacy only — not a "
            "DIY furnace kit. The six-stage recovery map is a conservation protocol analogy for "
            "artifacts — not medical burn care. ANCAP does not guarantee authenticity or original "
            "finish and does not pay insurance claims for fire loss."
        ),
        price=Money(amount="42000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        estimated_time_minutes=40,
        preview_items=[
            "Reverse-combustion / metallurgy literacy map",
            "Six-stage conservation protocol analogy",
            "Partner handoff checklist",
        ],
        output_items=[
            "Antique fire-restore intake brief",
            "Licensed conservation / metallurgy partner handoff",
            "Non-claim checklist (no DIY furnace / no medical burn care / no authenticity guarantee / no ANCAP insurance payout)",
            "Proof receipt",
        ],
        receipt_items=["workflow_slug", "price_snapshot", "architecture", "status_timeline"],
        tags=["conservation", "antique", "fire-restore", "metallurgy", "reverse-combustion"],
    ),

]


WORKFLOW_BUNDLES: list[WorkflowBundlePublic] = [
    WorkflowBundlePublic(
        slug="launch-pack",
        title="ANCAP Crypto Launch Pack",
        category="Launch Suite",
        summary="Five paid crypto launch workflows sold together as a higher-ticket execution bundle.",
        description="Creates listing copy, launch campaign plan, Telegram operating kit, bounty structure, and token risk snapshot in one checkout.",
        workflow_slugs=[
            "token-listing-pack",
            "crypto-campaign-builder",
            "telegram-growth-kit",
            "airdrop-bounty-builder",
            "token-risk-report",
        ],
        price=Money(amount="49", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=30,
        estimated_time_minutes=125,
        output_items=[
            "Listing pack",
            "Campaign plan",
            "Telegram growth kit",
            "Airdrop / bounty structure",
            "Token risk report",
            "Five proof-backed workflow receipts",
        ],
        tags=["bundle", "launch", "growth", "risk"],
    ),
    WorkflowBundlePublic(
        slug="growth-pack",
        title="ANCAP Growth Pack",
        category="Growth Suite",
        summary="Repeatable campaign and community workflows for teams that iterate every week.",
        description="Creates two campaign plans, two Telegram operating passes, and one bounty structure for recurring growth execution.",
        workflow_slugs=[
            "crypto-campaign-builder",
            "telegram-growth-kit",
            "airdrop-bounty-builder",
            "crypto-campaign-builder",
            "telegram-growth-kit",
        ],
        price=Money(amount="59", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=23,
        estimated_time_minutes=140,
        output_items=[
            "Two campaign plans",
            "Two Telegram growth passes",
            "Bounty task matrix",
            "Five proof-backed workflow receipts",
        ],
        tags=["bundle", "growth", "community", "campaign"],
    ),
    WorkflowBundlePublic(
        slug="concierge-pack",
        title="ANCAP Concierge Pack",
        category="Concierge",
        summary="A premium bundle for teams that want generated artifacts plus operator review.",
        description="Creates all five launch workflows and prices the run as a concierge engagement with room for manual review and delivery polish.",
        workflow_slugs=[
            "token-listing-pack",
            "crypto-campaign-builder",
            "telegram-growth-kit",
            "airdrop-bounty-builder",
            "token-risk-report",
        ],
        price=Money(amount="149", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=0,
        estimated_time_minutes=180,
        output_items=[
            "Full launch workflow set",
            "Premium review budget",
            "Custom delivery polish",
            "Five proof-backed workflow receipts",
        ],
        tags=["bundle", "concierge", "premium", "launch"],
    ),
    WorkflowBundlePublic(
        slug="pro-launch-pack",
        title="ANCAP Pro Launch Pack",
        category="Premium Launch",
        summary="Higher-ticket launch execution pack for teams that need listing, audit, KOL, bounty, and pro risk artifacts together.",
        description="Bundles the premium launch audit, exchange submission pack, KOL/Telegram campaign, bounty builder, and pro token risk report into one proof-backed checkout.",
        workflow_slugs=[
            "token-launch-audit-pack",
            "exchange-listing-submission-pack",
            "kol-telegram-campaign-builder",
            "airdrop-bounty-builder",
            "token-risk-report-pro",
        ],
        price=Money(amount="349", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=13,
        estimated_time_minutes=295,
        output_items=[
            "Launch readiness audit",
            "Exchange listing submission pack",
            "KOL / Telegram campaign kit",
            "Airdrop / bounty structure",
            "Token Risk Report Pro",
            "Five proof-backed workflow receipts",
        ],
        tags=["bundle", "launch", "premium", "risk", "growth"],
    ),
    WorkflowBundlePublic(
        slug="agent-commerce-pack",
        title="ANCAP Agent Commerce Pack",
        category="Agent Commerce",
        summary="A B2B pack for API owners and AI-agent builders who want pay-per-call monetization fast.",
        description="Combines API readiness, campaign positioning, listing copy, and proof-center setup so external agents can discover, pay, and verify ANCAP-style execution.",
        workflow_slugs=[
            "agent-api-readiness-pack",
            "crypto-campaign-builder",
            "token-listing-pack",
            "token-risk-report-pro",
        ],
        price=Money(amount="249", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=5,
        estimated_time_minutes=165,
        output_items=[
            "Agent/API paid endpoint offer",
            "x402-compatible payment terms",
            "Developer pricing matrix",
            "Proof-center receipt schema",
        ],
        tags=["bundle", "api", "x402", "agents"],
    ),
    WorkflowBundlePublic(
        slug="compliance-pack",
        title="MiCA Readiness Pack",
        category="Compliance",
        summary="Compliance and governance artifacts for EU-facing crypto teams.",
        description="Bundles MiCA-style governance readiness, token risk pro, and listing submission materials.",
        workflow_slugs=[
            "ai-iso-governance-readiness-pack",
            "token-risk-report-pro",
            "exchange-listing-submission-pack",
        ],
        price=Money(amount="199", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=8,
        estimated_time_minutes=180,
        output_items=[
            "MiCA / ISO governance checklist",
            "Token Risk Report Pro",
            "Exchange listing submission pack",
            "Three proof-backed workflow receipts",
        ],
        tags=["bundle", "compliance", "mica", "risk"],
    ),
    WorkflowBundlePublic(
        slug="growth-pro-pack",
        title="7-Day Campaign Pack",
        category="Growth",
        summary="High-ticket growth execution for launch-week campaigns.",
        description="Combines KOL/Telegram campaign builder, two campaign plans, and bounty structure for a full growth sprint.",
        workflow_slugs=[
            "kol-telegram-campaign-builder",
            "crypto-campaign-builder",
            "crypto-campaign-builder",
            "airdrop-bounty-builder",
        ],
        price=Money(amount="299", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=10,
        estimated_time_minutes=200,
        output_items=[
            "KOL / Telegram campaign kit",
            "Two campaign plans",
            "Bounty task matrix",
            "Four proof-backed workflow receipts",
        ],
        tags=["bundle", "growth", "campaign", "telegram"],
    ),
    WorkflowBundlePublic(
        slug="merchant-qr-pack",
        title="Payment QR Setup Pack",
        category="Merchant",
        summary="Merchant onboarding bundle for ANCAP Pay QR and payment links.",
        description="Agent API readiness plus listing copy and campaign positioning for merchants accepting ACP.",
        workflow_slugs=[
            "agent-api-readiness-pack",
            "token-listing-pack",
            "crypto-campaign-builder",
        ],
        price=Money(amount="79", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=0,
        estimated_time_minutes=90,
        output_items=[
            "Payment link / QR setup guide",
            "Merchant landing copy",
            "Campaign positioning brief",
            "Three proof-backed workflow receipts",
        ],
        tags=["bundle", "merchant", "pay", "qr"],
    ),
    WorkflowBundlePublic(
        slug="aeterna-longevity-pack",
        title="AETERNA Longevity Pack",
        category="AETERNA",
        summary="DNA wellness + 15-axis molecular aging profile + longevity panel for ACP checkout.",
        description=(
            "Three AETERNA consult-prep workflows for vaulted genomic / blood-RNA panel metadata. "
            "Emphasizes hallmark configuration over a single bio-age score. Licensed-partner handoff only."
        ),
        workflow_slugs=[
            "aeterna-dna-wellness-report",
            "aeterna-molecular-aging-profile",
            "aeterna-longevity-panel-brief",
        ],
        price=Money(amount="2500000", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=17,
        estimated_time_minutes=155,
        output_items=[
            "DNA wellness report",
            "Molecular aging profile (15 axes)",
            "Longevity panel brief",
            "Three proof-backed workflow receipts",
        ],
        tags=["bundle", "aeterna", "longevity", "dna", "molecular-aging"],
    ),

    WorkflowBundlePublic(
        slug="markets-intel-pack",
        title="Markets Intel Pack",
        category="Markets Suite",
        summary="Four AI market-analysis workflows: direction, commodities, crypto momentum, and pro radar.",
        description="Bundle for users who want LLM-assisted market and quote-path analysis across crypto and commodities.",
        workflow_slugs=[
            "market-direction-brief",
            "commodity-price-outlook",
            "crypto-quote-momentum-scan",
            "markets-ai-radar-pro",
        ],
        price=Money(amount="119", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        discount_percent=25,
        estimated_time_minutes=130,
        output_items=[
            "Market direction brief",
            "Commodity outlook",
            "Crypto momentum scan",
            "Markets AI radar pro",
            "Four proof-backed workflow receipts",
        ],
        tags=["bundle", "markets", "commodities", "ai"],
    ),

]


WORKFLOW_CREDIT_PACKAGES: list[WorkflowCreditPackagePublic] = [
    WorkflowCreditPackagePublic(
        slug="starter-credits",
        title="Starter Credits",
        description="Enough balance to run one launch workflow or test the paid execution loop.",
        price=Money(amount="25", currency="ACP"),
        credit_amount=Money(amount="25", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        bonus_percent=0,
        recommended_for=["first paid workflow", "proof bundle test"],
    ),
    WorkflowCreditPackagePublic(
        slug="launch-credits",
        title="Launch Credits",
        description="Best fit for the Launch Pack plus one or two follow-up reruns.",
        price=Money(amount="95", currency="ACP"),
        credit_amount=Money(amount="100", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        bonus_percent=5,
        recommended_for=["launch pack", "campaign iteration"],
    ),
    WorkflowCreditPackagePublic(
        slug="growth-credits",
        title="Growth Credits",
        description="A larger balance for repeated launch, growth, and risk workflows.",
        price=Money(amount="225", currency="ACP"),
        credit_amount=Money(amount="250", currency="ACP"),
        accepted_currencies=["ACP", "wACP"],
        bonus_percent=11,
        recommended_for=["teams", "multiple assets", "repeat campaigns"],
    ),
]


def find_workflow_template(workflow_slug: str) -> WorkflowTemplatePublic | None:
    return next((item for item in WORKFLOW_TEMPLATES if item.slug == workflow_slug), None)


def find_workflow_bundle(bundle_slug: str) -> WorkflowBundlePublic | None:
    return next((item for item in WORKFLOW_BUNDLES if item.slug == bundle_slug), None)


def find_credit_package(package_slug: str) -> WorkflowCreditPackagePublic | None:
    return next((item for item in WORKFLOW_CREDIT_PACKAGES if item.slug == package_slug), None)



def quote_workflow_amount(template: WorkflowTemplatePublic, payment_currency: str) -> Decimal:
    from app.services.market_economy import quote_catalog_acp

    acp, _sticker, _spot = quote_catalog_acp(template.price.amount, payment_currency=payment_currency)
    return acp


def quote_bundle_amount(bundle: WorkflowBundlePublic, payment_currency: str) -> Decimal:
    from app.services.market_economy import quote_catalog_acp

    acp, _sticker, _spot = quote_catalog_acp(bundle.price.amount, payment_currency=payment_currency)
    return acp


def quote_credit_package_amount(package: WorkflowCreditPackagePublic, payment_currency: str) -> Decimal:
    from app.services.market_economy import quote_catalog_acp

    acp, _sticker, _spot = quote_catalog_acp(package.price.amount, payment_currency=payment_currency)
    return acp



def build_workflow_preview(template: WorkflowTemplatePublic) -> dict[str, Any]:
    return {
        "headline": f"Preview for {template.title}",
        "included": template.preview_items,
        "note": "Persistent workflow run created. Payment confirmation and execution are tracked separately.",
        "sample_output_url": f"/sample-reports/{template.slug}",
    }



def build_workflow_result_shell(template: WorkflowTemplatePublic) -> dict[str, Any]:
    return {
        "status": "preview_ready",
        "sections": template.output_items,
    }



def execute_workflow_template(template: WorkflowTemplatePublic, inputs: dict[str, Any] | None) -> dict[str, Any]:
    payload = inputs or {}
    project_name = str(payload.get("project_name") or payload.get("project") or "Your project")
    audience = str(payload.get("audience") or "crypto users")
    goals = payload.get("goals") if isinstance(payload.get("goals"), list) else []
    channels = payload.get("channels") if isinstance(payload.get("channels"), list) else []
    token_symbol = str(payload.get("token_symbol") or payload.get("symbol") or "TOKEN")
     
    primary_cta = str(payload.get("primary_cta") or "Book a call / request a workflow")
    posting_style = str(payload.get("posting_style") or "direct, proof-driven, anti-hype")
    reward_budget = str(payload.get("reward_budget") or "to be defined")
    market = str(payload.get("market") or payload.get("region") or "global crypto market")
    competitors = payload.get("competitors") if isinstance(payload.get("competitors"), list) else []
    constraints = payload.get("constraints") if isinstance(payload.get("constraints"), list) else []
    token_type = str(payload.get("token_type") or "utility token")
    chain = str(payload.get("chain") or payload.get("network") or "EVM")
    liquidity_model = str(payload.get("liquidity_model") or "DEX-led liquidity")
    geography = str(payload.get("geography") or payload.get("region") or "global")

    generated_at = datetime.now(UTC).isoformat()
    deliverable: dict[str, Any]
    execution_summary: dict[str, Any]

    if template.slug == "market-direction-brief":
        horizon = str(payload.get("horizon") or payload.get("timeframe") or "14-30 days")
        asset = str(payload.get("asset") or payload.get("market") or market)
        deliverable = {
            "disclaimer": "Educational scenario analysis only. Not investment, trading, or financial advice. No guaranteed returns.",
            "scope": {"asset": asset, "horizon": horizon, "geography": geography},
            "direction_scenarios": {
                "bullish": {
                    "weight": "0.30-0.40",
                    "thesis": f"Upside path for {asset} if catalysts listed by the buyer clear and risk appetite improves.",
                    "what_to_watch": ["Liquidity / volume confirmation", "Macro risk-on tape", "Buyer-stated catalysts"],
                },
                "base": {
                    "weight": "0.35-0.45",
                    "thesis": f"Range / choppy path for {asset} while evidence remains mixed over {horizon}.",
                    "what_to_watch": ["Mean-reversion around key levels", "Narrative fatigue", "Desk inventory flows"],
                },
                "bearish": {
                    "weight": "0.20-0.30",
                    "thesis": f"Downside path if demand softens or forced selling appears in {asset}.",
                    "what_to_watch": ["Break of support levels", "Funding / credit stress", "Policy shocks"],
                },
            },
            "invalidation": [
                "A hard move through the buyer's stated stop/invalidation level with volume.",
                "Material change in supply/demand facts not present in the inputs.",
            ],
            "next_checks": [
                "Refresh with live quotes and order-book depth when available.",
                "Separate desk OTC intake pricing from speculative quote paths.",
            ],
        }
        execution_summary = {
            "status": "completed_stub",
            "mode": "markets_scenario_analysis",
            "note": "Stub deliverable used when LLM is unavailable; regenerate with live LLM for richer analysis.",
        }
    elif template.slug == "commodity-price-outlook":
        commodity = str(payload.get("commodity") or payload.get("asset") or "oil")
        horizon = str(payload.get("horizon") or "30-90 days")
        deliverable = {
            "disclaimer": "Indicative commodity outlook for education. Not a firm bid, hedge recommendation, or guaranteed price path.",
            "commodity": commodity,
            "horizon": horizon,
            "region": geography,
            "driver_matrix": {
                "supply": ["Production / export constraints from buyer notes", "Inventory and logistics friction", "Licensing / sanctions for controlled materials"],
                "demand": ["Industrial offtake", "Seasonality", "Substitution risk"],
                "quotes": ["Spot vs forward framing", "ACP desk indicative rates are separate from market futures"],
            },
            "scenario_paths": {
                "growth": f"Price-supportive path for {commodity} if supply tightens and demand holds.",
                "base": f"Stabilization / range for {commodity} over {horizon}.",
                "contraction": f"Softer quotes if inventories build or offtake slows.",
            },
            "desk_notes": [
                "OTC commodity intake settles after assay/grade review — do not treat outlook as a desk bid.",
                "Uranium and other controlled minerals may require licensed counterparties.",
            ],
        }
        execution_summary = {"status": "completed_stub", "mode": "commodity_outlook", "commodity": commodity}
    elif template.slug == "crypto-quote-momentum-scan":
        deliverable = {
            "disclaimer": "Momentum framing only. Not a buy/sell signal or return promise.",
            "asset": {"project": project_name, "symbol": token_symbol, "chain": chain},
            "momentum_framing": {
                "relative_strength": "medium_pending_data",
                "narrative_heat": "medium",
                "liquidity_quality": "needs_proof",
            },
            "path_weights": {
                "continuation_up": "0.25-0.35",
                "range": "0.40-0.50",
                "mean_reversion_down": "0.20-0.30",
            },
            "narrative_map": [
                f"Positioning for {project_name} / {token_symbol} should be checked against live social and listing chatter.",
                "Separate product utility narrative from short-term quote noise.",
            ],
            "evidence_gaps": competitors[:5] or ["Live volume", "Holder concentration", "Unlock calendar"],
        }
        execution_summary = {"status": "completed_stub", "mode": "crypto_momentum_scan"}
    elif template.slug == "markets-ai-radar-pro":
        assets = payload.get("assets") if isinstance(payload.get("assets"), list) else [str(payload.get("asset") or "BTC"), "oil", "ACP"]
        deliverable = {
            "disclaimer": "Pro radar is scenario ranking for research. Not personalized investment advice.",
            "radar": {
                "horizon": str(payload.get("horizon") or "multi-horizon 7d/30d/90d"),
                "assets": assets,
                "cross_asset_notes": [
                    "Crypto risk appetite often co-moves with liquidity; commodities may diverge on physical supply shocks.",
                    "ACP desk rates for metals/commodities are indicative OTC quotes, not exchange futures settles.",
                ],
            },
            "ranked_scenarios": [
                {"rank": 1, "label": "Risk-on crypto + soft commodities", "weight": "0.30"},
                {"rank": 2, "label": "Range-bound mixed tape", "weight": "0.40"},
                {"rank": 3, "label": "Risk-off crypto + commodity squeeze", "weight": "0.30"},
            ],
            "monitoring_checklist": [
                "Refresh LLM run when material news hits buyer watchlist",
                "Track OTC intake volumes vs quote path divergence",
                "Document evidence sources for each scenario weight update",
            ],
            "evidence_gaps": constraints[:5] or ["Live futures curve", "Options skew", "Physical inventory prints"],
        }
        execution_summary = {"status": "completed_stub", "mode": "markets_radar_pro", "asset_count": len(assets)}
    elif template.slug == "token-listing-pack":

        deliverable = {
            "positioning_summary": {
                "project": project_name,
                "token_symbol": token_symbol,
                "token_type": token_type,
                "chain": chain,
                "audience": audience,
                "market": market,
            },
            "listing_copy": {
                "short": f"{project_name} is a {chain}-based crypto platform building execution-ready tooling for {audience}.",
                "medium": f"{project_name} uses {token_symbol} as a {token_type} to coordinate access, incentives, or operations across {audience} in the {market}.",
                "long": f"{project_name} is positioned as a practical crypto product for {audience}, focused on execution instead of abstraction. {token_symbol} supports the platform as a {token_type} on {chain}, while the broader offer is packaged for cleaner exchange, directory, and partner submissions.",
            },
            "exchange_form_answers": {
                "what_is_project": f"{project_name} is a crypto-focused platform built for {audience}.",
                "problem": f"Teams in the {market} need reusable listing-ready messaging instead of rewriting answers every time.",
                "solution": f"{project_name} packages execution-focused tooling and service flows instead of vague AI/Web3 positioning.",
                "token_utility": f"{token_symbol} functions as a {token_type} aligned with platform access, incentives, and operational usage.",
                "target_users": audience,
                "network": chain,
                "liquidity_model": liquidity_model,
            },
            "token_utility_bullets": [
                f"{token_symbol} is framed as a {token_type}, not a passive promise asset",
                "Utility messaging is aligned with product access and execution flows",
                "Listing language avoids yield/investment claims and stays product-centric",
            ],
            "due_diligence_checklist": [
                "Prepare token/logo asset pack",
                "Verify website, docs, socials, and token messaging are consistent",
                "Document token utility clearly and avoid financial-promise language",
                "Prepare founder/team/contact answers for listing reviewers",
                "Reuse approved answers across exchanges/directories with version control",
            ],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "listing_pack",
            "sections_generated": 5,
            "focus": ["exchange forms", "directory copy", "token positioning", "due diligence"],
        }
    elif template.slug == "token-launch-audit-pack":
        deliverable = {
            "launch_readiness_score": 78,
            "scorecard": {
                "positioning": {"score": 82, "note": f"{project_name} has a clear buyer narrative for {audience} if proof examples are visible."},
                "liquidity_proof": {"score": 64, "note": f"{liquidity_model} needs lock, depth, and counterparty evidence before premium promotion."},
                "listing_readiness": {"score": 76, "note": "Core listing materials can be prepared, but reviewer evidence should be attached."},
                "campaign_quality": {"score": 84, "note": "Campaign can lead with execution outcomes and avoid investment-return language."},
            },
            "priority_fixes": [
                "Publish a one-page token utility memo with non-yield language",
                "Attach liquidity lock or treasury-control evidence",
                "Prepare proof links for website, docs, team/contact, and socials",
                "Create a reviewer-facing launch checklist before paid distribution",
            ],
            "go_no_go": {
                "status": "conditional_go",
                "reason": "Launch can proceed after evidence pack and liquidity proof are tightened.",
            },
            "proof_requests": ["liquidity lock", "top holder distribution", "treasury signer model", "official links"],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "launch_audit",
            "sections_generated": 5,
            "focus": ["readiness score", "gap matrix", "evidence requests", "launch fixes"],
        }
    elif template.slug == "exchange-listing-submission-pack":
        deliverable = {
            "submission_positioning": f"{project_name} should present {token_symbol} as product access and operational coordination, not as a passive return instrument.",
            "exchange_answer_bank": {
                "project_overview": f"{project_name} serves {audience} with crypto-native execution tooling on {chain}.",
                "token_utility": f"{token_symbol} is framed as a {token_type} tied to platform access, fees, incentives, and proof-backed operations.",
                "market_need": f"{market} buyers need concise launch, listing, campaign, and risk artifacts with auditable receipts.",
                "compliance_posture": "Do not promise yield, price appreciation, or investment outcomes; keep claims tied to software/service execution.",
            },
            "reviewer_packet": [
                "Token contract and chain details",
                "Website, docs, socials, and contact route",
                "Liquidity and treasury evidence",
                "Token utility memo",
                "Risk and disclosure note",
            ],
            "submission_sequence": ["directory listing", "DEX analytics profile", "centralized exchange intake", "partner marketplace update"],
            "red_line_claims": ["guaranteed returns", "risk-free yield", "price target", "exchange approval guarantee"],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "exchange_listing_submission",
            "sections_generated": 5,
            "focus": ["exchange answers", "reviewer packet", "submission sequence", "safe claims"],
        }
    elif template.slug == "kol-telegram-campaign-builder":
        deliverable = {
            "campaign_offer": f"Promote {project_name} as useful execution infrastructure for {audience}, with proof links and a concrete next action.",
            "kol_brief": {
                "angle": "paid AI execution for crypto teams, not vague AI/Web3 hype",
                "must_include": ["one concrete buyer pain", "one proof/receipt point", "one CTA"],
                "must_avoid": ["investment promises", "fake urgency", "undisclosed paid claims"],
            },
            "telegram_funnel": [
                "Pinned proof post with sample output",
                "Daily operator update",
                "Live Q&A or office-hours thread",
                "Paid report/workflow CTA",
            ],
            "partner_scripts": {
                "short_dm": f"{project_name} sells proof-backed AI workflow execution for launch/listing/growth teams. Want a sample report link?",
                "public_post": f"{project_name} packages listing packs, campaign builders, bounty flows, and token risk reports with receipts.",
            },
            "attribution_plan": ["referral code per partner", "paid-run conversion tracking", "commission only after captured payment"],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "kol_telegram_campaign",
            "sections_generated": 5,
            "focus": ["KOL brief", "Telegram funnel", "partner scripts", "attribution"],
        }
    elif template.slug == "token-risk-report-pro":
        deliverable = {
            "risk_summary": f"Pro risk review for {project_name} / {token_symbol} on {chain}.",
            "overall_score": 71,
            "risk_domains": {
                "holder_concentration": {"rating": "needs_evidence", "request": "top holders, vesting, lockups"},
                "liquidity_durability": {"rating": "medium", "request": "lock proof, pool depth, withdrawal controls"},
                "team_and_ops": {"rating": "medium", "request": "official contacts, response policy, treasury signer model"},
                "market_integrity": {"rating": "medium", "request": "campaign disclosure and anti-sybil controls"},
            },
            "buyer_ready_summary": f"{token_symbol} can be reviewed as a {token_type}, but buyers and partners should request liquidity, holder, and treasury evidence before higher-risk commitments.",
            "evidence_gap_queue": ["holder CSV or explorer link", "liquidity lock proof", "treasury policy", "campaign disclosures"],
            "upgrade_path": "Run Token Launch Audit Pack or Exchange Listing Submission Pack for a fuller launch-readiness packet.",
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "risk_report_pro",
            "sections_generated": 5,
            "focus": ["risk score", "evidence gaps", "buyer summary", "upgrade path"],
        }
    elif template.slug == "agent-api-readiness-pack":
        deliverable = {
            "endpoint_offer": {
                "buyer": "AI agents, crypto tools, dashboards, and operators needing paid on-demand checks",
                "pricing_model": "pay-per-call with prepaid credits now, x402-compatible HTTP 402 terms next",
                "receipt_model": "every paid call records usage, amount, request hash, and machine-readable result",
            },
            "x402_response_plan": {
                "status": 402,
                "network": "Base",
                "currency": "ACP",
                "fields": ["accepts", "amount", "pay_to", "resource", "expires_at", "proof_url"],
            },
            "spend_controls": ["monthly cap per agent", "per-key usage export", "402 insufficient balance response", "request hash for retries"],
            "developer_docs_outline": ["products", "pricing", "curl examples", "API key setup", "receipt/proof format"],
            "sample_curl": "curl -X POST https://ancap.cloud/api/v1/paid-api/token-risk -H 'X-API-Key: ...' -d '{\"subject\":\"TOKEN\",\"chain\":\"Base\"}'",
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "agent_api_readiness",
            "sections_generated": 5,
            "focus": ["API pricing", "x402 terms", "spend controls", "developer docs"],
        }
    elif template.slug == "ai-iso-governance-readiness-pack":
        ai_system = str(payload.get("ai_system") or payload.get("workflow_name") or project_name)
        intended_use = str(payload.get("intended_use") or "paid AI workflow execution")
        risk_level = str(payload.get("risk_level") or "medium")
        owner = str(payload.get("owner") or "platform owner")
        deliverable = {
            "governance_summary": f"{ai_system} should be operated as a controlled AI workflow with documented scope, owner, inputs, outputs, supplier dependencies, and proof receipts.",
            "ai_capability_map": {
                "learning_or_generation": "LLM-assisted generation is used for workflow artifacts; deterministic templates remain fallback only.",
                "reasoning_and_planning": "The workflow should record prompt, model, provider status, output sections, and quality checks.",
                "decision_support": "Outputs should support buyer/operator decisions, not claim autonomous investment or compliance approval.",
                "human_oversight": f"{owner} owns review, exception handling, and release decisions for higher-risk outputs.",
            },
            "iso_style_control_matrix": {
                "scope_and_policy": ["Define workflow scope", "Publish acceptable-use limits", "Avoid investment-return claims"],
                "risk_management": ["Classify use case risk", "Log failure mode", "Mark degraded fallback outputs"],
                "documented_information": ["Store run inputs hash", "Store output/proof hash", "Keep receipt and audit trail"],
                "supplier_controls": ["Track LLM provider", "Track model version", "Track latency/status/cost estimate"],
                "operation_and_monitoring": ["Use rate limits", "Monitor paid run failure rate", "Review degraded receipts"],
                "corrective_actions": ["Assign owner", "Record root cause", "Verify fix before closing"],
            },
            "audit_ready_evidence": [
                "Workflow specification and version",
                "Prompt/provider/model metadata",
                "Input, output, and receipt hashes",
                "Payment intent and capture status",
                "Fallback/degraded-mode marker when applicable",
                "Corrective-action record for incidents or nonconformities",
            ],
            "sop_checklist": [
                "Define buyer-facing promise and excluded claims",
                "Collect required inputs before execution",
                "Run LLM or approved fallback with status logging",
                "Perform quality review for premium reports",
                "Generate receipt/proof bundle",
                "Escalate failed or degraded paid runs",
            ],
            "readiness_score": {
                "score": 76,
                "risk_level": risk_level,
                "note": "Ready for controlled internal use after evidence retention, degraded-output labeling, and corrective-action ownership are verified.",
            },
            "certification_note": "This pack prepares operating evidence and controls; it does not certify ISO conformity or replace an accredited audit.",
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "ai_iso_governance_readiness",
            "sections_generated": 6,
            "focus": ["AI governance", "ISO-style controls", "audit evidence", "corrective actions"],
        }
    elif template.slug == "crypto-campaign-builder":
        deliverable = {
            "campaign_thesis": f"Grow {project_name} with direct, conversion-oriented messaging for {audience}.",
            "offer_stack": {
                "core_offer": f"{project_name} should be sold as an execution-ready crypto product, not abstract infrastructure.",
                "primary_cta": primary_cta,
                "positioning_rule": "Lead with outcomes, proof, and clear buyer fit.",
            },
            "channel_mix": channels or ["Telegram", "X", "Landing page", "Partner communities"],
            "30_day_plan": {
                "week_1": ["clarify offer", "ship landing copy", "define primary CTA"],
                "week_2": ["launch content rhythm", "seed partner mentions", "collect objections"],
                "week_3": ["test hooks and CTAs", "refine response scripts", "push best-performing angle"],
                "week_4": ["double down on winning channel", "publish proof/results", "convert warm leads"],
            },
            "content_calendar": {
                "telegram": ["operator update", "case/proof post", "CTA post"],
                "x": ["hook thread", "proof snippet", "offer reiteration"],
                "landing_page": ["headline test", "proof block", "CTA refinement"],
            },
            "post_angles": [
                f"Why {project_name} matters for {audience}",
                "Outcome-driven offer instead of tech abstraction",
                "Operational proof and before/after examples",
            ],
            "response_scripts": {
                "warm_inbound": "Send short offer summary, proof point, and CTA to continue.",
                "skeptical_reply": "Acknowledge objection, show concrete proof, and restate buyer fit.",
                "partner_outreach": "Lead with audience overlap and clear mutual upside.",
            },
            "goals": goals or ["Increase qualified inbound", "Improve campaign clarity", "Raise conversion intent"],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "campaign_plan",
            "sections_generated": 6,
            "focus": channels or ["Telegram", "X", "Landing page"],
        }
    elif template.slug == "telegram-growth-kit":
        deliverable = {
            "community_positioning": f"{project_name} Telegram should feel operational, trustworthy, and anti-spam.",
            "rules": [
                "No fake support or wallet-drain links",
                "No repetitive bounty spam",
                "Questions must route through a visible support flow",
                "Admins publish clear escalation rules",
            ],
            "welcome_flow": [
                f"Welcome {audience} with one pinned orientation message",
                "Show main CTA, docs, and scam warning",
                "Prompt users toward one meaningful next action",
            ],
            "content_pillars": [
                "product progress",
                "proof/results",
                "education / FAQ",
                "community call-to-action",
            ],
            "posting_cadence": {
                "daily": ["1 short update", "1 reply/support sweep"],
                "weekly": ["1 proof post", "1 pinned message review", "1 FAQ refresh"],
                "style": posting_style,
            },
            "moderation_checklist": [
                "Review scam reports daily",
                "Keep FAQ and pinned post current",
                "Remove low-signal farming messages fast",
            ],
            "operator_playbook": {
                "new_member_goal": "Get the user to one meaningful action within the first session.",
                "escalation_rule": "Move sensitive/account issues into a controlled support path.",
                "spam_policy": "Remove repetitive farming behavior fast and visibly.",
            },
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "telegram_ops_kit",
            "sections_generated": 6,
            "focus": ["community trust", "moderation", "onboarding", "content ops"],
        }
    elif template.slug == "airdrop-bounty-builder":
        deliverable = {
            "campaign_structure": {
                "awareness": ["follow/join", "share campaign post"],
                "contribution": ["thread/comment", "content creation", "referral invite"],
                "review": ["proof queue", "duplicate check", "manual escalation"],
            },
            "task_matrix": {
                "low_effort": ["follow channel", "join community"],
                "medium_effort": ["publish thoughtful reply", "create one distribution post"],
                "high_effort": ["write original thread", "bring verified referral traffic"],
            },
            "reward_logic": {
                "base_rule": "Higher-value actions receive higher weighted rewards",
                "anti_sybil": "Duplicate wallet/social proofs are rejected",
                "quality_multiplier": "Original useful contributions outrank copy-paste tasks",
                "budget_note": reward_budget,
            },
            "proof_policy": [
                "Wallet proof",
                "Link/screenshot proof",
                "Manual review for suspicious submissions",
            ],
            "review_queue_rules": {
                "auto_reject": ["duplicate wallet", "missing proof", "obvious bot spam"],
                "manual_review": ["suspicious velocity", "copy-paste content", "identity ambiguity"],
                "approval_goal": "Keep payout quality high without turning review into a bottleneck",
            },
            "constraints": constraints or ["Avoid spam-farm incentives", "Keep review burden manageable"],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "bounty_campaign",
            "sections_generated": 6,
            "focus": ["reward design", "anti-sybil", "proof review", "task matrix"],
        }
    elif template.slug == "token-risk-report":
        deliverable = {
            "risk_summary": f"Structured first-pass risk snapshot for {project_name} / {token_symbol} on {chain}.",
            "risk_matrix": {
                "token_structure": {
                    "rating": "medium",
                    "reason": f"{token_symbol} is described as a {token_type}; exact issuance and governance constraints were not independently verified.",
                },
                "liquidity": {
                    "rating": "medium",
                    "reason": f"Current liquidity model is described as {liquidity_model}, but lock depth and durability still need proof.",
                },
                "operations": {
                    "rating": "medium",
                    "reason": "Operational claims, response speed, and treasury discipline require source validation.",
                },
                "market_positioning": {
                    "rating": "low_to_medium",
                    "reason": f"Narrative fit for {geography} users may be reasonable, but distribution proof is still needed.",
                },
            },
            "trust_signals": [
                "Public docs or known team presence",
                "Observable liquidity and treasury communication",
                "Consistency across website, socials, and token messaging",
                "Clear non-yield product positioning reduces obvious marketing risk",
            ],
            "red_flags": [
                "Holder concentration should be verified deeper",
                "Liquidity lock / treasury policy needs explicit proof",
                "Operational claims require source validation",
                "Any mismatch between token utility and public pitch should be treated as material risk",
            ],
            "missing_data": [
                "Top holder distribution",
                "Treasury / multisig disclosure",
                "Liquidity lock evidence",
                "Exchange / partner references",
            ],
            "next_verification_steps": [
                "Check holder concentration and vesting logic",
                "Verify treasury wallet disclosures and signer model",
                "Confirm liquidity durability and withdrawal controls",
                "Compare website claims against onchain / public evidence",
            ],
            "peer_context": competitors or ["Category peers not provided"],
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "risk_report",
            "sections_generated": 6,
            "focus": ["risk matrix", "trust signals", "red flags", "verification steps"],
        }
    elif template.slug.startswith("aeterna-"):
        intent = str(payload.get("intent_kind") or template.slug)
        vault_ref = str(payload.get("vault_hash") or payload.get("content_sha256") or "not_provided")
        deliverable = {
            "division": "AETERNA",
            "intent": intent,
            "compliance": (
                "Educational / consult-prep only. Not a diagnosis. "
                "No CRISPR guide design, gene synthesis, or DIY enhancement protocols."
            ),
            "vault_hash_ref": vault_ref,
            "sequencing_com_hint": "Import exports from https://sequencing.com/ into the AETERNA DNA vault first.",
            "sections": template.output_items,
            "partner_handoff": {
                "required": True,
                "note": "Route outputs to a verified licensed partner before any clinical action.",
            },
            "sandbox_note": (
                "Genome sandbox explores annotations on vaulted metadata; it does not edit DNA."
            ),
        }
        if template.slug == "aeterna-stem-cell-organ-print":
            deliverable["intent"] = str(payload.get("intent_kind") or "organ_bioprint")
            deliverable["compliance"] = (
                "Licensed-partner bioprint intake only. Not a diagnosis. "
                "No CRISPR guide design, gene synthesis, DIY cell culture, or unlicensed enhancement protocols."
            )
            deliverable["manufacturing"] = {
                "mode": "licensed_partner_bioreactor",
                "unit": "per_organ",
                "price_acp": "250000",
                "primary_cell_source": "autologous_stem_cells",
                "fallback_cell_source": "wisdom_tooth_dental_pulp_stem_cells_dpsc",
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. "
                    "Printing occurs only in a licensed biochemical reactor operated by a verified partner — not a home kit."
                ),
            }
        if template.slug == "aeterna-mrna-reprogramming-brief":
            deliverable["intent"] = str(payload.get("intent_kind") or "partial_reprogramming_consult")
            deliverable["compliance"] = (
                "Educational / licensed-consult prep only. Not a diagnosis and not an approved therapy. "
                "No lipid recipes, mRNA sequences, LNP formulation steps, CRISPR guide design, "
                "gene synthesis, or DIY enhancement protocols."
            )
            deliverable["reprogramming"] = {
                "mode": "partial_keep_cell_identity",
                "delivery_literacy": "mrna_in_lipid_nanoparticle",
                "price_acp": "1000000",
                "citation": {
                    "kind": "uspto_notice_of_allowance_journalism",
                    "announced": "2026-08-27",
                    "legal_as_of": "2026-09-11",
                    "title": "Lipid Structures and Compositions Comprising the Same",
                    "platform": "eTurna LNP (Turn Biotechnologies assets; Daewoong Pharmaceutical)",
                    "sources": [
                        "https://incrussia.ru/news/v-ssha-odobrili-zayavku-na-patent-dlya-omolozheniya-kletok/",
                        "https://www.koreaherald.com/article/10854319",
                    ],
                    "affiliation": False,
                },
                "note": (
                    "A notice of allowance is not a fully issued U.S. patent and is not marketing authorization. "
                    "Reported work remains preclinical. ANCAP is not affiliated with Daewoong, Turn Bio, or eTurna."
                ),
            }
        if template.slug == "aeterna-vet-cat-cryo-restore":
            deliverable["intent"] = str(payload.get("intent_kind") or "vet_feline_cryo_restore")
            deliverable["compliance"] = (
                "Licensed-veterinary-partner tissue-bank intake only. Not a diagnosis, not a marketed "
                "veterinary device, and not a return-to-life warranty. No CRISPR, gene synthesis, "
                "or DIY cryoprotectant protocol."
            )
            deliverable["veterinary"] = {
                "mode": "licensed_veterinary_partner",
                "species": "felis_catus",
                "architecture": "controlled_rate_freezer_plus_ln2_cryochamber",
                "price_acp": "75000",
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical cryopreservation "
                    "and any reimplantation occur only in a licensed veterinary clinic."
                ),
            }
        if template.slug == "aeterna-vet-regen-pod":
            deliverable["intent"] = str(payload.get("intent_kind") or "vet_canine_regen_pod")
            deliverable["compliance"] = (
                "Licensed-veterinary-partner organ-pathway intake only. Not a diagnosis and not a "
                "marketed chamber. Infographic survival or speed figures are not product claims. "
                "No CRISPR, gene synthesis, or DIY bioreactor protocol."
            )
            deliverable["veterinary"] = {
                "mode": "licensed_veterinary_partner",
                "species": "canis_familiaris",
                "architecture": "vet_regen_pod_organ_bank_bioprint_robot_assist",
                "price_acp": "180000",
                "note": (
                    "ANCAP settles ACP and matches a licensed veterinary partner. ANCAP does not operate "
                    "VET REGEN POD hardware."
                ),
            }
        if template.slug == "aeterna-vinci-light-chamber":
            deliverable["intent"] = str(payload.get("intent_kind") or "vinci_light_chamber")
            deliverable["compliance"] = (
                "Licensed phototherapy / dermatology partner intake only. Not a diagnosis, not a "
                "marketed medical device, not a reconstructed Leonardo invention, and not a safe-tanning "
                "or vitamin-D treatment claim. No home LED-array recipe, CRISPR, or gene synthesis."
            )
            deliverable["photobiomodulation"] = {
                "mode": "licensed_phototherapy_partner",
                "architecture": "full_body_led_uva_red_nir_chamber",
                "price_acp": "48000",
                "bands": {
                    "uva": "320-400nm",
                    "red": "620-680nm",
                    "nir": "780-950nm",
                    "pbm_window": "600-950nm",
                },
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical light sessions occur "
                    "only under a licensed clinician. Infographic 'safe tan' copy is not a product claim. "
                    "UV exposure remains a known skin-cancer risk class."
                ),
            }
        if template.slug == "aeterna-microwave-body-contouring":
            deliverable["intent"] = str(payload.get("intent_kind") or "microwave_body_contouring")
            deliverable["compliance"] = (
                "Licensed aesthetic / dermatology partner intake only. Not a diagnosis, not a marketed "
                "medical device, not liposuction, and not a guaranteed fat-loss or body-contour claim. "
                "No home microwave-antenna recipe, CRISPR, or gene synthesis."
            )
            deliverable["microwave_body_contouring"] = {
                "mode": "licensed_aesthetic_dermatology_partner",
                "architecture": "contact_cooled_microwave_applicator",
                "price_acp": "52000",
                "bands": {
                    "ism_2450": "2.45GHz",
                    "ism_5800": "5.8GHz",
                },
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical microwave sessions occur "
                    "only under a licensed clinician. Infographic adipocyte-blebbing or lymphatic-clearance "
                    "copy is public protocol literacy, not a product claim."
                ),
            }
        if template.slug == "aeterna-biofusion-micromanipulation":
            deliverable["intent"] = str(payload.get("intent_kind") or "biofusion_micromanipulation")
            deliverable["compliance"] = (
                "Licensed ART / agricultural / BSL-lab partner intake only. Not a diagnosis, not a marketed "
                "medical device, not a fertility clinic, and not a guaranteed pregnancy or embryo. "
                "No home ICSI recipe, CRISPR, gene synthesis, or pathogen protocol."
            )
            deliverable["biofusion_micromanipulation"] = {
                "mode": "licensed_art_agri_bsl_partner",
                "architecture": "biofusion_micromanipulation_chamber",
                "price_acp": "88000",
                "rails": {
                    "ivf_icsi": "licensed_assisted_reproduction_clinic",
                    "plant_pollination": "licensed_agricultural_research_partner",
                    "embryo_observation": "clinic_protocol_literacy",
                    "microorganism_handling": "licensed_bsl_lab",
                },
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical micromanipulation occurs "
                    "only under a licensed clinician or BSL-lab operator. Infographic genetic-manipulation copy "
                    "is protocol literacy, not a product claim."
                ),
            }
        if template.slug == "aeterna-dpsc-biomaterial":
            deliverable["intent"] = str(payload.get("intent_kind") or "dpsc_biomaterial")
            deliverable["compliance"] = (
                "Licensed bioreactor-partner intake only. Not a diagnosis, not a full organ print, and not an "
                "FDA/CE cell therapy. No home culture kit, CRISPR, or gene synthesis."
            )
            deliverable["dpsc_biomaterial"] = {
                "mode": "licensed_bioreactor_partner",
                "architecture": "wisdom_tooth_dpsc_expansion",
                "price_acp": "65000",
                "cell_source": "wisdom_tooth_dental_pulp_stem_cells_dpsc",
                "related_organ_print_slug": "aeterna-stem-cell-organ-print",
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Cell expansion occurs only in a "
                    "licensed biochemical reactor. This SKU is a biomaterial construct, not a 250,000 ACP organ."
                ),
            }
        if template.slug == "aeterna-vascular-care-plus":
            deliverable["intent"] = str(payload.get("intent_kind") or "vascular_care_plus")
            deliverable["compliance"] = (
                "Licensed phlebology / vascular / aesthetic partner intake only. Not a diagnosis, not a marketed "
                "medical device, not a thrombosis treatment, and not a guaranteed varicose-vein claim. "
                "No home gas-applicator recipe, CRISPR, or gene synthesis."
            )
            deliverable["vascular_care_plus"] = {
                "mode": "licensed_phlebology_aesthetic_partner",
                "architecture": "anhydrous_n2_o2_lightwave_applicator",
                "price_acp": "54000",
                "gas": {"mix": "N2+O2", "class": "medical_grade_architecture_literacy"},
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical sessions occur only under "
                    "a licensed clinician. Infographic before/after or angiopathy copy is protocol literacy, "
                    "not a product claim. DVT / PE remain medical emergencies."
                ),
            }
        if template.slug == "aeterna-vascular-care":
            deliverable["intent"] = str(payload.get("intent_kind") or "vascular_care")
            deliverable["compliance"] = (
                "Licensed phlebology / vascular / aesthetic partner intake only. Not a diagnosis, not a marketed "
                "medical device, not surgery, and not a guaranteed vein-diameter claim. "
                "No home RF/US recipe, CRISPR, or gene synthesis."
            )
            deliverable["vascular_care"] = {
                "mode": "licensed_phlebology_aesthetic_partner",
                "architecture": "ultrasound_rf_thermal_applicator",
                "price_acp": "58000",
                "modalities": {
                    "ultrasound": "blood_flow_literacy",
                    "radiofrequency": "wall_tone_literacy",
                    "thermal": "tissue_comfort_literacy",
                },
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical sessions occur only under "
                    "a licensed clinician. Infographic before/after copy is protocol literacy, not a product claim."
                ),
            }
        if template.slug == "aeterna-transdermal-pistol":
            deliverable["intent"] = str(payload.get("intent_kind") or "transdermal_pistol")
            deliverable["compliance"] = (
                "Licensed clinic-partner intake only. Not a diagnosis, not a prescription dispenser, not "
                "compounding, and not a guaranteed transdermal dose. No home injection kit, CRISPR, or gene synthesis."
            )
            deliverable["transdermal_pistol"] = {
                "mode": "licensed_clinic_partner",
                "architecture": "needle_free_transdermal_pistol",
                "price_acp": "46000",
                "delivery": {"route": "aerosol_plus_carrier_gas", "gases_literacy": "CO2_N2_O2_or_mix"},
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical sessions occur only under "
                    "a licensed clinician with a lawful substance list. Infographic cosmetic or fat-reduction "
                    "copy is protocol literacy, not a product claim."
                ),
            }
        if template.slug == "aeterna-m-receptor-subscription":
            deliverable["intent"] = str(payload.get("intent_kind") or "m_receptor_subscription")
            deliverable["compliance"] = (
                "Licensed clinic subscription only. Not a diagnosis, not compounding, not a scopolamine or "
                "muscarinic-drug recipe, and not a treatment claim. No home iontophoresis, inhaler, or vagus "
                "stimulator kit, CRISPR, or gene synthesis."
            )
            deliverable["m_receptor_subscription"] = {
                "mode": "licensed_clinic_subscription",
                "architecture": "m_receptor_multimodal_delivery",
                "billing": "subscription",
                "price_acp_monthly": "12000",
                "price_acp_quarterly": "32000",
                "price_acp_annual": "108000",
                "modules": {
                    "transdermal_patch": "licensed_clinic_literacy",
                    "iontophoresis": "licensed_clinic_literacy",
                    "inhaler_nebulizer": "licensed_clinic_literacy",
                    "neurostimulation": "vagus_adjacent_literacy",
                },
                "note": (
                    "ANCAP settles the subscription period in ACP and issues a partner handoff brief. "
                    "Physical modules occur only under a licensed clinician. Infographic M1–M5 and "
                    "scopolamine copy is receptor literacy, not a product claim."
                ),
            }
        if template.slug == "aeterna-oxygen-carrier":
            deliverable["intent"] = str(payload.get("intent_kind") or "oxygen_carrier_brief")
            deliverable["compliance"] = (
                "Licensed bioreactor / transfusion-medicine partner only. Not a blood product, not compounding "
                "of hemoglobin or perfluorocarbon, not a CE/FDA oxygen therapeutic, and not a manufacturing SOP. "
                "No home emulsion kit, CRISPR, or gene synthesis."
            )
            deliverable["oxygen_carrier"] = {
                "mode": "licensed_bioreactor_partner",
                "architecture": "hboC_or_pfc_oxygen_carrier",
                "price_acp": "92000",
                "cores_literacy": ["modified_hemoglobin_vesicle", "perfluorocarbon_emulsion"],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical manufacture occurs only "
                    "under a licensed bioreactor. Infographic QC and fill copy is architecture literacy, "
                    "not a product claim."
                ),
            }
        if template.slug == "aeterna-synthetic-blood-mamba":
            deliverable["intent"] = str(payload.get("intent_kind") or "synthetic_blood_mamba_brief")
            deliverable["compliance"] = (
                "Licensed bioreactor / transfusion-medicine partner only. Not a blood product, not compounding "
                "of venom peptides, hemoglobin or perfluorocarbon, not a CE/FDA therapeutic, not a toxin "
                "recipe, and not a manufacturing SOP. No home emulsion or venom kit, CRISPR, or gene synthesis."
            )
            deliverable["synthetic_blood_mamba"] = {
                "mode": "licensed_bioreactor_partner",
                "architecture": "hboc_pfc_black_mamba_peptide_architecture",
                "price_acp": "98000",
                "layers_literacy": [
                    "oxygen_carrier_core",
                    "lipid_shell",
                    "polymer_mesh",
                    "modified_black_mamba_peptides",
                    "delivery_vesicle",
                    "immune_management_sensors",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Physical manufacture occurs only "
                    "under a licensed bioreactor. Infographic stages and controlled-dose callouts are "
                    "architecture literacy, not a product claim or dosing guide."
                ),
            }
        if template.slug == "aeterna-adhd-support":
            deliverable["intent"] = str(payload.get("intent_kind") or "adhd_support_brief")
            deliverable["compliance"] = (
                "Licensed clinician partner only. Not a diagnosis, not a prescription, not stimulant "
                "compounding, not a CE/FDA drug, and not a guaranteed academic or financial outcome. "
                "Infographic billionaire-path steps are motivational literacy, not a promise."
            )
            deliverable["adhd_support"] = {
                "mode": "licensed_clinician_partner",
                "architecture": "adhd_support_partner_literacy",
                "price_acp": "42000",
                "themes_literacy": [
                    "attention_and_task_completion",
                    "planning_and_impulse_control",
                    "emotion_regulation",
                    "peer_and_team_skills",
                    "self_esteem",
                    "comorbid_risk_literacy",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Clinical care occurs only "
                    "under a licensed clinician. Infographic steps are motivational literacy, not a "
                    "product claim."
                ),
            }
        if template.slug == "aeterna-aurea-vita":
            deliverable["intent"] = str(payload.get("intent_kind") or "aurea_vita_brief")
            deliverable["compliance"] = (
                "Licensed lifestyle / longevity / nutrition-sport partner only. Not medical advice, "
                "not a diagnosis, not a prescription, not a CE/FDA drug or device, and not a guaranteed "
                "lifespan, weight, or athletic outcome."
            )
            deliverable["aurea_vita"] = {
                "mode": "licensed_lifestyle_longevity_partner",
                "architecture": "aurea_vita_quality_of_life_literacy",
                "price_acp": "40",
                "themes_literacy": [
                    "quality_of_life_acceleration",
                    "longevity_literacy",
                    "nutrition_recommendations",
                    "sport_and_movement",
                    "everyday_health_hygiene",
                    "sleep_and_recovery",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Coaching or clinical care "
                    "occurs only under a licensed partner. Infographics are motivational literacy, "
                    "not a product claim."
                ),
            }
        if template.slug == "aeterna-down-syndrome-support":
            deliverable["intent"] = str(payload.get("intent_kind") or "down_syndrome_support_brief")
            deliverable["compliance"] = (
                "Licensed developmental pediatrics / genetics / child-neurology partner only. Not a cure "
                "for Down syndrome, not a diagnosis, not gene therapy or CRISPR sold by ANCAP, not a "
                "prescription, and not a guaranteed developmental outcome."
            )
            deliverable["down_syndrome_support"] = {
                "mode": "licensed_clinician_partner",
                "architecture": "down_syndrome_support_partner_literacy",
                "price_acp": "42000",
                "themes_literacy": [
                    "early_intervention",
                    "family_caregiver_coordination",
                    "learning_and_skills_adaptation",
                    "health_partner_screening",
                    "community_peer_support",
                    "developmental_literacy",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Clinical care occurs only "
                    "under a licensed clinician. Infographics are support literacy, not a cure claim."
                ),
            }
        if template.slug == "aeterna-substance-coding":
            deliverable["intent"] = str(payload.get("intent_kind") or "substance_coding_brief")
            deliverable["compliance"] = (
                "Licensed addiction-medicine / narcology / clinical-hypnosis partner only. Not a coding "
                "session performed by ANCAP, not a guarantee of abstinence, not compounding or sale of "
                "controlled substances by ANCAP, and not a substitute for emergency care."
            )
            deliverable["substance_coding"] = {
                "mode": "licensed_clinician_partner",
                "architecture": "substance_coding_partner_literacy",
                "price_acp": "48000",
                "modalities_literacy": [
                    "light_protocol_literacy",
                    "clinic_only_substance_protocol_literacy",
                    "clinical_hypnosis_literacy",
                    "non_essential_psychoactive_dependence_literacy",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Clinical care occurs only "
                    "under a licensed clinician. Infographics are support literacy, not a coding claim."
                ),
            }
        if template.slug == "aeterna-pulmopure-subscription":
            deliverable["intent"] = str(payload.get("intent_kind") or "pulmopure_subscription")
            deliverable["compliance"] = (
                "Licensed pulmonology / respiratory clinic subscription only. Not a CE/FDA device sold by "
                "ANCAP, not ozone therapy, not medical-gas compounding, not a home respiratory kit, and not "
                "a guaranteed tar-clearance or 'clean lungs' outcome."
            )
            deliverable["pulmopure_subscription"] = {
                "mode": "licensed_clinic_subscription",
                "architecture": "pulmopure_gas_vibration_partner_literacy",
                "billing": "subscription",
                "price_acp_monthly": "14000",
                "price_acp_quarterly": "38000",
                "price_acp_annual": "128000",
                "modules": {
                    "gas_vibration": "licensed_clinic_literacy",
                    "medical_gas_mix": "partner_protocol_literacy_only",
                    "lavender_oil_atomizer": "aromatherapy_literacy",
                    "soft_standard_intensive_modes": "partner_mode_literacy",
                },
                "note": (
                    "ANCAP settles the subscription period in ACP and issues a partner handoff brief. "
                    "Physical sessions occur only under a licensed clinician after screening. Infographic "
                    "modes and before/after alveoli are protocol literacy, not a product claim."
                ),
            }

        if template.slug == "aeterna-barsuk-quantum-pen":
            deliverable["intent"] = str(payload.get("intent_kind") or "barsuk_quantum_pen_brief")
            deliverable["compliance"] = (
                "Licensed secure-comms partner only. Not a Parker product, not a weapon, not unbreakable "
                "crypto, and not a CE/FDA device sold by ANCAP."
            )
            deliverable["barsuk_quantum_pen"] = {
                "mode": "licensed_secure_comms_partner",
                "architecture": "barsuk_quantum_pen_partner_literacy",
                "price_acp": "36000",
                "themes_literacy": [
                    "pen_form_secure_comms",
                    "quantum_crypto_literacy",
                    "sensor_nav_literacy",
                    "smart_ink_literacy",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Infographic ranges are fiction "
                    "literacy, not a product claim."
                ),
            }
        if template.slug == "aeterna-teleport-earphones":
            deliverable["intent"] = str(payload.get("intent_kind") or "teleport_earphones_brief")
            deliverable["compliance"] = (
                "Licensed partner fiction brief only. Not an Apple product, not a real teleporter, not a "
                "military weapon system, and not a guaranteed medical-evacuation outcome."
            )
            deliverable["teleport_earphones"] = {
                "mode": "licensed_partner_fiction_brief",
                "architecture": "teleport_earphones_medevac_literacy",
                "price_acp": "58000",
                "themes_literacy": [
                    "fictional_medevac_teleport",
                    "quantum_comms_literacy",
                    "neural_interface_literacy",
                    "field_case_ruggedization_literacy",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief framed around medevac fiction. "
                    "Infographic combat panels are sci-fi literacy, not ops doctrine."
                ),
            }
        if template.slug == "aeterna-installation-project":
            deliverable["intent"] = str(payload.get("intent_kind") or "installation_project_brief")
            deliverable["compliance"] = (
                "Licensed neonatology / infant-nutrition partner only. Not infant formula sold by ANCAP, "
                "not a CE/FDA hyperbaric device, not home HBO, and not a guaranteed clinical outcome."
            )
            deliverable["installation_project"] = {
                "mode": "licensed_neonatology_nutrition_partner",
                "architecture": "installation_project_neonatal_partner_literacy",
                "price_acp": "72000",
                "themes_literacy": [
                    "high_protein_infant_formula_line",
                    "natural_synthetic_milk_gmp_literacy",
                    "neonatal_hyperbaric_chamber_literacy",
                    "premature_infant_nursing_literacy",
                ],
                "note": (
                    "ANCAP settles ACP and issues a partner handoff brief. Infographic capacity, ATA, and "
                    "composition callouts are architecture literacy, not product claims."
                ),
            }
        if template.slug == "aeterna-dna-pheromone-perfume":
            deliverable["intent"] = str(payload.get("intent_kind") or "dna_pheromone_perfume_bottle")
            deliverable["compliance"] = (
                "Licensed cosmetic / fragrance partner only. Sold per bottle. Not a drug, not an "
                "aphrodisiac medical claim, not a guaranteed attraction outcome, and not CE/FDA "
                "pheromone medicine. Genome bytes are never uploaded."
            )
            deliverable["dna_pheromone_perfume"] = {
                "mode": "licensed_cosmetic_fragrance_partner",
                "architecture": "dna_matched_pheromone_perfume_literacy",
                "unit": "per_bottle",
                "quantity": 1,
                "price_acp": "8900",
                "themes_literacy": [
                    "olfactory_profile_from_vault_hash",
                    "cosmetic_pheromone_blend_literacy",
                    "skin_safe_fragrance_carrier",
                    "partner_fill_and_label",
                ],
                "note": (
                    "ANCAP settles 8,900 ACP for one bottle and issues a partner handoff brief. "
                    "Optional vault-hash matching is olfactory literacy, not a medical pheromone assay."
                ),
            }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "aeterna_longevity",
            "sections_generated": len(template.output_items),
            "focus": ["dna vault", "longevity consult", "partner handoff", "acp receipt"],
        }
    elif template.slug == "entertainment-tesla-coil-party":
        deliverable = {
            "desk": "entertainment",
            "intent": "tesla_coil_party",
            "compliance": (
                "Licensed venue partner only. Not affiliated with Jack Daniel's or Brown-Forman. "
                "ANCAP does not hold a liquor licence and does not sell alcohol, cannabis, or controlled "
                "substances. Age/ID gates apply. Tesla coil HV is venue electrical-safety literacy — not a DIY kit."
            ),
            "tesla_coil_party": {
                "mode": "licensed_venue_partner",
                "architecture": "tesla_coil_party_partner_literacy",
                "price_acp": "8900",
                "hospitality_literacy": [
                    "jack_daniels_brand_hospitality_where_licensed",
                    "age_id_gate_18_or_21",
                    "jurisdiction_permitted_adult_substances_only",
                    "hv_tesla_coil_venue_operator_only",
                ],
                "note": (
                    "ANCAP settles ACP and issues a venue partner handoff brief. Complimentary whiskey "
                    "copy is hospitality literacy where the partner is licensed — not an ANCAP bar."
                ),
            },
            "summary": f"Tesla coil party venue brief generated for {project_name}.",
            "items": template.output_items,
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "entertainment_party",
            "sections_generated": len(template.output_items),
            "focus": ["venue handoff", "age gate", "hv safety literacy", "acp receipt"],
        }
    elif template.slug == "antique-fire-restore":
        deliverable = {
            "desk": "conservation",
            "intent": "antique_fire_restore",
            "compliance": (
                "Licensed conservation / metallurgy partner only. Reverse-combustion literacy is not a "
                "DIY furnace kit. Six-stage map is conservation analogy — not medical burn care. "
                "No authenticity guarantee. ANCAP does not pay insurance claims for fire loss."
            ),
            "antique_fire_restore": {
                "mode": "licensed_conservation_partner",
                "architecture": "antique_fire_restore_partner_literacy",
                "price_acp": "42000",
                "literacy": [
                    "reverse_combustion_reduction_chemistry",
                    "six_stage_conservation_analogy_not_medical",
                    "no_diy_furnace",
                    "no_authenticity_guarantee",
                    "no_ancap_insurance_payout",
                ],
                "note": (
                    "ANCAP settles 42,000 ACP and issues a partner handoff brief. Workshop work "
                    "stays with the licensed conservation / metallurgy partner."
                ),
            },
            "summary": f"Antique fire-restore partner brief generated for {project_name}.",
            "items": template.output_items,
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "conservation_fire_restore",
            "sections_generated": len(template.output_items),
            "focus": ["partner handoff", "reverse combustion literacy", "conservation stages", "acp receipt"],
        }
    elif template.slug.startswith("stardust-"):
        deliverable = {
            "desk": "stardust",
            "brand_literacy": "StardustSRT",
            "compliance": (
                "Licensed partner weather-control / earth-monitoring literacy only. Not a live "
                "geoengineering console, not unilateral worldwide weather modification by ANCAP, "
                "not an official meteorological warning, and not a guaranteed storm or rainfall outcome."
            ),
            "summary": f"StardustSRT partner brief generated for {project_name}.",
            "items": template.output_items,
            "modules_literacy": [
                "rainfall_enhancement",
                "storm_dissipation",
                "temperature_regulation",
                "snow_management",
                "extreme_weather_monitor",
                "disaster_early_warning",
            ],
            "note": (
                "ANCAP settles ACP and issues a partner handoff brief. Infographic Weather Control "
                "toggles are product literacy, not ops doctrine."
            ),
        }
        execution_summary = {
            "mode": "workflow_specific",
            "artifact_kind": "stardust_weather_control",
            "sections_generated": len(template.output_items),
            "focus": ["weather control", "earth monitoring", "partner handoff", "acp receipt"],
        }
    else:
        deliverable = {
            "summary": f"Workflow result generated for {project_name}.",
            "items": template.output_items,
        }
        execution_summary = {
            "mode": "template_stub",
            "artifact_kind": "generic",
            "sections_generated": len(template.output_items),
            "focus": [template.slug],
        }

    return {
        "status": "completed",
        "workflow_slug": template.slug,
        "template_title": template.title,
        "generated_at": generated_at,
        "delivery": template.output_items,
        "deliverable": deliverable,
        "execution_summary": execution_summary,
    }
