"""Initial database schema.

Revision ID: 001
Create Date: 2025-05-14
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sources table (referenced by others)
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("citation", sa.Text(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("reliability", sa.Float(), nullable=True),
        sa.Column("license", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("reliability BETWEEN 0 AND 1", name="ck_sources_reliability"),
    )

    # Languages table
    op.create_table(
        "languages",
        sa.Column("iso_code", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("family", sa.Text(), nullable=True),
        sa.Column("branch", sa.Text(), nullable=True),
        sa.Column("period", sa.Text(), nullable=True),
        sa.Column("parent_iso", sa.Text(), sa.ForeignKey("languages.iso_code"), nullable=True),
        sa.Column("script_default", sa.Text(), nullable=True),
    )

    # Places table (core)
    op.create_table(
        "places",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("geometry", Geometry("POINT", srid=4326), nullable=False),
        sa.Column("elevation_m", sa.Float(), nullable=True),
        sa.Column("uncertainty_m", sa.Float(), nullable=True),
        sa.Column("place_type", sa.Text(), nullable=True),
        sa.Column("wikidata_qid", sa.Text(), nullable=True),
        sa.Column("geonames_id", sa.BigInteger(), nullable=True),
        sa.Column("osm_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_places_geometry", "places", ["geometry"], postgresql_using="gist")
    op.create_index("ix_places_wikidata", "places", ["wikidata_qid"], unique=False)
    op.create_index("ix_places_geonames", "places", ["geonames_id"], unique=False)

    # Name attestations
    op.create_table(
        "name_attestations",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("form", sa.Text(), nullable=False),
        sa.Column("normalized_form", sa.Text(), nullable=False),
        sa.Column("language_code", sa.Text(), sa.ForeignKey("languages.iso_code"), nullable=False),
        sa.Column("script", sa.Text(), nullable=True),
        sa.Column("year_from", sa.Integer(), nullable=True),
        sa.Column("year_to", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_attestations_confidence"),
    )
    op.create_index("ix_attestations_place", "name_attestations", ["place_id"])
    op.create_index("ix_attestations_form", "name_attestations", ["normalized_form"])
    op.create_index(
        "ix_attestations_form_trgm", "name_attestations", ["normalized_form"],
        postgresql_using="gin",
        postgresql_ops={"normalized_form": "gin_trgm_ops"},
    )

    # Name components (morphological decomposition)
    op.create_table(
        "name_components",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("attestation_id", sa.Uuid(), sa.ForeignKey("name_attestations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("component", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("morph_type", sa.Text(), nullable=False),
        sa.Column("lemma", sa.Text(), nullable=True),
        sa.Column("language_code", sa.Text(), sa.ForeignKey("languages.iso_code"), nullable=True),
        sa.Column("meaning_uri", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_components_confidence"),
        sa.CheckConstraint(
            "morph_type IN ('prefix', 'stem', 'suffix', 'compound_head', 'compound_modifier', 'infix', 'genitive')",
            name="ck_components_morph_type",
        ),
    )
    op.create_index("ix_components_attestation", "name_components", ["attestation_id"])
    op.create_index("ix_components_lemma", "name_components", ["lemma"])

    # Language layers (which language layers are attested at a place)
    op.create_table(
        "language_layers",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language_code", sa.Text(), sa.ForeignKey("languages.iso_code"), nullable=False),
        sa.Column("period", sa.Text(), nullable=True),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_layers_confidence"),
    )

    # Interpretations (scholarly claims with provenance)
    op.create_table(
        "interpretations",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("probability", sa.Float(), nullable=True),
        sa.Column("method", sa.Text(), nullable=True),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
        sa.Column("supersedes_id", sa.Uuid(), sa.ForeignKey("interpretations.id"), nullable=True),
        sa.Column("ontology_version", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("probability BETWEEN 0 AND 1", name="ck_interpretations_probability"),
    )
    op.create_index("ix_interpretations_place", "interpretations", ["place_id"])

    # Hypotheses (testable claims)
    op.create_table(
        "hypotheses",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=True),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("null_hypothesis", sa.Text(), nullable=False),
        sa.Column("test_family", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), server_default=sa.text("'proposed'")),
        sa.Column("preregistered", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("p_value", sa.Float(), nullable=True),
        sa.Column("effect_size", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "status IN ('proposed', 'preregistered', 'tested', 'confirmed', 'rejected', 'inconclusive')",
            name="ck_hypotheses_status",
        ),
    )

    # Terrain features (perspective C)
    op.create_table(
        "terrain_features",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_type", sa.Text(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("method", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )

    # Ecological features (perspective D)
    op.create_table(
        "ecological_features",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_type", sa.Text(), nullable=False),
        sa.Column("species_taxon", sa.Text(), nullable=True),
        sa.Column("period", sa.Text(), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )

    # Archaeological sites (perspective E)
    op.create_table(
        "archaeological_sites",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("site_type", sa.Text(), nullable=False),
        sa.Column("period", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )

    # Cultural features (perspective F, G)
    op.create_table(
        "cultural_features",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_type", sa.Text(), nullable=False),
        sa.Column("religion", sa.Text(), nullable=True),
        sa.Column("period", sa.Text(), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )

    # Historical events (perspective B)
    op.create_table(
        "historical_events",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("date_from", sa.Integer(), nullable=True),
        sa.Column("date_to", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )

    # Renaming events (perspective G, political)
    op.create_table(
        "renaming_events",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_attestation_id", sa.Uuid(), sa.ForeignKey("name_attestations.id"), nullable=True),
        sa.Column("to_attestation_id", sa.Uuid(), sa.ForeignKey("name_attestations.id"), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("motivation", sa.Text(), nullable=True),
        sa.Column("actor", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )

    # Administrative history (perspective J)
    op.create_table(
        "administrative_units",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("place_id", sa.Uuid(), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit_type", sa.Text(), nullable=False),
        sa.Column("unit_name", sa.Text(), nullable=False),
        sa.Column("date_from", sa.Integer(), nullable=True),
        sa.Column("date_to", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("administrative_units")
    op.drop_table("renaming_events")
    op.drop_table("historical_events")
    op.drop_table("cultural_features")
    op.drop_table("archaeological_sites")
    op.drop_table("ecological_features")
    op.drop_table("terrain_features")
    op.drop_table("hypotheses")
    op.drop_table("interpretations")
    op.drop_table("language_layers")
    op.drop_table("name_components")
    op.drop_table("name_attestations")
    op.drop_table("places")
    op.drop_table("languages")
    op.drop_table("sources")
