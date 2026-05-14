"""Tests for data onboarding state machine."""

from __future__ import annotations

import pytest

from toponymia.core import RecordStatus
from toponymia.core.onboarding import (
    GateError,
    InvalidTransitionError,
    check_promotion_gate,
    demote,
    promote,
    retract,
)


class TestPromotionGates:
    """Test gate validation for each stage transition."""

    def test_candidate_to_verified_passes(self):
        result = check_promotion_gate(
            RecordStatus.candidate,
            has_source=True,
            has_normalized_form=True,
        )
        assert result.passed

    def test_candidate_to_verified_no_source(self):
        result = check_promotion_gate(
            RecordStatus.candidate,
            has_source=False,
            has_normalized_form=True,
        )
        assert not result.passed
        assert "source_id" in result.reason

    def test_candidate_to_verified_no_normalized_form(self):
        result = check_promotion_gate(
            RecordStatus.candidate,
            has_source=True,
            has_normalized_form=False,
        )
        assert not result.passed
        assert "normalized_form" in result.reason

    def test_verified_to_enriched_passes(self):
        result = check_promotion_gate(
            RecordStatus.verified,
            has_language=True,
            has_components=True,
        )
        assert result.passed

    def test_verified_to_enriched_no_components(self):
        result = check_promotion_gate(
            RecordStatus.verified,
            has_language=True,
            has_components=False,
        )
        assert not result.passed
        assert "component" in result.reason

    def test_enriched_to_reviewed_passes(self):
        result = check_promotion_gate(
            RecordStatus.enriched,
            reviewer="reviewer_a",
            ingester="ingester_b",
        )
        assert result.passed

    def test_enriched_to_reviewed_same_person(self):
        result = check_promotion_gate(
            RecordStatus.enriched,
            reviewer="same_user",
            ingester="same_user",
        )
        assert not result.passed
        assert "four-eyes" in result.reason

    def test_enriched_to_reviewed_no_reviewer(self):
        result = check_promotion_gate(
            RecordStatus.enriched,
            reviewer=None,
            ingester="ingester_b",
        )
        assert not result.passed
        assert "reviewer" in result.reason

    def test_reviewed_to_published_passes(self):
        result = check_promotion_gate(RecordStatus.reviewed)
        assert result.passed


class TestPromote:
    """Test the promote function."""

    def test_promote_candidate_to_verified(self):
        new_status, record = promote(
            RecordStatus.candidate,
            actor="test_user",
            record_id="rec-001",
            has_source=True,
            has_normalized_form=True,
        )
        assert new_status == RecordStatus.verified
        assert record.from_status == RecordStatus.candidate
        assert record.to_status == RecordStatus.verified
        assert record.actor == "test_user"
        assert record.record_id == "rec-001"

    def test_promote_verified_to_enriched(self):
        new_status, _ = promote(
            RecordStatus.verified,
            actor="test_user",
            record_id="rec-001",
            has_language=True,
            has_components=True,
        )
        assert new_status == RecordStatus.enriched

    def test_promote_enriched_to_reviewed(self):
        new_status, _ = promote(
            RecordStatus.enriched,
            actor="reviewer_a",
            record_id="rec-001",
            reviewer="reviewer_a",
            ingester="ingester_b",
        )
        assert new_status == RecordStatus.reviewed

    def test_promote_reviewed_to_published(self):
        new_status, _ = promote(
            RecordStatus.reviewed,
            actor="admin",
            record_id="rec-001",
        )
        assert new_status == RecordStatus.published

    def test_promote_published_raises(self):
        with pytest.raises(InvalidTransitionError, match="final stage"):
            promote(
                RecordStatus.published,
                actor="test_user",
                record_id="rec-001",
            )

    def test_promote_retracted_raises(self):
        with pytest.raises(InvalidTransitionError, match="retracted"):
            promote(
                RecordStatus.retracted,
                actor="test_user",
                record_id="rec-001",
            )

    def test_promote_gate_failure_raises(self):
        with pytest.raises(GateError, match="source_id"):
            promote(
                RecordStatus.candidate,
                actor="test_user",
                record_id="rec-001",
                has_source=False,
                has_normalized_form=True,
            )


class TestDemote:
    """Test the demote function."""

    def test_demote_verified_to_candidate(self):
        new_status, record = demote(
            RecordStatus.verified,
            actor="admin",
            record_id="rec-001",
            reason="Source unreliable",
        )
        assert new_status == RecordStatus.candidate
        assert record.reason == "Source unreliable"

    def test_demote_published_to_reviewed(self):
        new_status, _ = demote(
            RecordStatus.published,
            actor="admin",
            record_id="rec-001",
            reason="New evidence contradicts",
        )
        assert new_status == RecordStatus.reviewed

    def test_demote_candidate_raises(self):
        with pytest.raises(InvalidTransitionError, match="lowest stage"):
            demote(
                RecordStatus.candidate,
                actor="admin",
                record_id="rec-001",
                reason="test",
            )

    def test_demote_retracted_raises(self):
        with pytest.raises(InvalidTransitionError, match="retracted"):
            demote(
                RecordStatus.retracted,
                actor="admin",
                record_id="rec-001",
                reason="test",
            )


class TestRetract:
    """Test the retract function."""

    def test_retract_from_candidate(self):
        new_status, record = retract(
            RecordStatus.candidate,
            actor="admin",
            record_id="rec-001",
            reason="Duplicate entry",
        )
        assert new_status == RecordStatus.retracted
        assert record.reason == "Duplicate entry"

    def test_retract_from_published(self):
        new_status, _ = retract(
            RecordStatus.published,
            actor="admin",
            record_id="rec-001",
            reason="Fabricated data discovered",
        )
        assert new_status == RecordStatus.retracted

    def test_retract_already_retracted_raises(self):
        with pytest.raises(InvalidTransitionError, match="already retracted"):
            retract(
                RecordStatus.retracted,
                actor="admin",
                record_id="rec-001",
                reason="test",
            )
