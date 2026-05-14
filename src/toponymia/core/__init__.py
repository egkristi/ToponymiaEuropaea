"""Core domain models using SQLAlchemy ORM."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
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
    parent_iso: Mapped[str | None] = mapped_column(Text, ForeignKey("languages.iso_code"), nullable=True)
    script_default: Mapped[str | None] = mapped_column(Text, nullable=True)


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
    geometry: Mapped[str] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    uncertainty_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    place_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    wikidata_qid: Mapped[str | None] = mapped_column(Text, nullable=True)
    geonames_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    attestations: Mapped[list[NameAttestation]] = relationship(back_populates="place", cascade="all, delete-orphan")
    interpretations: Mapped[list[Interpretation]] = relationship(back_populates="place", cascade="all, delete-orphan")


class NameAttestation(Base):
    __tablename__ = "name_attestations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
    place_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    form: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_form: Mapped[str] = mapped_column(Text, nullable=False)
    language_code: Mapped[str] = mapped_column(Text, ForeignKey("languages.iso_code"), nullable=False)
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    year_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("sources.id"), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    place: Mapped[Place] = relationship(back_populates="attestations")
    components: Mapped[list[NameComponent]] = relationship(back_populates="attestation", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_attestations_confidence"),
    )


class NameComponent(Base):
    __tablename__ = "name_components"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
    attestation_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("name_attestations.id", ondelete="CASCADE"), nullable=False)
    component: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    morph_type: Mapped[str] = mapped_column(Text, nullable=False)
    lemma: Mapped[str | None] = mapped_column(Text, nullable=True)
    language_code: Mapped[str | None] = mapped_column(Text, ForeignKey("languages.iso_code"), nullable=True)
    meaning_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    attestation: Mapped[NameAttestation] = relationship(back_populates="components")

    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_components_confidence"),
        CheckConstraint(
            "morph_type IN ('prefix', 'stem', 'suffix', 'compound_head', 'compound_modifier', 'infix', 'genitive')",
            name="ck_components_morph_type",
        ),
    )


class Interpretation(Base):
    __tablename__ = "interpretations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
    place_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    method: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date | None] = mapped_column(nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("sources.id"), nullable=True)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("interpretations.id"), nullable=True)
    ontology_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    place: Mapped[Place] = relationship(back_populates="interpretations")

    __table_args__ = (
        CheckConstraint("probability BETWEEN 0 AND 1", name="ck_interpretations_probability"),
    )


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.gen_random_uuid())
    place_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("places.id", ondelete="CASCADE"), nullable=True)
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
            "status IN ('proposed', 'preregistered', 'tested', 'confirmed', 'rejected', 'inconclusive')",
            name="ck_hypotheses_status",
        ),
    )
