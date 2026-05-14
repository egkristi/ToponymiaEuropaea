"""Core domain models using SQLAlchemy ORM."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class RecordStatus(enum.Enum):
    """Onboarding stage for data records."""

    candidate = "candidate"
    verified = "verified"
    enriched = "enriched"
    reviewed = "reviewed"
    published = "published"
    retracted = "retracted"


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    citation: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    reliability: Mapped[float | None] = mapped_column(Float, nullable=True)
    license: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("reliability BETWEEN 0 AND 1", name="ck_sources_reliability"),
    )


class Language(Base):
    __tablename__ = "languages"

    iso_code: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    family: Mapped[str | None] = mapped_column(Text, nullable=True)
    branch: Mapped[str | None] = mapped_column(Text, nullable=True)
    period: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_iso: Mapped[str | None] = mapped_column(
        Text, ForeignKey("languages.iso_code"), nullable=True
    )
    script_default: Mapped[str | None] = mapped_column(Text, nullable=True)


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )

    # --- Location & geometry ---
    geometry: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    uncertainty_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_km2: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Classification ---
    place_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    terrain_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    land_cover: Mapped[str | None] = mapped_column(Text, nullable=True)
    geology: Mapped[str | None] = mapped_column(Text, nullable=True)
    climate_zone: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Administrative ---
    country_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_level_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_level_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    municipality_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- External identifiers ---
    wikidata_qid: Mapped[str | None] = mapped_column(Text, nullable=True)
    geonames_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    national_registry_id: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Temporal ---
    first_attested_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Extensibility (arbitrary structured data) ---
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # --- Relationships ---
    attestations: Mapped[list[NameAttestation]] = relationship(
        back_populates="place", cascade="all, delete-orphan"
    )
    interpretations: Mapped[list[Interpretation]] = relationship(
        back_populates="place", cascade="all, delete-orphan"
    )
    relations_from: Mapped[list[PlaceRelation]] = relationship(
        foreign_keys="PlaceRelation.place_id",
        back_populates="place",
        cascade="all, delete-orphan",
    )
    relations_to: Mapped[list[PlaceRelation]] = relationship(
        foreign_keys="PlaceRelation.related_place_id",
        back_populates="related_place",
    )


class NameLemma(Base):
    """A name as a lexical type, independent of which places it attaches to.

    Represents the abstract identity of a name (e.g., "Berg") across all
    attestations and places. Enables distributional statistics ("show me
    all 40,000 Berg-attestations") and etymological tracking.
    """

    __tablename__ = "name_lemmas"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    canonical_form: Mapped[str] = mapped_column(Text, nullable=False)
    language_code: Mapped[str] = mapped_column(
        Text, ForeignKey("languages.iso_code"), nullable=False
    )
    semantic_field: Mapped[str | None] = mapped_column(Text, nullable=True)
    pie_root: Mapped[str | None] = mapped_column(Text, nullable=True)
    meaning: Mapped[str | None] = mapped_column(Text, nullable=True)
    cognates: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    first_attested_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attestations: Mapped[list[NameAttestation]] = relationship(back_populates="lemma")


class NameAttestation(Base):
    __tablename__ = "name_attestations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    lemma_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("name_lemmas.id"), nullable=True
    )

    # --- Name forms ---
    form: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_form: Mapped[str] = mapped_column(Text, nullable=False)
    phonetic_form: Mapped[str | None] = mapped_column(Text, nullable=True)
    ascii_form: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Linguistic metadata ---
    language_code: Mapped[str] = mapped_column(
        Text, ForeignKey("languages.iso_code"), nullable=False
    )
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    register: Mapped[str | None] = mapped_column(Text, nullable=True)
    dialect: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Temporal attestation ---
    year_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_precision: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Provenance ---
    source_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("sources.id"), nullable=False)
    source_page: Mapped[str | None] = mapped_column(Text, nullable=True)
    collector: Mapped[str | None] = mapped_column(Text, nullable=True)
    collection_method: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Quality ---
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[RecordStatus] = mapped_column(
        Enum(RecordStatus, name="record_status"),
        server_default="candidate",
        nullable=False,
    )
    is_current: Mapped[bool] = mapped_column(Boolean, server_default="false")
    is_official: Mapped[bool] = mapped_column(Boolean, server_default="false")
    reviewed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Etymology notes ---
    etymology_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    historical_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Extensibility ---
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # --- Relationships ---
    place: Mapped[Place] = relationship(back_populates="attestations")
    lemma: Mapped[NameLemma | None] = relationship(back_populates="attestations")
    components: Mapped[list[NameComponent]] = relationship(
        back_populates="attestation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_attestations_confidence"),
    )


class NameComponent(Base):
    __tablename__ = "name_components"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    attestation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("name_attestations.id", ondelete="CASCADE"), nullable=False
    )
    component: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    morph_type: Mapped[str] = mapped_column(Text, nullable=False)
    lemma: Mapped[str | None] = mapped_column(Text, nullable=True)
    language_code: Mapped[str | None] = mapped_column(
        Text, ForeignKey("languages.iso_code"), nullable=True
    )
    meaning_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    attestation: Mapped[NameAttestation] = relationship(back_populates="components")

    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_components_confidence"),
        CheckConstraint(
            "morph_type IN ('prefix', 'stem', 'suffix',"
            " 'compound_head', 'compound_modifier', 'infix', 'genitive')",
            name="ck_components_morph_type",
        ),
    )


class Interpretation(Base):
    __tablename__ = "interpretations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    method: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date | None] = mapped_column(nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sources.id"), nullable=True
    )
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("interpretations.id"), nullable=True
    )
    ontology_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    place: Mapped[Place] = relationship(back_populates="interpretations")

    __table_args__ = (
        CheckConstraint("probability BETWEEN 0 AND 1", name="ck_interpretations_probability"),
    )


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    place_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=True
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    null_hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    test_family: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, server_default="proposed")
    preregistered: Mapped[bool] = mapped_column(Boolean, server_default="false")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    p_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    effect_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('proposed', 'preregistered', 'tested',"
            " 'confirmed', 'rejected', 'inconclusive')",
            name="ck_hypotheses_status",
        ),
    )


class PlaceRelation(Base):
    """Spatial and semantic relationships between places.

    Tracks nearby places, containing water bodies, administrative containment,
    and any other spatial relationship needed for analysis.
    """

    __tablename__ = "place_relations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=func.gen_random_uuid()
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    related_place_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(Text, nullable=False)
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    bearing_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sources.id"), nullable=True
    )
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    place: Mapped[Place] = relationship(foreign_keys=[place_id], back_populates="relations_from")
    related_place: Mapped[Place] = relationship(
        foreign_keys=[related_place_id], back_populates="relations_to"
    )

    __table_args__ = (
        CheckConstraint(
            "relation_type IN ("
            "'near', 'adjacent', 'within', 'contains', "
            "'flows_through', 'on_shore_of', 'at_mouth_of', "
            "'overlooks', 'upstream_of', 'downstream_of', "
            "'island_in', 'tributary_of', 'drains_to')",
            name="ck_place_relations_type",
        ),
        CheckConstraint(
            "place_id != related_place_id",
            name="ck_place_relations_no_self",
        ),
    )
