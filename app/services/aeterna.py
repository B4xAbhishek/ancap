"""AETERNA longevity marketplace service (R12)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import (
    AeternaDnaVaultEntry,
    AeternaIntentOrder,
    AeternaPartner,
    OrgRoleEnum,
)
from app.schemas.aeterna import (
    AeternaAgingHallmarkPublic,
    AeternaDnaVaultCreate,
    AeternaDnaVaultPublic,
    AeternaIntentKind,
    AeternaIntentOrderCreate,
    AeternaIntentOrderPublic,
    AeternaOrderStatus,
    AeternaPartnerCreate,
    AeternaPartnerPublic,
    AeternaStatusPublic,
    AeternaVaultStatus,
)
from app.services.org_access import require_org_role

AETERNA_WORKFLOW_SLUGS = [
    "aeterna-dna-wellness-report",
    "aeterna-longevity-panel-brief",
    "aeterna-pigmentation-consult-brief",
    "aeterna-telomere-panel-review",
    "aeterna-disease-risk-navigator",
    "aeterna-molecular-aging-profile",
    "aeterna-stem-cell-organ-print",
    "aeterna-mrna-reprogramming-brief",
    "aeterna-vet-cat-cryo-restore",
    "aeterna-vet-regen-pod",
    "aeterna-vinci-light-chamber",
    "aeterna-microwave-body-contouring",
    "aeterna-biofusion-micromanipulation",
    "aeterna-dpsc-biomaterial",
    "aeterna-vascular-care-plus",
    "aeterna-vascular-care",
    "aeterna-transdermal-pistol",
    "aeterna-m-receptor-subscription",
    "aeterna-oxygen-carrier",
    "aeterna-synthetic-blood-mamba",
    "aeterna-adhd-support",
    "aeterna-aurea-vita",
    "aeterna-down-syndrome-support",
    "aeterna-substance-coding",
    "aeterna-pulmopure-subscription",
    "aeterna-installation-project",
    "aeterna-dna-pheromone-perfume",
]

ORGAN_PRINT_SLUG = "aeterna-stem-cell-organ-print"
ORGAN_PRINT_PRICE_ACP = Decimal("250000")
MOLECULAR_AGING_SLUG = "aeterna-molecular-aging-profile"
MRNA_REPROGRAMMING_SLUG = "aeterna-mrna-reprogramming-brief"
VET_CAT_CRYO_SLUG = "aeterna-vet-cat-cryo-restore"
VET_CAT_CRYO_PRICE_ACP = Decimal("75000")
VET_REGEN_POD_SLUG = "aeterna-vet-regen-pod"
VET_REGEN_POD_PRICE_ACP = Decimal("180000")
VINCI_LIGHT_SLUG = "aeterna-vinci-light-chamber"
VINCI_LIGHT_PRICE_ACP = Decimal("48000")
MICROWAVE_BODY_SLUG = "aeterna-microwave-body-contouring"
MICROWAVE_BODY_PRICE_ACP = Decimal("52000")
BIOFUSION_SLUG = "aeterna-biofusion-micromanipulation"
BIOFUSION_PRICE_ACP = Decimal("88000")
DPSC_BIOMATERIAL_SLUG = "aeterna-dpsc-biomaterial"
DPSC_BIOMATERIAL_PRICE_ACP = Decimal("65000")
VASCULAR_PLUS_SLUG = "aeterna-vascular-care-plus"
VASCULAR_PLUS_PRICE_ACP = Decimal("54000")
VASCULAR_CARE_SLUG = "aeterna-vascular-care"
VASCULAR_CARE_PRICE_ACP = Decimal("58000")
TRANSDERMAL_SLUG = "aeterna-transdermal-pistol"
TRANSDERMAL_PRICE_ACP = Decimal("46000")
M_RECEPTOR_SLUG = "aeterna-m-receptor-subscription"
M_RECEPTOR_PRICE_ACP = Decimal("12000")
M_RECEPTOR_QUARTERLY_ACP = Decimal("32000")
M_RECEPTOR_ANNUAL_ACP = Decimal("108000")
OXYGEN_CARRIER_SLUG = "aeterna-oxygen-carrier"
OXYGEN_CARRIER_PRICE_ACP = Decimal("92000")
SYNTHETIC_BLOOD_MAMBA_SLUG = "aeterna-synthetic-blood-mamba"
SYNTHETIC_BLOOD_MAMBA_PRICE_ACP = Decimal("98000")
ADHD_SUPPORT_SLUG = "aeterna-adhd-support"
ADHD_SUPPORT_PRICE_ACP = Decimal("42000")
AUREA_VITA_SLUG = "aeterna-aurea-vita"
AUREA_VITA_PRICE_ACP = Decimal("40")
DOWN_SYNDROME_SUPPORT_SLUG = "aeterna-down-syndrome-support"
DOWN_SYNDROME_SUPPORT_PRICE_ACP = Decimal("42000")
SUBSTANCE_CODING_SLUG = "aeterna-substance-coding"
SUBSTANCE_CODING_PRICE_ACP = Decimal("48000")
PULMOPURE_SLUG = "aeterna-pulmopure-subscription"
PULMOPURE_PRICE_ACP = Decimal("14000")
PULMOPURE_QUARTERLY_ACP = Decimal("38000")
PULMOPURE_ANNUAL_ACP = Decimal("128000")
BARSUK_SLUG = "aeterna-barsuk-quantum-pen"
BARSUK_PRICE_ACP = Decimal("36000")
TELEPORT_SLUG = "aeterna-teleport-earphones"
TELEPORT_PRICE_ACP = Decimal("58000")
INSTALLATION_PROJECT_SLUG = "aeterna-installation-project"
INSTALLATION_PROJECT_PRICE_ACP = Decimal("72000")
DNA_PHEROMONE_PERFUME_SLUG = "aeterna-dna-pheromone-perfume"
DNA_PHEROMONE_PERFUME_PRICE_ACP = Decimal("8900")

# 15 hallmark axes for partner-ready molecular aging briefs (blood RNA / PCR-style panels).
# Gene-pair hints are educational placeholders for consult prep — not diagnostic assays.
AETERNA_AGING_HALLMARKS: list[AeternaAgingHallmarkPublic] = [
    AeternaAgingHallmarkPublic(
        id="dna_repair",
        title="DNA repair",
        gene_pair_hint="repair sensor / effector pair",
        theme="genomic_instability",
    ),
    AeternaAgingHallmarkPublic(
        id="telomere_maintenance",
        title="Telomere maintenance",
        gene_pair_hint="shelterin / telomerase-axis pair",
        theme="telomere_attrition",
    ),
    AeternaAgingHallmarkPublic(
        id="epigenetic_regulation",
        title="Epigenetic regulation",
        gene_pair_hint="writer / eraser pair",
        theme="epigenetic_alterations",
    ),
    AeternaAgingHallmarkPublic(
        id="proteostasis",
        title="Proteostasis",
        gene_pair_hint="chaperone / proteasome pair",
        theme="loss_of_proteostasis",
    ),
    AeternaAgingHallmarkPublic(
        id="autophagy",
        title="Autophagy",
        gene_pair_hint="initiation / clearance pair",
        theme="disabled_macroautophagy",
    ),
    AeternaAgingHallmarkPublic(
        id="energy_metabolism",
        title="Energy metabolism",
        gene_pair_hint="glycolysis / OXPHOS balance pair",
        theme="deregulated_nutrient_sensing",
    ),
    AeternaAgingHallmarkPublic(
        id="cellular_senescence",
        title="Cellular senescence",
        gene_pair_hint="SASP / checkpoint pair",
        theme="cellular_senescence",
    ),
    AeternaAgingHallmarkPublic(
        id="stem_cell_maintenance",
        title="Stem-cell maintenance",
        gene_pair_hint="niche / renewal pair",
        theme="stem_cell_exhaustion",
    ),
    AeternaAgingHallmarkPublic(
        id="mitochondrial_function",
        title="Mitochondrial function",
        gene_pair_hint="biogenesis / quality-control pair",
        theme="mitochondrial_dysfunction",
    ),
    AeternaAgingHallmarkPublic(
        id="inflammatory_tone",
        title="Inflammatory tone",
        gene_pair_hint="pro- / anti-inflammatory pair",
        theme="chronic_inflammation",
    ),
    AeternaAgingHallmarkPublic(
        id="intercellular_signaling",
        title="Intercellular signaling",
        gene_pair_hint="ligand / receptor pair",
        theme="altered_communication",
    ),
    AeternaAgingHallmarkPublic(
        id="extracellular_matrix",
        title="Extracellular matrix integrity",
        gene_pair_hint="matrix build / remodel pair",
        theme="tissue_integrity",
    ),
    AeternaAgingHallmarkPublic(
        id="circadian_systemic",
        title="Circadian / systemic regulation",
        gene_pair_hint="clock / effector pair",
        theme="systemic_regulation",
    ),
    AeternaAgingHallmarkPublic(
        id="immune_aging",
        title="Immune aging",
        gene_pair_hint="innate / adaptive balance pair",
        theme="immunosenescence",
    ),
    AeternaAgingHallmarkPublic(
        id="nutrient_sensing",
        title="Nutrient sensing",
        gene_pair_hint="mTOR / AMPK-axis pair",
        theme="nutrient_sensing",
    ),
]

AETERNA_INTENT_DEFAULT_SLUGS: dict[str, str] = {
    AeternaIntentKind.pigmentation_consult.value: "aeterna-pigmentation-consult-brief",
    AeternaIntentKind.telomere_panel_review.value: "aeterna-telomere-panel-review",
    AeternaIntentKind.disease_risk_report.value: "aeterna-disease-risk-navigator",
    AeternaIntentKind.longevity_plan.value: "aeterna-longevity-panel-brief",
    AeternaIntentKind.dna_sandbox_explore.value: "aeterna-dna-wellness-report",
    AeternaIntentKind.partner_clinic_match.value: "aeterna-longevity-panel-brief",
    AeternaIntentKind.organ_bioprint.value: ORGAN_PRINT_SLUG,
    AeternaIntentKind.molecular_aging_profile.value: MOLECULAR_AGING_SLUG,
    AeternaIntentKind.partial_reprogramming_consult.value: MRNA_REPROGRAMMING_SLUG,
    AeternaIntentKind.vet_feline_cryo_restore.value: VET_CAT_CRYO_SLUG,
    AeternaIntentKind.vet_canine_regen_pod.value: VET_REGEN_POD_SLUG,
    AeternaIntentKind.vinci_light_chamber.value: VINCI_LIGHT_SLUG,
    AeternaIntentKind.microwave_body_contouring.value: MICROWAVE_BODY_SLUG,
    AeternaIntentKind.biofusion_micromanipulation.value: BIOFUSION_SLUG,
    AeternaIntentKind.dpsc_biomaterial.value: DPSC_BIOMATERIAL_SLUG,
    AeternaIntentKind.vascular_care_plus.value: VASCULAR_PLUS_SLUG,
    AeternaIntentKind.vascular_care.value: VASCULAR_CARE_SLUG,
    AeternaIntentKind.transdermal_pistol.value: TRANSDERMAL_SLUG,
    AeternaIntentKind.m_receptor_subscription.value: M_RECEPTOR_SLUG,
    AeternaIntentKind.oxygen_carrier_brief.value: OXYGEN_CARRIER_SLUG,
    AeternaIntentKind.synthetic_blood_mamba_brief.value: SYNTHETIC_BLOOD_MAMBA_SLUG,
    AeternaIntentKind.adhd_support_brief.value: ADHD_SUPPORT_SLUG,
    AeternaIntentKind.aurea_vita_brief.value: AUREA_VITA_SLUG,
    AeternaIntentKind.down_syndrome_support_brief.value: DOWN_SYNDROME_SUPPORT_SLUG,
    AeternaIntentKind.substance_coding_brief.value: SUBSTANCE_CODING_SLUG,
    AeternaIntentKind.pulmopure_subscription.value: PULMOPURE_SLUG,
    AeternaIntentKind.installation_project_brief.value: INSTALLATION_PROJECT_SLUG,
    AeternaIntentKind.dna_pheromone_perfume_bottle.value: DNA_PHEROMONE_PERFUME_SLUG,
}

ORGAN_PRINT_HANDOFF_META = {
    "manufacturing_mode": "licensed_partner_bioreactor",
    "unit": "per_organ",
    "price_acp": "250000",
    "primary_cell_source": "autologous_stem_cells",
    "fallback_cell_source": "wisdom_tooth_dental_pulp_stem_cells_dpsc",
    "note": (
        "ANCAP settles ACP and issues a partner handoff brief. "
        "Printing occurs only in a licensed biochemical reactor operated by a verified partner — not a home kit."
    ),
}

MOLECULAR_AGING_META = {
    "panel_axes": 15,
    "sample_hint": "venous_blood_rna_expression_or_partner_pcr_metadata",
    "output_style": "per_hallmark_configuration_not_single_bio_age",
    "sex_aware": True,
    "inspiration_note": (
        "Product framing aligned with public research on multi-gene blood RNA aging panels "
        "(e.g. hallmark-mapped expression profiles) — AETERNA does not claim affiliation with any lab."
    ),
}

VET_CAT_CRYO_META = {
    "mode": "licensed_veterinary_partner",
    "species": "felis_catus",
    "unit": "tissue_bank_intake",
    "price_acp": "75000",
    "architecture": "controlled_rate_freezer_plus_ln2_cryochamber",
    "note": (
        "Conceptual feline tissue cryoconservator-restorer rail. ANCAP settles ACP and issues a "
        "licensed-veterinary-partner intake brief. Not a marketed medical device, not a return-to-life "
        "warranty, and not a DIY cryo protocol."
    ),
}

VET_REGEN_POD_META = {
    "mode": "licensed_veterinary_partner",
    "species": "canis_familiaris",
    "unit": "organ_pathway",
    "price_acp": "180000",
    "architecture": "vet_regen_pod_organ_bank_bioprint_robot_assist",
    "note": (
        "Conceptual canine VET REGEN POD organ-transplant and regeneration chamber. ANCAP settles ACP "
        "and matches a licensed veterinary partner. Infographic survival or speed figures are not product claims."
    ),
}

VINCI_LIGHT_META = {
    "mode": "licensed_phototherapy_partner",
    "unit": "session_protocol_brief",
    "price_acp": "48000",
    "architecture": "full_body_led_uva_red_nir_chamber",
    "bands": {
        "uva": "320-400nm",
        "red": "620-680nm",
        "nir": "780-950nm",
        "pbm_window": "600-950nm",
    },
    "inspiration": "leonardo_sunlight_health_literacy",
    "note": (
        "Conceptual full-body photobiomodulation / light-session chamber. ANCAP settles ACP and issues "
        "a licensed dermatology or phototherapy-partner brief. Not a reconstructed Leonardo invention, "
        "not a marketed medical device, and not a safe-tanning or vitamin-D treatment claim. "
        "UVA on the infographic is a known skin-cancer risk class — partner screening required."
    ),
}

MICROWAVE_BODY_META = {
    "mode": "licensed_aesthetic_dermatology_partner",
    "unit": "session_protocol_brief",
    "price_acp": "52000",
    "architecture": "contact_cooled_microwave_applicator",
    "bands": {
        "ism_2450": "2.45GHz",
        "ism_5800": "5.8GHz",
    },
    "note": (
        "Conceptual contact-cooled microwave body-contouring rail (2.45 / 5.8 GHz ISM). ANCAP settles ACP "
        "and issues a licensed aesthetic or dermatology-partner brief. Not a marketed medical device, not "
        "liposuction, not a weight-loss program, and not a guaranteed adipocyte-clearance or contour result. "
        "Partner screening required (implants, pacemakers, pregnancy, metal, thermal injury history)."
    ),
}

BIOFUSION_META = {
    "mode": "licensed_art_agri_bsl_partner",
    "unit": "session_protocol_brief",
    "price_acp": "88000",
    "architecture": "biofusion_micromanipulation_chamber",
    "rails": {
        "ivf_icsi": "licensed_assisted_reproduction_clinic",
        "plant_pollination": "licensed_agricultural_research_partner",
        "embryo_observation": "clinic_protocol_literacy",
        "microorganism_handling": "licensed_bsl_lab",
    },
    "note": (
        "Conceptual BioFusion micromanipulation chamber (temperature / pH / gas / HEPA-UV architecture). "
        "ANCAP settles ACP and issues a licensed-partner brief. Not a marketed medical device, not a "
        "fertility clinic operated by ANCAP, not a guaranteed pregnancy or viable embryo, not a gene-editing "
        "or pathogen recipe, and not a home ICSI / plant-hybridization kit. Infographic 'genetic manipulations' "
        "copy is partner-lab literacy, not a product."
    ),
}

DPSC_BIOMATERIAL_META = {
    "mode": "licensed_bioreactor_partner",
    "unit": "biomaterial_construct",
    "price_acp": "65000",
    "architecture": "wisdom_tooth_dpsc_expansion",
    "cell_source": "wisdom_tooth_dental_pulp_stem_cells_dpsc",
    "related_organ_print_slug": ORGAN_PRINT_SLUG,
    "note": (
        "Licensed-partner expansion of autologous wisdom-tooth DPSC into a biomaterial construct. "
        "ANCAP settles ACP and issues a bioreactor handoff. Not a full organ (see aeterna-stem-cell-organ-print "
        "at 250,000 ACP), not an FDA/CE cell therapy, and not a home culture kit."
    ),
}

VASCULAR_PLUS_META = {
    "mode": "licensed_phlebology_aesthetic_partner",
    "unit": "session_protocol_brief",
    "price_acp": "54000",
    "architecture": "anhydrous_n2_o2_lightwave_applicator",
    "gas": {
        "mix": "N2+O2",
        "class": "medical_grade_architecture_literacy",
    },
    "note": (
        "Conceptual Vascular Care+ rail: controlled anhydrous nitrogen-oxygen flow plus light-wave "
        "applicator. ANCAP settles ACP and issues a licensed phlebology / vascular / aesthetic-partner brief. "
        "Not a marketed medical device, not a CE/FDA product sold by ANCAP, not a thrombosis or pulmonary-embolism "
        "treatment, and not a guaranteed varicose-vein, oedema, or diabetic-angiopathy result. Infographic "
        "before/after copy is protocol literacy. Partner screening required (DVT, implants, pregnancy, open wounds)."
    ),
}

VASCULAR_CARE_META = {
    "mode": "licensed_phlebology_aesthetic_partner",
    "unit": "session_protocol_brief",
    "price_acp": "58000",
    "architecture": "ultrasound_rf_thermal_applicator",
    "modalities": {
        "ultrasound": "blood_flow_literacy",
        "radiofrequency": "wall_tone_literacy",
        "thermal": "tissue_comfort_literacy",
    },
    "note": (
        "Conceptual Vascular Care rail: ultrasound / radiofrequency / thermal applicator. ANCAP settles ACP "
        "and issues a licensed phlebology / vascular / aesthetic-partner brief. Not a marketed medical device, "
        "not surgery, not a CE/FDA product sold by ANCAP, and not a guaranteed vein-diameter, oedema, or "
        "pain-score claim. Infographic before/after copy is protocol literacy. Partner screening required."
    ),
}

TRANSDERMAL_META = {
    "mode": "licensed_clinic_partner",
    "unit": "session_protocol_brief",
    "price_acp": "46000",
    "architecture": "needle_free_transdermal_pistol",
    "delivery": {
        "route": "aerosol_plus_carrier_gas",
        "gases_literacy": "CO2_N2_O2_or_mix",
    },
    "note": (
        "Conceptual needle-free transdermal pistol (aerosol of actives plus carrier gas). ANCAP settles ACP "
        "and issues a licensed clinic-partner brief. Not a prescription dispenser, not compounding, not a "
        "home injection or mesotherapy kit, not a CE/FDA device sold by ANCAP, and not a guaranteed "
        "transdermal dose, varicose, fat-reduction, or cosmetic result. Partner screening and lawful "
        "substance lists required."
    ),
}

M_RECEPTOR_META = {
    "mode": "licensed_clinic_subscription",
    "unit": "monthly_protocol_retainer",
    "billing": "subscription",
    "price_acp_monthly": "12000",
    "price_acp_quarterly": "32000",
    "price_acp_annual": "108000",
    "architecture": "m_receptor_multimodal_delivery",
    "modules": {
        "transdermal_patch": "licensed_clinic_literacy",
        "iontophoresis": "licensed_clinic_literacy",
        "inhaler_nebulizer": "licensed_clinic_literacy",
        "neurostimulation": "vagus_adjacent_literacy",
    },
    "note": (
        "Conceptual M-receptor delivery and neuromodulation subscription. ANCAP settles ACP per billing "
        "period and issues a licensed-clinic partner brief covering patch, iontophoresis, inhaler/nebulizer, "
        "and vagus-adjacent stimulation as architecture literacy. Not a marketed medical device, not "
        "compounding of scopolamine or any muscarinic agonist/antagonist, not a CE/FDA product sold by ANCAP, "
        "and not a treatment claim for Parkinson, asthma, COPD, arrhythmia, or intraocular pressure. "
        "M1–M5 receptor table on the infographic is literacy, not a dosing guide. Partner screening required."
    ),
}

OXYGEN_CARRIER_META = {
    "mode": "licensed_bioreactor_partner",
    "unit": "architecture_brief",
    "price_acp": "92000",
    "architecture": "hboC_or_pfc_oxygen_carrier",
    "cores_literacy": ["modified_hemoglobin_vesicle", "perfluorocarbon_emulsion"],
    "note": (
        "Conceptual artificial oxygen-carrier brief. ANCAP settles ACP and issues a licensed bioreactor / "
        "transfusion-medicine partner handoff covering hemoglobin-core or PFC-core architecture literacy. "
        "Not a blood product, not compounding of hemoglobin or perfluorocarbon, not a CE/FDA oxygen "
        "therapeutic, and not a manufacturing SOP. Infographic QC and fill diagrams are literacy, not a recipe. "
        "Partner screening required."
    ),
}

SYNTHETIC_BLOOD_MAMBA_META = {
    "mode": "licensed_bioreactor_partner",
    "unit": "architecture_brief",
    "price_acp": "98000",
    "architecture": "hboc_pfc_black_mamba_peptide_architecture",
    "layers_literacy": [
        "oxygen_carrier_core",
        "lipid_shell",
        "polymer_mesh",
        "modified_black_mamba_peptides",
        "delivery_vesicle",
        "immune_management_sensors",
    ],
    "note": (
        "Conceptual synthetic-blood architecture brief with modified Black Mamba peptide literacy. "
        "ANCAP settles ACP and issues a licensed bioreactor / transfusion-medicine partner handoff. "
        "Not a blood product, not compounding of venom peptides, hemoglobin or PFC, not a CE/FDA "
        "therapeutic, not a toxin recipe, and not a manufacturing SOP. Infographic stages and "
        "'controlled dose' callouts are architecture literacy, not a dosing guide. Partner screening required."
    ),
}

ADHD_SUPPORT_META = {
    "mode": "licensed_clinician_partner",
    "unit": "support_brief",
    "price_acp": "42000",
    "architecture": "adhd_support_partner_literacy",
    "themes_literacy": [
        "attention_and_task_completion",
        "planning_and_impulse_control",
        "emotion_regulation",
        "peer_and_team_skills",
        "self_esteem",
        "comorbid_risk_literacy",
    ],
    "note": (
        "Conceptual ADHD / СДВГ support brief. ANCAP settles ACP and issues a licensed clinician / "
        "child-psychiatry or neurology partner handoff covering attention, planning, emotion, and "
        "school-adaptation literacy. Not a diagnosis, not a prescription, not stimulant compounding, "
        "not a CE/FDA drug, and not a guaranteed academic or financial outcome. Infographic "
        "'billionaire path' steps are motivational literacy, not a promise. Partner screening required; "
        "caregivers retain clinical decision rights with the licensed clinician."
    ),
}

AUREA_VITA_META = {
    "mode": "licensed_lifestyle_longevity_partner",
    "unit": "vita_brief",
    "price_acp": "40",
    "architecture": "aurea_vita_quality_of_life_literacy",
    "themes_literacy": [
        "quality_of_life_acceleration",
        "longevity_literacy",
        "nutrition_recommendations",
        "sport_and_movement",
        "everyday_health_hygiene",
        "sleep_and_recovery",
    ],
    "note": (
        "AUREA Vita is a licensed lifestyle / longevity / nutrition-sport partner brief for rapid "
        "quality-of-life literacy: nutrition, sport, health hygiene, sleep, and longevity framing. "
        "ANCAP settles 40 ACP and issues a partner handoff. Not medical advice, not a diagnosis, "
        "not a prescription, not a CE/FDA drug or device, not a guaranteed lifespan or performance "
        "outcome. Partner screening required; clinical decisions stay with the licensed partner."
    ),
}

DOWN_SYNDROME_SUPPORT_META = {
    "mode": "licensed_clinician_partner",
    "unit": "support_brief",
    "price_acp": "42000",
    "architecture": "down_syndrome_support_partner_literacy",
    "themes_literacy": [
        "early_intervention",
        "family_caregiver_coordination",
        "learning_and_skills_adaptation",
        "health_partner_screening",
        "community_peer_support",
        "developmental_literacy",
    ],
    "note": (
        "Conceptual Down syndrome support brief. ANCAP settles ACP and issues a licensed developmental "
        "pediatrics / genetics / child-neurology partner handoff covering early intervention, family "
        "support, and school-adaptation literacy. Not a cure for Down syndrome, not a diagnosis, not "
        "gene therapy or CRISPR sold by ANCAP, not a prescription, and not a guaranteed developmental "
        "or life outcome. Partner screening required; caregivers retain clinical decision rights with "
        "the licensed clinician."
    ),
}


SUBSTANCE_CODING_META = {
    "mode": "licensed_clinician_partner",
    "unit": "coding_support_brief",
    "price_acp": "48000",
    "architecture": "substance_coding_partner_literacy",
    "modalities_literacy": [
        "light_protocol_literacy",
        "clinic_only_substance_protocol_literacy",
        "clinical_hypnosis_literacy",
        "non_essential_psychoactive_dependence_literacy",
        "relapse_risk_literacy",
        "emergency_care_handoff",
    ],
    "note": (
        "Conceptual substance-coding support brief. ANCAP settles ACP and issues a licensed "
        "addiction-medicine / narcology / clinical-hypnosis partner handoff covering light-protocol, "
        "clinic-only substance, and hypnosis literacy aimed at psychoactive substances that are not "
        "necessary for life. Not a coding session performed by ANCAP, not a guarantee of abstinence, "
        "not compounding or sale of controlled substances by ANCAP, not hypnosis sold as entertainment, "
        "and not a substitute for emergency or psychiatric care. Clinical care occurs only under a "
        "licensed clinician after screening."
    ),
}


BARSUK_META = {
    "mode": "licensed_secure_comms_partner",
    "unit": "architecture_brief",
    "price_acp": "36000",
    "architecture": "barsuk_quantum_pen_partner_literacy",
    "themes_literacy": [
        "pen_form_secure_comms",
        "quantum_crypto_literacy",
        "sensor_nav_literacy",
        "smart_ink_literacy",
    ],
    "note": (
        "Conceptual Project Barsuk / quantum-pen brief. ANCAP settles ACP and issues a licensed "
        "secure-comms / identity partner handoff. Not a Parker Pen Company product, not a CE/FDA device, "
        "not a military weapon, not unbreakable cryptography, and not a field kit sold by ANCAP. "
        "Infographic ranges and materials are fiction / architecture literacy. Partner screening required."
    ),
}

TELEPORT_META = {
    "mode": "licensed_partner_fiction_brief",
    "unit": "architecture_brief",
    "price_acp": "58000",
    "architecture": "teleport_earphones_medevac_literacy",
    "themes_literacy": [
        "fictional_medevac_teleport",
        "quantum_comms_literacy",
        "neural_interface_literacy",
        "field_case_ruggedization_literacy",
    ],
    "note": (
        "Conceptual AIRPODS T-2026 / teleport-earphones brief focused on medical-evacuation fiction. "
        "ANCAP settles ACP and issues a licensed partner handoff. Not an Apple product, not a real "
        "teleporter, not a military weapon system, not a guaranteed 10,000 km jump, and not a combat "
        "ops kit. Infographic ranges and combat panels are sci-fi literacy; ANCAP frames the SKU around "
        "rescue / medevac themes only. Partner screening required."
    ),
}

INSTALLATION_PROJECT_META = {
    "mode": "licensed_neonatology_nutrition_partner",
    "unit": "architecture_brief",
    "price_acp": "72000",
    "architecture": "installation_project_neonatal_partner_literacy",
    "themes_literacy": [
        "high_protein_infant_formula_line",
        "natural_synthetic_milk_gmp_literacy",
        "neonatal_hyperbaric_chamber_literacy",
        "premature_infant_nursing_literacy",
    ],
    "modules": {
        "milk_line_capacity_literacy": "up_to_1000_l_per_day_conceptual",
        "formats": ["liquid_milk", "dry_powder"],
        "hyperbaric_pressure_ata_literacy": "1.5_to_2.0",
        "hyperbaric_temp_c_literacy": "36_to_37",
        "capacity_newborns_literacy": "1_to_2",
        "standards_literacy": ["GMP", "medical_partner_standards"],
    },
    "note": (
        "Conceptual Installation Project (Проект Установки) brief. ANCAP settles ACP and issues a licensed "
        "neonatology / infant-nutrition / perinatal partner handoff covering high-protein natural-synthetic "
        "milk production literacy and neonatal hyperbaric-chamber architecture. Not infant formula sold by "
        "ANCAP, not a CE/FDA device, not home hyperbaric oxygen therapy, not a milk factory title deed, and "
        "not a guaranteed reduction of rickets, anemia, infection, or developmental delay. Infographic "
        "capacities, ATA ranges, and composition callouts are partner architecture literacy. Partner "
        "screening required."
    ),
}

DNA_PHEROMONE_PERFUME_META = {
    "mode": "licensed_cosmetic_fragrance_partner",
    "unit": "per_bottle",
    "quantity": 1,
    "price_acp": "8900",
    "architecture": "dna_matched_pheromone_perfume_literacy",
    "themes_literacy": [
        "olfactory_profile_from_vault_hash",
        "cosmetic_pheromone_blend_literacy",
        "skin_safe_fragrance_carrier",
        "partner_fill_and_label",
    ],
    "note": (
        "Sale unit is exactly one bottle. ANCAP settles 8,900 ACP and issues a licensed cosmetic / "
        "fragrance partner handoff. Optional DNA-vault content hash informs olfactory-profile literacy — "
        "genome bytes are never uploaded. Not a drug, not an aphrodisiac medical claim, not a guaranteed "
        "attraction or relationship outcome, not CE/FDA pheromone medicine, and not compounding of "
        "controlled substances. Partner screening required."
    ),
}

PULMOPURE_META = {
    "mode": "licensed_clinic_subscription",
    "unit": "monthly_protocol_retainer",
    "billing": "subscription",
    "price_acp_monthly": "14000",
    "price_acp_quarterly": "38000",
    "price_acp_annual": "128000",
    "architecture": "pulmopure_gas_vibration_partner_literacy",
    "modules": {
        "gas_vibration": "licensed_clinic_literacy",
        "medical_gas_mix": "partner_protocol_literacy_only",
        "lavender_oil_atomizer": "aromatherapy_literacy",
        "soft_standard_intensive_modes": "partner_mode_literacy",
    },
    "note": (
        "Conceptual PulmoPure lung-care subscription. ANCAP settles ACP per billing period and issues a "
        "licensed pulmonology / respiratory / smoking-cessation clinic partner brief covering gas-vibration, "
        "gas-mix, and lavender-oil architecture literacy. Not a CE/FDA device sold by ANCAP, not ozone "
        "therapy, not medical-gas compounding, not a home respiratory kit, and not a guaranteed tar-clearance, "
        "cough reduction, or 'clean lungs' outcome. Soft / Standard / Intensive mode callouts and before/after "
        "alveoli artwork are protocol literacy, not product claims. Partner screening required "
        "(asthma, COPD, pneumothorax history, pregnancy, ozone sensitivity)."
    ),
}

MRNA_REPROGRAMMING_META = {
    "mode": "licensed_partner_consult_only",
    "delivery_literacy": "mrna_in_lipid_nanoparticle_lnp",
    "goal": "partial_reprogramming_keep_cell_identity",
    "not": [
        "issued_us_patent_until_grant_issues",
        "approved_drug",
        "full_pluripotent_reset",
        "lipid_recipe",
        "mrna_sequence",
        "wet_lab_protocol",
    ],
    "citation_note": (
        "Public journalism (Inc. Russia 8 Sep 2026; Daewoong / USPTO notice of allowance "
        "announced 27 Aug 2026) on ionizable lipids for the eTurna LNP platform. "
        "ANCAP is not affiliated with Daewoong Pharmaceutical, Turn Biotechnologies, "
        "HanAll Biopharma, or eTurna."
    ),
}

_COMPLIANCE = (
    "AETERNA sells ACP-paid analysis, consult briefs, and licensed-partner handoffs only. "
    "No DIY CRISPR/Cas9 protocols, gene synthesis, LNP formulation recipes, mRNA sequences, "
    "or unlicensed enhancement procedures. "
    "Molecular aging profiles, partial-reprogramming briefs, and veterinary organ rails "
    "are educational / partner-prep — not clinical or veterinary diagnoses, not approved "
    "anti-aging drugs, and not marketed medical devices."
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _feature_enabled() -> bool:
    return bool(getattr(get_settings(), "ff_aeterna", False))


def _vault_public(row: AeternaDnaVaultEntry) -> AeternaDnaVaultPublic:
    return AeternaDnaVaultPublic(
        id=uuid.UUID(str(row.id)),
        org_id=uuid.UUID(str(row.org_id)) if row.org_id else None,
        owner_user_id=uuid.UUID(str(row.owner_user_id)),
        label=row.label,
        source=row.source,
        source_uri=row.source_uri,
        content_sha256=row.content_sha256,
        format_hint=row.format_hint,
        status=row.status,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _order_public(row: AeternaIntentOrder) -> AeternaIntentOrderPublic:
    return AeternaIntentOrderPublic(
        id=uuid.UUID(str(row.id)),
        org_id=uuid.UUID(str(row.org_id)) if row.org_id else None,
        owner_user_id=uuid.UUID(str(row.owner_user_id)),
        intent_kind=row.intent_kind,
        vault_id=uuid.UUID(str(row.vault_id)) if row.vault_id else None,
        workflow_slug=row.workflow_slug,
        status=row.status,
        budget_acp=row.budget_acp,
        notes=row.notes,
        metadata_json=dict(row.metadata_json or {}),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _partner_public(row: AeternaPartner) -> AeternaPartnerPublic:
    return AeternaPartnerPublic(
        id=uuid.UUID(str(row.id)),
        org_id=uuid.UUID(str(row.org_id)),
        name=row.name,
        jurisdiction=row.jurisdiction,
        license_ref=row.license_ref,
        website=row.website,
        supported_intents=list(row.supported_intents or []),
        verified=bool(row.verified),
        created_at=row.created_at,
    )


async def division_status(session: AsyncSession) -> AeternaStatusPublic:
    enabled = _feature_enabled()
    vaults = (await session.execute(select(func.count()).select_from(AeternaDnaVaultEntry))).scalar_one()
    orders = (await session.execute(select(func.count()).select_from(AeternaIntentOrder))).scalar_one()
    partners = (
        await session.execute(
            select(func.count()).select_from(AeternaPartner).where(AeternaPartner.verified.is_(True))
        )
    ).scalar_one()
    return AeternaStatusPublic(
        feature_enabled=enabled,
        tagline=(
            "Eternal life rails: DNA vault, 15-axis molecular aging profile, "
            "partial mRNA-reprogramming consults, stem-cell organ print, "
            "veterinary tissue-cryo / VET REGEN POD partner rails, Vinci light chamber, microwave body contouring, "
            "BioFusion micromanipulation chamber, wisdom-tooth DPSC biomaterial, "
            "Vascular Care+ gas-light rail, Vascular Care ultrasound/RF rail, needle-free transdermal pistol, "
            "M-receptor delivery subscription, artificial oxygen-carrier brief, "
            "synthetic-blood / Black Mamba peptide architecture brief, ADHD / СДВГ support brief, "
            "PulmoPure lung-care subscription, Installation Project neonatal nutrition / hyperbaric "
            "partner brief, licensed longevity partners."
        ),
        vault_entries=int(vaults or 0),
        intent_orders=int(orders or 0),
        partners_verified=int(partners or 0),
        workflow_slugs=list(AETERNA_WORKFLOW_SLUGS),
        sequencing_import_hint=(
            "Hash Sequencing.com / VCF exports or partner blood-RNA panel metadata locally "
            "(streaming SHA-256), then POST only content_sha256 + tiny metadata. "
            "Do not upload hg38/CRAM/FASTA or raw FASTQ to ANCAP — disk is hash-only."
        ),
        compliance_note=_COMPLIANCE,
        next_gate="Enable FF_AETERNA" if not enabled else "Partner verification queue + licensed checkout UX",
        aging_hallmarks=list(AETERNA_AGING_HALLMARKS),
        molecular_aging_note=(
            "Goal is an individual configuration of aging processes "
            "(DNA repair, proteostasis, energy metabolism, senescence, …) — "
            "not one universal \"you are biologically N years old\" score. Sex-aware models preferred."
        ),
        reprogramming_note=(
            "Partial reprogramming = restore some youthful cell functions without erasing identity. "
            "eTurna-style LNP mRNA delivery is cited as public patent-literacy only "
            "(USPTO notice of allowance, Aug 2026) — not a therapy ANCAP sells or compounds."
        ),
        vet_regen_note=(
            "Feline cryoconservator-restorer and canine VET REGEN POD listings are licensed-veterinary "
            "partner intakes. Infographics are conceptual architecture — not a marketed device and not "
            "a survival-rate or return-to-life claim."
        ),
        vinci_light_note=(
            "Vinci light chamber listings are licensed phototherapy / dermatology partner intakes. "
            "Infographics are conceptual architecture inspired by Leonardo-era sunlight literacy — "
            "not a reconstructed invention, not a CE/FDA device, and not a safe-tanning claim."
        ),
        microwave_body_note=(
            "Microwave body-contouring listings are licensed aesthetic / dermatology partner intakes "
            "for a contact-cooled 2.45 / 5.8 GHz applicator. Infographics are conceptual architecture — "
            "not a marketed device, not liposuction, and not a guaranteed fat-loss claim."
        ),
        biofusion_note=(
            "BioFusion micromanipulation listings are licensed ART / agricultural / BSL-lab partner intakes. "
            "Infographics are conceptual architecture — not a fertility clinic, not a guaranteed embryo or "
            "pregnancy, and not a gene-editing or pathogen kit."
        ),
        dpsc_biomaterial_note=(
            "Wisdom-tooth DPSC biomaterial listings expand autologous dental pulp stem cells in a licensed "
            "bioreactor. They are not a full organ print and not a marketed cell therapy."
        ),
        vascular_care_plus_note=(
            "Vascular Care+ listings are licensed phlebology / vascular / aesthetic partner intakes for an "
            "anhydrous N2+O2 plus light-wave applicator. Infographics are conceptual architecture — not a "
            "marketed device, not a thrombosis treatment, and not a guaranteed varicose-vein claim."
        ),
        vascular_care_note=(
            "Vascular Care listings are licensed phlebology / vascular / aesthetic partner intakes for an "
            "ultrasound / radiofrequency / thermal applicator. Infographics are conceptual architecture — not "
            "a marketed device, not surgery, and not a guaranteed vein-diameter claim."
        ),
        transdermal_pistol_note=(
            "Needle-free transdermal pistol listings are licensed clinic-partner intakes for aerosol plus "
            "carrier-gas delivery. Infographics are conceptual architecture — not a prescription dispenser, "
            "not compounding, and not a guaranteed dose or cosmetic result."
        ),
        m_receptor_note=(
            "M-receptor listings are licensed-clinic subscriptions for multimodal delivery and neuromodulation "
            "literacy (patch, iontophoresis, inhaler, vagus-adjacent stimulation). Infographics are conceptual "
            "architecture — not compounding, not a CE/FDA device, and not a treatment claim."
        ),
        oxygen_carrier_note=(
            "Oxygen-carrier listings are licensed bioreactor / transfusion-medicine partner intakes for "
            "hemoglobin-vesicle or PFC-emulsion architecture literacy. Infographics are conceptual — not a "
            "blood product, not compounding, and not a CE/FDA oxygen therapeutic."
        ),
        synthetic_blood_mamba_note=(
            "Synthetic-blood / Black Mamba peptide architecture listings are licensed bioreactor / "
            "transfusion-medicine partner intakes. Infographics are conceptual — not a blood product, "
            "not venom compounding, not a toxin SOP, and not a CE/FDA therapeutic."
        ),
        adhd_support_note=(
            "ADHD / СДВГ support listings are licensed clinician partner intakes for attention, planning, "
            "emotion, and school-adaptation literacy. Infographics are motivational — not a diagnosis, "
            "not a prescription, not stimulant compounding, and not a guaranteed financial outcome."
        ),
        aurea_vita_note=(
            "AUREA Vita listings are licensed lifestyle / longevity partner intakes for rapid quality-of-life "
            "literacy: nutrition, sport, health hygiene, sleep, and longevity framing. Infographics are "
            "motivational — not medical advice, not a diagnosis, not a prescription, and not a guaranteed "
            "lifespan or performance outcome."
        ),
        down_syndrome_support_note=(
            "Down syndrome support listings are licensed developmental pediatrics / genetics / "
            "child-neurology partner intakes for early intervention and family literacy. Infographics "
            "are support architecture — not a cure, not a diagnosis, not gene therapy sold by ANCAP, "
            "and not a guaranteed developmental outcome."
        ),
        substance_coding_note=(
            "Substance-coding listings are licensed addiction-medicine / narcology / clinical-hypnosis "
            "partner intakes for light, clinic-only substance, and hypnosis literacy aimed at non-essential "
            "psychoactive dependence. Infographics are architecture — not a coding session by ANCAP, "
            "not guaranteed abstinence, and not controlled-substance compounding by ANCAP."
        ),
        pulmopure_note=(
            "PulmoPure listings are licensed pulmonology / respiratory clinic subscriptions for "
            "gas-vibration and lavender-oil architecture literacy. Infographics are conceptual — not a "
            "CE/FDA device, not ozone therapy, not medical-gas compounding, and not a guaranteed "
            "tar-clearance or 'clean lungs' outcome."
        ),
        barsuk_note="Retired from public launch catalog.",
        teleport_earphones_note="Retired from public launch catalog.",
        installation_project_note=(
            "Installation Project listings are licensed neonatology / infant-nutrition partner intakes for "
            "high-protein milk-line and neonatal hyperbaric-chamber literacy. Infographics are conceptual — "
            "not formula sold by ANCAP, not a CE/FDA device, not home HBO, and not a guaranteed clinical outcome."
        ),
        dna_pheromone_perfume_note=(
            "DNA-matched pheromone perfume is sold per bottle (8,900 ACP). Optional DNA-vault hash informs "
            "olfactory-profile literacy for a licensed cosmetic partner fill — not a drug, not an aphrodisiac "
            "claim, and not a guaranteed attraction outcome."
        ),
    )


async def create_vault_entry(
    session: AsyncSession, *, user_id: str, body: AeternaDnaVaultCreate, org_id: str | None = None
) -> AeternaDnaVaultPublic:
    if not _feature_enabled():
        raise HTTPException(status_code=503, detail="AETERNA feature flag disabled")
    if not body.consent_acknowledged:
        raise HTTPException(status_code=400, detail="consent_acknowledged required")
    if org_id:
        await require_org_role(session, org_id, user_id, OrgRoleEnum.member)
    now = _utcnow()
    row = AeternaDnaVaultEntry(
        org_id=org_id,
        owner_user_id=user_id,
        label=body.label.strip(),
        source=body.source.value,
        source_uri=body.source_uri,
        content_sha256=body.content_sha256.lower(),
        format_hint=body.format_hint.strip().lower() or "vcf",
        status=AeternaVaultStatus.indexed.value,
        metadata_json=body.metadata_json or {},
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    return _vault_public(row)


async def list_vault_entries(
    session: AsyncSession, *, user_id: str, org_id: str | None = None
) -> list[AeternaDnaVaultPublic]:
    if org_id:
        await require_org_role(session, org_id, user_id, OrgRoleEnum.viewer)
        stmt = select(AeternaDnaVaultEntry).where(AeternaDnaVaultEntry.org_id == org_id)
    else:
        stmt = select(AeternaDnaVaultEntry).where(AeternaDnaVaultEntry.owner_user_id == user_id)
    stmt = stmt.order_by(AeternaDnaVaultEntry.created_at.desc())
    return [_vault_public(r) for r in (await session.execute(stmt)).scalars().all()]


async def create_intent_order(
    session: AsyncSession, *, user_id: str, body: AeternaIntentOrderCreate, org_id: str | None = None
) -> AeternaIntentOrderPublic:
    if not _feature_enabled():
        raise HTTPException(status_code=503, detail="AETERNA feature flag disabled")
    if body.intent_kind == AeternaIntentKind.barsuk_quantum_pen_brief:
        raise HTTPException(
            status_code=410,
            detail="barsuk_quantum_pen_brief retired from public launch catalog",
        )
    if body.intent_kind == AeternaIntentKind.teleport_earphones_brief:
        raise HTTPException(
            status_code=410,
            detail="teleport_earphones_brief retired from public launch catalog",
        )
    if org_id:
        await require_org_role(session, org_id, user_id, OrgRoleEnum.member)
    if body.vault_id:
        vault = await session.get(AeternaDnaVaultEntry, str(body.vault_id))
        if vault is None:
            raise HTTPException(status_code=404, detail="DNA vault entry not found")
        if vault.owner_user_id != user_id and (not org_id or vault.org_id != org_id):
            raise HTTPException(status_code=403, detail="Vault entry not accessible")
    slug = body.workflow_slug or AETERNA_INTENT_DEFAULT_SLUGS.get(body.intent_kind.value)
    if slug and slug not in AETERNA_WORKFLOW_SLUGS:
        raise HTTPException(status_code=400, detail="Unknown AETERNA workflow_slug")
    if body.intent_kind == AeternaIntentKind.organ_bioprint:
        if slug and slug != ORGAN_PRINT_SLUG:
            raise HTTPException(
                status_code=400,
                detail="organ_bioprint requires workflow_slug aeterna-stem-cell-organ-print",
            )
        slug = ORGAN_PRINT_SLUG
        if body.budget_acp < ORGAN_PRINT_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="organ_bioprint budget_acp must be at least 250000 ACP per organ",
            )
    meta = dict(body.metadata_json or {})
    if body.intent_kind == AeternaIntentKind.organ_bioprint:
        for key, value in ORGAN_PRINT_HANDOFF_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.molecular_aging_profile:
        if slug and slug != MOLECULAR_AGING_SLUG:
            raise HTTPException(
                status_code=400,
                detail="molecular_aging_profile requires workflow_slug aeterna-molecular-aging-profile",
            )
        slug = MOLECULAR_AGING_SLUG
        for key, value in MOLECULAR_AGING_META.items():
            meta.setdefault(key, value)
        meta.setdefault(
            "hallmark_ids",
            [h.id for h in AETERNA_AGING_HALLMARKS],
        )
    if body.intent_kind == AeternaIntentKind.partial_reprogramming_consult:
        if slug and slug != MRNA_REPROGRAMMING_SLUG:
            raise HTTPException(
                status_code=400,
                detail="partial_reprogramming_consult requires workflow_slug aeterna-mrna-reprogramming-brief",
            )
        slug = MRNA_REPROGRAMMING_SLUG
        if body.budget_acp < Decimal("1000000"):
            raise HTTPException(
                status_code=400,
                detail="partial_reprogramming_consult budget_acp must be at least 1000000 ACP",
            )
        for key, value in MRNA_REPROGRAMMING_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.vet_feline_cryo_restore:
        if slug and slug != VET_CAT_CRYO_SLUG:
            raise HTTPException(
                status_code=400,
                detail="vet_feline_cryo_restore requires workflow_slug aeterna-vet-cat-cryo-restore",
            )
        slug = VET_CAT_CRYO_SLUG
        if body.budget_acp < VET_CAT_CRYO_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="vet_feline_cryo_restore budget_acp must be at least 75000 ACP",
            )
        for key, value in VET_CAT_CRYO_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.vet_canine_regen_pod:
        if slug and slug != VET_REGEN_POD_SLUG:
            raise HTTPException(
                status_code=400,
                detail="vet_canine_regen_pod requires workflow_slug aeterna-vet-regen-pod",
            )
        slug = VET_REGEN_POD_SLUG
        if body.budget_acp < VET_REGEN_POD_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="vet_canine_regen_pod budget_acp must be at least 180000 ACP",
            )
        for key, value in VET_REGEN_POD_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.vinci_light_chamber:
        if slug and slug != VINCI_LIGHT_SLUG:
            raise HTTPException(
                status_code=400,
                detail="vinci_light_chamber requires workflow_slug aeterna-vinci-light-chamber",
            )
        slug = VINCI_LIGHT_SLUG
        if body.budget_acp < VINCI_LIGHT_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="vinci_light_chamber budget_acp must be at least 48000 ACP",
            )
        for key, value in VINCI_LIGHT_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.microwave_body_contouring:
        if slug and slug != MICROWAVE_BODY_SLUG:
            raise HTTPException(
                status_code=400,
                detail="microwave_body_contouring requires workflow_slug aeterna-microwave-body-contouring",
            )
        slug = MICROWAVE_BODY_SLUG
        if body.budget_acp < MICROWAVE_BODY_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="microwave_body_contouring budget_acp must be at least 52000 ACP",
            )
        for key, value in MICROWAVE_BODY_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.biofusion_micromanipulation:
        if slug and slug != BIOFUSION_SLUG:
            raise HTTPException(
                status_code=400,
                detail="biofusion_micromanipulation requires workflow_slug aeterna-biofusion-micromanipulation",
            )
        slug = BIOFUSION_SLUG
        if body.budget_acp < BIOFUSION_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="biofusion_micromanipulation budget_acp must be at least 88000 ACP",
            )
        for key, value in BIOFUSION_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.dpsc_biomaterial:
        if slug and slug != DPSC_BIOMATERIAL_SLUG:
            raise HTTPException(
                status_code=400,
                detail="dpsc_biomaterial requires workflow_slug aeterna-dpsc-biomaterial",
            )
        slug = DPSC_BIOMATERIAL_SLUG
        if body.budget_acp < DPSC_BIOMATERIAL_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="dpsc_biomaterial budget_acp must be at least 65000 ACP",
            )
        for key, value in DPSC_BIOMATERIAL_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.vascular_care_plus:
        if slug and slug != VASCULAR_PLUS_SLUG:
            raise HTTPException(
                status_code=400,
                detail="vascular_care_plus requires workflow_slug aeterna-vascular-care-plus",
            )
        slug = VASCULAR_PLUS_SLUG
        if body.budget_acp < VASCULAR_PLUS_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="vascular_care_plus budget_acp must be at least 54000 ACP",
            )
        for key, value in VASCULAR_PLUS_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.vascular_care:
        if slug and slug != VASCULAR_CARE_SLUG:
            raise HTTPException(
                status_code=400,
                detail="vascular_care requires workflow_slug aeterna-vascular-care",
            )
        slug = VASCULAR_CARE_SLUG
        if body.budget_acp < VASCULAR_CARE_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="vascular_care budget_acp must be at least 58000 ACP",
            )
        for key, value in VASCULAR_CARE_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.transdermal_pistol:
        if slug and slug != TRANSDERMAL_SLUG:
            raise HTTPException(
                status_code=400,
                detail="transdermal_pistol requires workflow_slug aeterna-transdermal-pistol",
            )
        slug = TRANSDERMAL_SLUG
        if body.budget_acp < TRANSDERMAL_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="transdermal_pistol budget_acp must be at least 46000 ACP",
            )
        for key, value in TRANSDERMAL_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.m_receptor_subscription:
        if slug and slug != M_RECEPTOR_SLUG:
            raise HTTPException(
                status_code=400,
                detail="m_receptor_subscription requires workflow_slug aeterna-m-receptor-subscription",
            )
        slug = M_RECEPTOR_SLUG
        if body.budget_acp < M_RECEPTOR_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="m_receptor_subscription budget_acp must be at least 12000 ACP per month",
            )
        for key, value in M_RECEPTOR_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.oxygen_carrier_brief:
        if slug and slug != OXYGEN_CARRIER_SLUG:
            raise HTTPException(
                status_code=400,
                detail="oxygen_carrier_brief requires workflow_slug aeterna-oxygen-carrier",
            )
        slug = OXYGEN_CARRIER_SLUG
        if body.budget_acp < OXYGEN_CARRIER_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="oxygen_carrier_brief budget_acp must be at least 92000 ACP",
            )
        for key, value in OXYGEN_CARRIER_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.synthetic_blood_mamba_brief:
        if slug and slug != SYNTHETIC_BLOOD_MAMBA_SLUG:
            raise HTTPException(
                status_code=400,
                detail="synthetic_blood_mamba_brief requires workflow_slug aeterna-synthetic-blood-mamba",
            )
        slug = SYNTHETIC_BLOOD_MAMBA_SLUG
        if body.budget_acp < SYNTHETIC_BLOOD_MAMBA_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="synthetic_blood_mamba_brief budget_acp must be at least 98000 ACP",
            )
        for key, value in SYNTHETIC_BLOOD_MAMBA_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.adhd_support_brief:
        if slug and slug != ADHD_SUPPORT_SLUG:
            raise HTTPException(
                status_code=400,
                detail="adhd_support_brief requires workflow_slug aeterna-adhd-support",
            )
        slug = ADHD_SUPPORT_SLUG
        if body.budget_acp < ADHD_SUPPORT_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="adhd_support_brief budget_acp must be at least 42000 ACP",
            )
        for key, value in ADHD_SUPPORT_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.aurea_vita_brief:
        if slug and slug != AUREA_VITA_SLUG:
            raise HTTPException(
                status_code=400,
                detail="aurea_vita_brief requires workflow_slug aeterna-aurea-vita",
            )
        slug = AUREA_VITA_SLUG
        if body.budget_acp < AUREA_VITA_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="aurea_vita_brief budget_acp must be at least 40 ACP",
            )
        for key, value in AUREA_VITA_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.down_syndrome_support_brief:
        if slug and slug != DOWN_SYNDROME_SUPPORT_SLUG:
            raise HTTPException(
                status_code=400,
                detail="down_syndrome_support_brief requires workflow_slug aeterna-down-syndrome-support",
            )
        slug = DOWN_SYNDROME_SUPPORT_SLUG
        if body.budget_acp < DOWN_SYNDROME_SUPPORT_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="down_syndrome_support_brief budget_acp must be at least 42000 ACP",
            )
        for key, value in DOWN_SYNDROME_SUPPORT_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.substance_coding_brief:
        if slug and slug != SUBSTANCE_CODING_SLUG:
            raise HTTPException(
                status_code=400,
                detail="substance_coding_brief requires workflow_slug aeterna-substance-coding",
            )
        slug = SUBSTANCE_CODING_SLUG
        if body.budget_acp < SUBSTANCE_CODING_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="substance_coding_brief budget_acp must be at least 48000 ACP",
            )
        for key, value in SUBSTANCE_CODING_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.pulmopure_subscription:
        if slug and slug != PULMOPURE_SLUG:
            raise HTTPException(
                status_code=400,
                detail="pulmopure_subscription requires workflow_slug aeterna-pulmopure-subscription",
            )
        slug = PULMOPURE_SLUG
        if body.budget_acp < PULMOPURE_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="pulmopure_subscription budget_acp must be at least 14000 ACP per month",
            )
        for key, value in PULMOPURE_META.items():
            meta.setdefault(key, value)

    if body.intent_kind == AeternaIntentKind.installation_project_brief:
        if slug and slug != INSTALLATION_PROJECT_SLUG:
            raise HTTPException(
                status_code=400,
                detail="installation_project_brief requires workflow_slug aeterna-installation-project",
            )
        slug = INSTALLATION_PROJECT_SLUG
        if body.budget_acp < INSTALLATION_PROJECT_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="installation_project_brief budget_acp must be at least 72000 ACP",
            )
        for key, value in INSTALLATION_PROJECT_META.items():
            meta.setdefault(key, value)
    if body.intent_kind == AeternaIntentKind.dna_pheromone_perfume_bottle:
        if slug and slug != DNA_PHEROMONE_PERFUME_SLUG:
            raise HTTPException(
                status_code=400,
                detail="dna_pheromone_perfume_bottle requires workflow_slug aeterna-dna-pheromone-perfume",
            )
        slug = DNA_PHEROMONE_PERFUME_SLUG
        if body.budget_acp < DNA_PHEROMONE_PERFUME_PRICE_ACP:
            raise HTTPException(
                status_code=400,
                detail="dna_pheromone_perfume_bottle budget_acp must be at least 8900 ACP per bottle",
            )
        for key, value in DNA_PHEROMONE_PERFUME_META.items():
            meta.setdefault(key, value)
        meta["quantity"] = 1
        meta["unit"] = "per_bottle"
    now = _utcnow()
    row = AeternaIntentOrder(
        org_id=org_id,
        owner_user_id=user_id,
        intent_kind=body.intent_kind.value,
        vault_id=str(body.vault_id) if body.vault_id else None,
        workflow_slug=slug,
        status=AeternaOrderStatus.draft.value,
        budget_acp=body.budget_acp,
        notes=body.notes,
        metadata_json=meta,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    return _order_public(row)


async def list_intent_orders(
    session: AsyncSession, *, user_id: str, org_id: str | None = None
) -> list[AeternaIntentOrderPublic]:
    if org_id:
        await require_org_role(session, org_id, user_id, OrgRoleEnum.viewer)
        stmt = select(AeternaIntentOrder).where(AeternaIntentOrder.org_id == org_id)
    else:
        stmt = select(AeternaIntentOrder).where(AeternaIntentOrder.owner_user_id == user_id)
    stmt = stmt.order_by(AeternaIntentOrder.created_at.desc())
    return [_order_public(r) for r in (await session.execute(stmt)).scalars().all()]


async def create_partner(
    session: AsyncSession, *, org_id: str, user_id: str, body: AeternaPartnerCreate
) -> AeternaPartnerPublic:
    await require_org_role(session, org_id, user_id, OrgRoleEnum.admin)
    if not _feature_enabled():
        raise HTTPException(status_code=503, detail="AETERNA feature flag disabled")
    now = _utcnow()
    row = AeternaPartner(
        org_id=org_id,
        name=body.name.strip(),
        jurisdiction=body.jurisdiction.strip(),
        license_ref=body.license_ref,
        website=body.website,
        supported_intents=[i.value for i in body.supported_intents],
        verified=False,
        metadata_json=body.metadata_json or {},
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    return _partner_public(row)


async def list_partners(
    session: AsyncSession, *, org_id: str, user_id: str
) -> list[AeternaPartnerPublic]:
    await require_org_role(session, org_id, user_id, OrgRoleEnum.viewer)
    q = await session.execute(
        select(AeternaPartner)
        .where(AeternaPartner.org_id == org_id)
        .order_by(AeternaPartner.created_at.desc())
    )
    return [_partner_public(r) for r in q.scalars().all()]


async def org_summary(session: AsyncSession, *, org_id: str, user_id: str) -> AeternaStatusPublic:
    await require_org_role(session, org_id, user_id, OrgRoleEnum.viewer)
    base = await division_status(session)
    vaults = (
        await session.execute(
            select(func.count()).select_from(AeternaDnaVaultEntry).where(AeternaDnaVaultEntry.org_id == org_id)
        )
    ).scalar_one()
    orders = (
        await session.execute(
            select(func.count()).select_from(AeternaIntentOrder).where(AeternaIntentOrder.org_id == org_id)
        )
    ).scalar_one()
    partners = (
        await session.execute(
            select(func.count())
            .select_from(AeternaPartner)
            .where(AeternaPartner.org_id == org_id, AeternaPartner.verified.is_(True))
        )
    ).scalar_one()
    return base.model_copy(
        update={
            "vault_entries": int(vaults or 0),
            "intent_orders": int(orders or 0),
            "partners_verified": int(partners or 0),
        }
    )
