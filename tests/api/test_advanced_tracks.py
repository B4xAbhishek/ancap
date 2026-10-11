"""Smoke tests for R9/R10/R11/R12 advanced track foundations."""
from __future__ import annotations

import pytest

from app.main import app
from app.schemas.aeterna import AeternaDnaVaultCreate, AeternaIntentKind, AeternaStatusPublic
from app.schemas.orbital_edge import OrbitalEdgeStatusPublic, OrbitalNodeCreate
from app.schemas.securities import SecurityIntakeCreate, SecurityInstrumentType
from app.schemas.watch_fleet import WatchAssetCreate, WatchSlot
from app.services.workflow_execution import WORKFLOW_TEMPLATES


def test_advanced_track_routes_registered():
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/organizations/{org_id}/securities/intake" in paths
    assert "/organizations/{org_id}/watch-fleet/watches" in paths
    assert "/orbital-edge/status" in paths
    assert "/aeterna/status" in paths
    assert "/space-auction/catalog" in paths
    assert "/v1/space-auction/catalog" in paths
    assert "/animal-auction/catalog" in paths
    assert "/v1/animal-auction/catalog" in paths
    assert "/aeterna/vault" in paths
    assert "/v1/aeterna/status" in paths
    assert "/v1/organizations/{org_id}/securities/summary" in paths
    assert "/v1/organizations/{org_id}/watch-fleet/summary" in paths
    assert "/v1/orbital-edge/status" in paths


def test_advanced_track_schema_smoke():
    intake = SecurityIntakeCreate(
        instrument_type=SecurityInstrumentType.promissory_note,
        issuer_name="Example Issuer",
        jurisdiction="US-DE",
        face_amount="1000.00",
    )
    assert intake.currency == "USD"

    watch = WatchAssetCreate(
        employee_user_id="00000000-0000-4000-8000-000000000001",
        slot=WatchSlot.a,
        band_color="graphite",
        serial_number="AW-TEST-001",
    )
    assert watch.slot == WatchSlot.a

    node = OrbitalNodeCreate(codename="ancap-edge-demo")
    assert node.launch_provider == "spacex"
    assert OrbitalEdgeStatusPublic.model_fields["feature_enabled"]

    vault = AeternaDnaVaultCreate(
        label="My Sequencing export",
        content_sha256="a" * 64,
        consent_acknowledged=True,
        source_uri="https://sequencing.com/",
    )
    assert vault.format_hint == "vcf"
    assert AeternaIntentKind.pigmentation_consult.value == "pigmentation_consult"
    assert AeternaIntentKind.organ_bioprint.value == "organ_bioprint"
    assert AeternaIntentKind.partial_reprogramming_consult.value == "partial_reprogramming_consult"
    assert AeternaIntentKind.vet_feline_cryo_restore.value == "vet_feline_cryo_restore"
    assert AeternaIntentKind.vet_canine_regen_pod.value == "vet_canine_regen_pod"
    assert AeternaIntentKind.vinci_light_chamber.value == "vinci_light_chamber"
    assert AeternaIntentKind.microwave_body_contouring.value == "microwave_body_contouring"
    assert AeternaIntentKind.biofusion_micromanipulation.value == "biofusion_micromanipulation"
    assert AeternaIntentKind.dpsc_biomaterial.value == "dpsc_biomaterial"
    assert AeternaIntentKind.vascular_care_plus.value == "vascular_care_plus"
    assert AeternaIntentKind.vascular_care.value == "vascular_care"
    assert AeternaIntentKind.transdermal_pistol.value == "transdermal_pistol"
    assert AeternaIntentKind.m_receptor_subscription.value == "m_receptor_subscription"
    assert AeternaIntentKind.oxygen_carrier_brief.value == "oxygen_carrier_brief"
    assert AeternaIntentKind.synthetic_blood_mamba_brief.value == "synthetic_blood_mamba_brief"
    assert AeternaIntentKind.adhd_support_brief.value == "adhd_support_brief"
    assert AeternaIntentKind.down_syndrome_support_brief.value == "down_syndrome_support_brief"
    assert AeternaIntentKind.substance_coding_brief.value == "substance_coding_brief"
    assert AeternaIntentKind.pulmopure_subscription.value == "pulmopure_subscription"
    assert AeternaIntentKind.barsuk_quantum_pen_brief.value == "barsuk_quantum_pen_brief"
    assert AeternaIntentKind.teleport_earphones_brief.value == "teleport_earphones_brief"
    assert AeternaIntentKind.installation_project_brief.value == "installation_project_brief"
    assert AeternaIntentKind.dna_pheromone_perfume_bottle.value == "dna_pheromone_perfume_bottle"
    assert AeternaStatusPublic.model_fields["division"]
    assert AeternaStatusPublic.model_fields["reprogramming_note"]
    assert AeternaStatusPublic.model_fields["vet_regen_note"]
    assert AeternaStatusPublic.model_fields["vinci_light_note"]
    assert AeternaStatusPublic.model_fields["microwave_body_note"]
    assert AeternaStatusPublic.model_fields["biofusion_note"]
    assert AeternaStatusPublic.model_fields["dpsc_biomaterial_note"]
    assert AeternaStatusPublic.model_fields["vascular_care_plus_note"]
    assert AeternaStatusPublic.model_fields["vascular_care_note"]
    assert AeternaStatusPublic.model_fields["transdermal_pistol_note"]
    assert AeternaStatusPublic.model_fields["m_receptor_note"]
    assert AeternaStatusPublic.model_fields["oxygen_carrier_note"]
    assert AeternaStatusPublic.model_fields["synthetic_blood_mamba_note"]
    assert AeternaStatusPublic.model_fields["adhd_support_note"]
    assert AeternaStatusPublic.model_fields["down_syndrome_support_note"]
    assert AeternaStatusPublic.model_fields["substance_coding_note"]
    assert AeternaStatusPublic.model_fields["pulmopure_note"]
    assert AeternaStatusPublic.model_fields["barsuk_note"]
    assert AeternaStatusPublic.model_fields["teleport_earphones_note"]
    assert AeternaStatusPublic.model_fields["installation_project_note"]
    assert AeternaStatusPublic.model_fields["dna_pheromone_perfume_note"]


def test_aeterna_workflow_templates_catalogued():
    slugs = {t.slug for t in WORKFLOW_TEMPLATES}
    assert "aeterna-dna-wellness-report" in slugs
    assert "aeterna-pigmentation-consult-brief" in slugs
    assert "aeterna-stem-cell-organ-print" in slugs
    assert "aeterna-mrna-reprogramming-brief" in slugs
    aeterna = [t for t in WORKFLOW_TEMPLATES if t.category == "AETERNA"]
    assert len(aeterna) >= 26
    priced = {
        "aeterna-stem-cell-organ-print": "250000",
        "aeterna-vet-cat-cryo-restore": "75000",
        "aeterna-vet-regen-pod": "180000",
        "aeterna-vinci-light-chamber": "48000",
        "aeterna-microwave-body-contouring": "52000",
        "aeterna-transdermal-pistol": "46000",
        "aeterna-m-receptor-subscription": "12000",
        "aeterna-pulmopure-subscription": "14000",
        "aeterna-installation-project": "72000",
        "aeterna-dna-pheromone-perfume": "8900",
        "aeterna-oxygen-carrier": "92000",
        "aeterna-synthetic-blood-mamba": "98000",
        "aeterna-adhd-support": "42000",
        "aeterna-down-syndrome-support": "42000",
        "aeterna-substance-coding": "48000",
        "aeterna-vascular-care-plus": "54000",
        "aeterna-vascular-care": "58000",
        "aeterna-dpsc-biomaterial": "65000",
        "aeterna-biofusion-micromanipulation": "88000",
        "aeterna-aurea-vita": "40",
    }
    for tpl in aeterna:
        assert tpl.price.currency == "ACP"
        expected = priced.get(tpl.slug, "1000000")
        assert tpl.price.amount == expected
    assert "aeterna-vet-cat-cryo-restore" in slugs
    assert "aeterna-vet-regen-pod" in slugs
    assert "aeterna-vinci-light-chamber" in slugs
    assert "aeterna-microwave-body-contouring" in slugs
    assert "aeterna-biofusion-micromanipulation" in slugs
    assert "aeterna-dpsc-biomaterial" in slugs
    assert "aeterna-vascular-care-plus" in slugs
    assert "aeterna-vascular-care" in slugs
    assert "aeterna-transdermal-pistol" in slugs
    assert "aeterna-m-receptor-subscription" in slugs
    assert "aeterna-oxygen-carrier" in slugs
    assert "aeterna-synthetic-blood-mamba" in slugs
    assert "aeterna-adhd-support" in slugs
    assert "aeterna-down-syndrome-support" in slugs
    assert "aeterna-substance-coding" in slugs
    assert "aeterna-pulmopure-subscription" in slugs
    assert "entertainment-tesla-coil-party" in slugs
    assert "aeterna-barsuk-quantum-pen" not in slugs
    assert "aeterna-teleport-earphones" not in slugs
    assert "aeterna-installation-project" in slugs
    assert "aeterna-dna-pheromone-perfume" in slugs


def test_aeterna_vault_metadata_rejects_sequence_blobs():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AeternaDnaVaultCreate(
            label="bad",
            content_sha256="a" * 64,
            consent_acknowledged=True,
            metadata_json={"sequence": "ATCG" * 200},
        )
    ok = AeternaDnaVaultCreate(
        label="ok",
        content_sha256="b" * 64,
        consent_acknowledged=True,
        metadata_json={"storage_mode": "hash_only", "content_byte_size": 123},
    )
    assert ok.content_sha256 == "b" * 64


def test_aeterna_vault_source_uri_rejects_private_targets():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AeternaDnaVaultCreate(
            label="ssrf",
            content_sha256="c" * 64,
            consent_acknowledged=True,
            source_uri="http://169.254.169.254/latest/meta-data",
        )
    with pytest.raises(ValidationError):
        AeternaDnaVaultCreate(
            label="ssrf",
            content_sha256="c" * 64,
            consent_acknowledged=True,
            source_uri="https://127.0.0.1/vault",
        )


def test_organ_print_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-stem-cell-organ-print")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "organ_bioprint"})
    manufacturing = out["deliverable"]["manufacturing"]
    assert manufacturing["mode"] == "licensed_partner_bioreactor"
    assert manufacturing["price_acp"] == "250000"
    assert manufacturing["primary_cell_source"] == "autologous_stem_cells"
    assert manufacturing["fallback_cell_source"] == "wisdom_tooth_dental_pulp_stem_cells_dpsc"
    assert out["deliverable"]["intent"] == "organ_bioprint"
    assert out["deliverable"]["partner_handoff"]["required"] is True
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "crispr cas9 protocol"):
        assert forbidden not in blob


def test_aeterna_longevity_pack_and_intent_slug_map():
    from app.services.aeterna import AETERNA_INTENT_DEFAULT_SLUGS, MRNA_REPROGRAMMING_SLUG, ORGAN_PRINT_SLUG
    from app.services.workflow_execution import WORKFLOW_BUNDLES

    pack = next(x for x in WORKFLOW_BUNDLES if x.slug == "aeterna-longevity-pack")
    assert pack.price.amount == "2500000"
    assert "aeterna-dna-wellness-report" in pack.workflow_slugs
    assert ORGAN_PRINT_SLUG not in pack.workflow_slugs
    assert AETERNA_INTENT_DEFAULT_SLUGS["organ_bioprint"] == ORGAN_PRINT_SLUG
    assert AETERNA_INTENT_DEFAULT_SLUGS["partial_reprogramming_consult"] == MRNA_REPROGRAMMING_SLUG


def test_organ_bioprint_intent_defaults_slug_and_rejects_low_budget(client):
    from app.services.aeterna import ORGAN_PRINT_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "organ_bioprint", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    wrong_slug = client.post(
        "/v1/aeterna/intents",
        json={
            "intent_kind": "organ_bioprint",
            "budget_acp": "250000",
            "workflow_slug": "aeterna-dna-wellness-report",
        },
    )
    assert wrong_slug.status_code == 400, wrong_slug.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "organ_bioprint", "budget_acp": "250000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["intent_kind"] == "organ_bioprint"
    assert payload["workflow_slug"] == ORGAN_PRINT_SLUG
    assert payload["metadata_json"]["manufacturing_mode"] == "licensed_partner_bioreactor"
    assert payload["metadata_json"]["fallback_cell_source"] == "wisdom_tooth_dental_pulp_stem_cells_dpsc"


def test_mrna_reprogramming_execution_is_consult_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-mrna-reprogramming-brief")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "partial_reprogramming_consult"})
    reprogramming = out["deliverable"]["reprogramming"]
    assert reprogramming["mode"] == "partial_keep_cell_identity"
    assert reprogramming["price_acp"] == "1000000"
    assert reprogramming["citation"]["affiliation"] is False
    assert out["deliverable"]["partner_handoff"]["required"] is True
    blob = str(out).lower()
    for forbidden in ("ionizable lipid recipe", "molar ratio", "incubate at", "guide rna", "pcr primer"):
        assert forbidden not in blob


def test_partial_reprogramming_intent_defaults_slug_and_rejects_low_budget(client):
    from app.services.aeterna import MRNA_REPROGRAMMING_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "partial_reprogramming_consult", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    wrong_slug = client.post(
        "/v1/aeterna/intents",
        json={
            "intent_kind": "partial_reprogramming_consult",
            "budget_acp": "1000000",
            "workflow_slug": "aeterna-dna-wellness-report",
        },
    )
    assert wrong_slug.status_code == 400, wrong_slug.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "partial_reprogramming_consult", "budget_acp": "1000000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["intent_kind"] == "partial_reprogramming_consult"
    assert payload["workflow_slug"] == MRNA_REPROGRAMMING_SLUG
    assert payload["metadata_json"]["mode"] == "licensed_partner_consult_only"
    assert payload["metadata_json"]["goal"] == "partial_reprogramming_keep_cell_identity"


def test_vet_regen_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    cat = find_workflow_template("aeterna-vet-cat-cryo-restore")
    assert cat is not None
    cat_out = execute_workflow_template(cat, {"intent_kind": "vet_feline_cryo_restore"})
    assert cat_out["deliverable"]["veterinary"]["species"] == "felis_catus"
    assert cat_out["deliverable"]["veterinary"]["price_acp"] == "75000"
    assert cat_out["deliverable"]["partner_handoff"]["required"] is True

    dog = find_workflow_template("aeterna-vet-regen-pod")
    assert dog is not None
    dog_out = execute_workflow_template(dog, {"intent_kind": "vet_canine_regen_pod"})
    assert dog_out["deliverable"]["veterinary"]["species"] == "canis_familiaris"
    assert dog_out["deliverable"]["veterinary"]["price_acp"] == "180000"
    blob = (str(cat_out) + str(dog_out)).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "ionizable lipid recipe"):
        assert forbidden not in blob
    assert "licensed_veterinary_partner" in blob
    assert "return-to-life warranty" in blob or "not a return-to-life" in blob


def test_vinci_light_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-vinci-light-chamber")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "vinci_light_chamber"})
    pbm = out["deliverable"]["photobiomodulation"]
    assert pbm["price_acp"] == "48000"
    assert pbm["bands"]["pbm_window"] == "600-950nm"
    assert out["deliverable"]["partner_handoff"]["required"] is True
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "ionizable lipid recipe"):
        assert forbidden not in blob
    assert "licensed_phototherapy_partner" in blob
    assert "safe-tanning" in blob or "safe tanning" in blob


def test_vet_regen_intents_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import VET_CAT_CRYO_SLUG, VET_REGEN_POD_SLUG

    too_low_cat = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vet_feline_cryo_restore", "budget_acp": "1000"},
    )
    assert too_low_cat.status_code == 400, too_low_cat.text

    created_cat = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vet_feline_cryo_restore", "budget_acp": "75000"},
    )
    assert created_cat.status_code == 201, created_cat.text
    cat_payload = created_cat.json()
    assert cat_payload["workflow_slug"] == VET_CAT_CRYO_SLUG
    assert cat_payload["metadata_json"]["species"] == "felis_catus"

    too_low_dog = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vet_canine_regen_pod", "budget_acp": "1000"},
    )
    assert too_low_dog.status_code == 400, too_low_dog.text

    created_dog = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vet_canine_regen_pod", "budget_acp": "180000"},
    )
    assert created_dog.status_code == 201, created_dog.text
    dog_payload = created_dog.json()
    assert dog_payload["workflow_slug"] == VET_REGEN_POD_SLUG
    assert dog_payload["metadata_json"]["architecture"] == "vet_regen_pod_organ_bank_bioprint_robot_assist"


def test_vinci_light_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import VINCI_LIGHT_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vinci_light_chamber", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vinci_light_chamber", "budget_acp": "48000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == VINCI_LIGHT_SLUG
    assert payload["metadata_json"]["architecture"] == "full_body_led_uva_red_nir_chamber"
    assert payload["metadata_json"]["bands"]["red"] == "620-680nm"


def test_microwave_body_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-microwave-body-contouring")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "microwave_body_contouring"})
    mw = out["deliverable"]["microwave_body_contouring"]
    assert mw["price_acp"] == "52000"
    assert mw["bands"]["ism_2450"] == "2.45GHz"
    assert mw["bands"]["ism_5800"] == "5.8GHz"
    assert out["deliverable"]["partner_handoff"]["required"] is True
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "ionizable lipid recipe"):
        assert forbidden not in blob
    assert "licensed_aesthetic_dermatology_partner" in blob
    assert "liposuction" in blob


def test_microwave_body_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import MICROWAVE_BODY_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "microwave_body_contouring", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "microwave_body_contouring", "budget_acp": "52000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == MICROWAVE_BODY_SLUG
    assert payload["metadata_json"]["architecture"] == "contact_cooled_microwave_applicator"
    assert payload["metadata_json"]["bands"]["ism_5800"] == "5.8GHz"


def test_biofusion_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-biofusion-micromanipulation")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "biofusion_micromanipulation"})
    bf = out["deliverable"]["biofusion_micromanipulation"]
    assert bf["price_acp"] == "88000"
    assert bf["rails"]["ivf_icsi"] == "licensed_assisted_reproduction_clinic"
    assert out["deliverable"]["partner_handoff"]["required"] is True
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "ionizable lipid recipe"):
        assert forbidden not in blob
    assert "licensed_art_agri_bsl_partner" in blob
    assert "pregnancy" in blob


def test_biofusion_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import BIOFUSION_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "biofusion_micromanipulation", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "biofusion_micromanipulation", "budget_acp": "88000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == BIOFUSION_SLUG
    assert payload["metadata_json"]["architecture"] == "biofusion_micromanipulation_chamber"


def test_dpsc_biomaterial_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-dpsc-biomaterial")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "dpsc_biomaterial"})
    dpsc = out["deliverable"]["dpsc_biomaterial"]
    assert dpsc["price_acp"] == "65000"
    assert dpsc["cell_source"] == "wisdom_tooth_dental_pulp_stem_cells_dpsc"
    assert dpsc["related_organ_print_slug"] == "aeterna-stem-cell-organ-print"
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at"):
        assert forbidden not in blob
    assert "licensed_bioreactor_partner" in blob


def test_dpsc_biomaterial_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import DPSC_BIOMATERIAL_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "dpsc_biomaterial", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "dpsc_biomaterial", "budget_acp": "65000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == DPSC_BIOMATERIAL_SLUG
    assert payload["metadata_json"]["architecture"] == "wisdom_tooth_dpsc_expansion"


def test_vascular_care_plus_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-vascular-care-plus")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "vascular_care_plus"})
    vc = out["deliverable"]["vascular_care_plus"]
    assert vc["price_acp"] == "54000"
    assert vc["gas"]["mix"] == "N2+O2"
    assert out["deliverable"]["partner_handoff"]["required"] is True
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "ionizable lipid recipe"):
        assert forbidden not in blob
    assert "licensed_phlebology_aesthetic_partner" in blob
    assert "thrombosis" in blob


def test_vascular_care_plus_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import VASCULAR_PLUS_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vascular_care_plus", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vascular_care_plus", "budget_acp": "54000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == VASCULAR_PLUS_SLUG
    assert payload["metadata_json"]["architecture"] == "anhydrous_n2_o2_lightwave_applicator"


def test_vascular_care_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-vascular-care")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "vascular_care"})
    vc = out["deliverable"]["vascular_care"]
    assert vc["price_acp"] == "58000"
    assert vc["modalities"]["ultrasound"] == "blood_flow_literacy"
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at"):
        assert forbidden not in blob
    assert "licensed_phlebology_aesthetic_partner" in blob


def test_vascular_care_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import VASCULAR_CARE_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vascular_care", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "vascular_care", "budget_acp": "58000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == VASCULAR_CARE_SLUG
    assert payload["metadata_json"]["architecture"] == "ultrasound_rf_thermal_applicator"


def test_transdermal_pistol_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-transdermal-pistol")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "transdermal_pistol"})
    td = out["deliverable"]["transdermal_pistol"]
    assert td["price_acp"] == "46000"
    assert td["delivery"]["route"] == "aerosol_plus_carrier_gas"
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at"):
        assert forbidden not in blob
    assert "licensed_clinic_partner" in blob
    assert "compounding" in blob


def test_transdermal_pistol_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import TRANSDERMAL_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "transdermal_pistol", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "transdermal_pistol", "budget_acp": "46000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == TRANSDERMAL_SLUG
    assert payload["metadata_json"]["architecture"] == "needle_free_transdermal_pistol"


def test_m_receptor_subscription_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-m-receptor-subscription")
    assert tpl is not None
    assert tpl.billing == "subscription"
    assert tpl.subscription_price_monthly is not None
    assert tpl.subscription_price_monthly.amount == "12000"
    assert tpl.subscription_price_quarterly is not None
    assert tpl.subscription_price_quarterly.amount == "32000"
    assert tpl.subscription_price_annual is not None
    assert tpl.subscription_price_annual.amount == "108000"
    out = execute_workflow_template(tpl, {"intent_kind": "m_receptor_subscription"})
    mr = out["deliverable"]["m_receptor_subscription"]
    assert mr["billing"] == "subscription"
    assert mr["price_acp_monthly"] == "12000"
    assert mr["architecture"] == "m_receptor_multimodal_delivery"
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at"):
        assert forbidden not in blob
    assert "licensed_clinic" in blob
    assert "compounding" in blob


def test_m_receptor_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import M_RECEPTOR_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "m_receptor_subscription", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "m_receptor_subscription", "budget_acp": "12000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == M_RECEPTOR_SLUG
    assert payload["metadata_json"]["architecture"] == "m_receptor_multimodal_delivery"
    assert payload["metadata_json"]["billing"] == "subscription"


def test_oxygen_carrier_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-oxygen-carrier")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "oxygen_carrier_brief"})
    ox = out["deliverable"]["oxygen_carrier"]
    assert ox["price_acp"] == "92000"
    assert ox["architecture"] == "hboC_or_pfc_oxygen_carrier"
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at"):
        assert forbidden not in blob
    assert "licensed_bioreactor" in blob
    assert "compounding" in blob


def test_oxygen_carrier_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import OXYGEN_CARRIER_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "oxygen_carrier_brief", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "oxygen_carrier_brief", "budget_acp": "92000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == OXYGEN_CARRIER_SLUG
    assert payload["metadata_json"]["architecture"] == "hboC_or_pfc_oxygen_carrier"


def test_synthetic_blood_mamba_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-synthetic-blood-mamba")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "synthetic_blood_mamba_brief"})
    sb = out["deliverable"]["synthetic_blood_mamba"]
    assert sb["price_acp"] == "98000"
    assert sb["architecture"] == "hboc_pfc_black_mamba_peptide_architecture"
    blob = str(out).lower()
    for forbidden in ("guide rna", "pcr primer", "incubate at", "venom extraction"):
        assert forbidden not in blob
    assert "licensed_bioreactor" in blob
    assert "toxin" in blob or "venom" in blob


def test_synthetic_blood_mamba_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import SYNTHETIC_BLOOD_MAMBA_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "synthetic_blood_mamba_brief", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "synthetic_blood_mamba_brief", "budget_acp": "98000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == SYNTHETIC_BLOOD_MAMBA_SLUG
    assert payload["metadata_json"]["architecture"] == "hboc_pfc_black_mamba_peptide_architecture"


def test_adhd_support_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-adhd-support")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "adhd_support_brief"})
    adhd = out["deliverable"]["adhd_support"]
    assert adhd["price_acp"] == "42000"
    assert adhd["architecture"] == "adhd_support_partner_literacy"
    blob = str(out).lower()
    for forbidden in ("methylphenidate", "amphetamine dose", "prescribe 10 mg"):
        assert forbidden not in blob
    assert "licensed_clinician" in blob
    assert "diagnosis" in blob


def test_adhd_support_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import ADHD_SUPPORT_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "adhd_support_brief", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "adhd_support_brief", "budget_acp": "42000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == ADHD_SUPPORT_SLUG
    assert payload["metadata_json"]["architecture"] == "adhd_support_partner_literacy"


def test_down_syndrome_support_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-down-syndrome-support")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "down_syndrome_support_brief"})
    ds = out["deliverable"]["down_syndrome_support"]
    assert ds["price_acp"] == "42000"
    assert ds["architecture"] == "down_syndrome_support_partner_literacy"
    blob = str(out).lower()
    for forbidden in ("crispr dose", "cure trisomy", "gene edit recipe"):
        assert forbidden not in blob
    assert "licensed" in blob
    assert "cure" in blob


def test_down_syndrome_support_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import DOWN_SYNDROME_SUPPORT_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "down_syndrome_support_brief", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "down_syndrome_support_brief", "budget_acp": "42000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == DOWN_SYNDROME_SUPPORT_SLUG
    assert payload["metadata_json"]["architecture"] == "down_syndrome_support_partner_literacy"


def test_substance_coding_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-substance-coding")
    assert tpl is not None
    out = execute_workflow_template(tpl, {"intent_kind": "substance_coding_brief"})
    coding = out["deliverable"]["substance_coding"]
    assert coding["price_acp"] == "48000"
    assert coding["architecture"] == "substance_coding_partner_literacy"
    blob = str(out).lower()
    for forbidden in ("dose recipe mg", "compound methadone", "diy hypnosis kit"):
        assert forbidden not in blob
    assert "licensed" in blob
    assert "abstinence" in blob


def test_substance_coding_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import SUBSTANCE_CODING_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "substance_coding_brief", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "substance_coding_brief", "budget_acp": "48000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == SUBSTANCE_CODING_SLUG
    assert payload["metadata_json"]["architecture"] == "substance_coding_partner_literacy"


def test_tesla_coil_party_execution_is_venue_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("entertainment-tesla-coil-party")
    assert tpl is not None
    assert tpl.price.amount == "8900"
    out = execute_workflow_template(tpl, {})
    party = out["deliverable"]["tesla_coil_party"]
    assert party["price_acp"] == "8900"
    assert party["architecture"] == "tesla_coil_party_partner_literacy"
    blob = str(out).lower()
    assert "jack daniel" in blob or "brown-forman" in blob
    assert "liquor" in blob
    assert "age" in blob


def test_pulmopure_subscription_execution_is_partner_handoff_only():
    from app.services.workflow_execution import execute_workflow_template, find_workflow_template

    tpl = find_workflow_template("aeterna-pulmopure-subscription")
    assert tpl is not None
    assert tpl.billing == "subscription"
    assert tpl.subscription_price_monthly is not None
    assert tpl.subscription_price_monthly.amount == "14000"
    assert tpl.subscription_price_quarterly is not None
    assert tpl.subscription_price_quarterly.amount == "38000"
    assert tpl.subscription_price_annual is not None
    assert tpl.subscription_price_annual.amount == "128000"
    out = execute_workflow_template(tpl, {"intent_kind": "pulmopure_subscription"})
    pp = out["deliverable"]["pulmopure_subscription"]
    assert pp["billing"] == "subscription"
    assert pp["price_acp_monthly"] == "14000"
    assert pp["architecture"] == "pulmopure_gas_vibration_partner_literacy"
    blob = str(out).lower()
    for forbidden in ("ozone dose", "ppm ozone", "home ozone kit"):
        assert forbidden not in blob
    assert "licensed_clinic" in blob
    assert "ozone" in blob


def test_pulmopure_intent_default_slug_and_reject_low_budget(client):
    from app.services.aeterna import PULMOPURE_SLUG

    too_low = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "pulmopure_subscription", "budget_acp": "1000"},
    )
    assert too_low.status_code == 400, too_low.text

    created = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "pulmopure_subscription", "budget_acp": "14000"},
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["workflow_slug"] == PULMOPURE_SLUG
    assert payload["metadata_json"]["architecture"] == "pulmopure_gas_vibration_partner_literacy"
    assert payload["metadata_json"]["billing"] == "subscription"



def test_barsuk_and_teleport_retired_from_catalog():
    from app.services.workflow_execution import find_workflow_template

    assert find_workflow_template("aeterna-barsuk-quantum-pen") is None
    assert find_workflow_template("aeterna-teleport-earphones") is None


def test_barsuk_intent_retired(client):
    res = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "barsuk_quantum_pen_brief", "budget_acp": "36000"},
    )
    assert res.status_code == 410, res.text


def test_teleport_intent_retired(client):
    res = client.post(
        "/v1/aeterna/intents",
        json={"intent_kind": "teleport_earphones_brief", "budget_acp": "58000"},
    )
    assert res.status_code == 410, res.text


def test_advanced_track_routes_include_org_aeterna_intents():
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/organizations/{org_id}/aeterna/intents" in paths
    assert "/v1/organizations/{org_id}/aeterna/intents" in paths
