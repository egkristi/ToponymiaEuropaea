"""Add onboarding status fields and enriched metadata columns.

Revision ID: 002
Revises: 001
Create Date: 2025-05-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create record_status enum type
    record_status = sa.Enum(
        "candidate",
        "verified",
        "enriched",
        "reviewed",
        "published",
        "retracted",
        name="record_status",
    )
    record_status.create(op.get_bind(), checkfirst=True)

    # --- name_attestations: onboarding fields ---
    op.add_column(
        "name_attestations",
        sa.Column(
            "status",
            record_status,
            server_default="candidate",
            nullable=False,
        ),
    )
    op.add_column(
        "name_attestations",
        sa.Column("reviewed_by", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("is_official", sa.Boolean(), server_default="false", nullable=False),
    )

    # --- name_attestations: enriched metadata ---
    op.add_column(
        "name_attestations",
        sa.Column("phonetic_form", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("ascii_form", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("register", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("dialect", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("date_precision", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("source_page", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("collector", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("collection_method", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("etymology_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("historical_context", sa.Text(), nullable=True),
    )
    op.add_column(
        "name_attestations",
        sa.Column("extra", JSONB(), nullable=True),
    )

    # Index on status for fast filtering
    op.create_index("ix_attestations_status", "name_attestations", ["status"])

    # Index on ascii_form for fuzzy search
    op.create_index("ix_attestations_ascii", "name_attestations", ["ascii_form"])

    # Make source_id NOT NULL (backfill existing rows first)
    op.execute(
        "UPDATE name_attestations SET source_id = "
        "(SELECT id FROM sources LIMIT 1) WHERE source_id IS NULL"
    )
    op.alter_column("name_attestations", "source_id", nullable=False)

    # --- places: enriched metadata ---
    op.add_column("places", sa.Column("depth_m", sa.Float(), nullable=True))
    op.add_column("places", sa.Column("area_km2", sa.Float(), nullable=True))
    op.add_column("places", sa.Column("terrain_type", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("land_cover", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("geology", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("climate_zone", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("country_code", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("admin_level_1", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("admin_level_2", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("municipality_code", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("population", sa.Integer(), nullable=True))
    op.add_column("places", sa.Column("national_registry_id", sa.Text(), nullable=True))
    op.add_column("places", sa.Column("first_attested_year", sa.Integer(), nullable=True))
    op.add_column("places", sa.Column("extra", JSONB(), nullable=True))

    op.create_index("ix_places_country", "places", ["country_code"])
    op.create_index("ix_places_municipality", "places", ["municipality_code"])
    op.create_index("ix_places_national_id", "places", ["national_registry_id"], unique=True)

    # --- place_relations table ---
    op.create_table(
        "place_relations",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "place_id",
            sa.Uuid(),
            sa.ForeignKey("places.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "related_place_id",
            sa.Uuid(),
            sa.ForeignKey("places.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("relation_type", sa.Text(), nullable=False),
        sa.Column("distance_m", sa.Float(), nullable=True),
        sa.Column("bearing_deg", sa.Float(), nullable=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=True),
        sa.Column("extra", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "relation_type IN ("
            "'near', 'adjacent', 'within', 'contains', "
            "'flows_through', 'on_shore_of', 'at_mouth_of', "
            "'overlooks', 'upstream_of', 'downstream_of', "
            "'island_in', 'tributary_of', 'drains_to')",
            name="ck_place_relations_type",
        ),
    )
    op.create_index("ix_place_relations_place", "place_relations", ["place_id"])
    op.create_index("ix_place_relations_related", "place_relations", ["related_place_id"])
    op.create_index("ix_place_relations_type", "place_relations", ["relation_type"])


def downgrade() -> None:
    # Drop place_relations
    op.drop_index("ix_place_relations_type")
    op.drop_index("ix_place_relations_related")
    op.drop_index("ix_place_relations_place")
    op.drop_table("place_relations")

    # Drop places enriched columns
    op.drop_index("ix_places_national_id")
    op.drop_index("ix_places_municipality")
    op.drop_index("ix_places_country")
    for col in [
        "extra",
        "first_attested_year",
        "national_registry_id",
        "population",
        "municipality_code",
        "admin_level_2",
        "admin_level_1",
        "country_code",
        "climate_zone",
        "geology",
        "land_cover",
        "terrain_type",
        "area_km2",
        "depth_m",
    ]:
        op.drop_column("places", col)

    # Revert source_id to nullable
    op.alter_column("name_attestations", "source_id", nullable=True)

    # Drop name_attestations enriched columns
    op.drop_index("ix_attestations_ascii")
    op.drop_index("ix_attestations_status")
    for col in [
        "extra",
        "historical_context",
        "etymology_notes",
        "collection_method",
        "collector",
        "source_page",
        "date_precision",
        "dialect",
        "register",
        "ascii_form",
        "phonetic_form",
        "is_official",
        "reviewed_at",
        "reviewed_by",
        "status",
    ]:
        op.drop_column("name_attestations", col)

    # Drop enum type
    sa.Enum(name="record_status").drop(op.get_bind(), checkfirst=True)
