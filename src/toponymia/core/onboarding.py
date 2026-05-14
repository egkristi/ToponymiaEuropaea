"""Data onboarding state machine.

Enforces the 5-stage pipeline with validation gates between stages:
  candidate → verified → enriched → reviewed → published

Each transition has gate criteria that must be met before promotion.
All transitions are recorded in an audit log for full traceability.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from toponymia.core import RecordStatus

# Valid transitions: (from_status, to_status)
VALID_PROMOTIONS: dict[RecordStatus, RecordStatus] = {
    RecordStatus.candidate: RecordStatus.verified,
    RecordStatus.verified: RecordStatus.enriched,
    RecordStatus.enriched: RecordStatus.reviewed,
    RecordStatus.reviewed: RecordStatus.published,
}

VALID_DEMOTIONS: dict[RecordStatus, RecordStatus] = {
    RecordStatus.verified: RecordStatus.candidate,
    RecordStatus.enriched: RecordStatus.verified,
    RecordStatus.reviewed: RecordStatus.enriched,
    RecordStatus.published: RecordStatus.reviewed,
}


@dataclass
class GateResult:
    """Result of a validation gate check."""

    passed: bool
    reason: str


@dataclass
class TransitionRecord:
    """Audit log entry for a state transition."""

    record_id: str
    from_status: RecordStatus
    to_status: RecordStatus
    actor: str
    timestamp: datetime
    reason: str | None = None


class GateError(Exception):
    """Raised when a transition gate is not satisfied."""

    def __init__(self, gate_result: GateResult):
        self.gate_result = gate_result
        super().__init__(gate_result.reason)


class InvalidTransitionError(Exception):
    """Raised when a transition is not valid."""


def check_promotion_gate(
    status: RecordStatus,
    *,
    has_source: bool = False,
    has_normalized_form: bool = False,
    has_language: bool = False,
    has_components: bool = False,
    reviewer: str | None = None,
    ingester: str | None = None,
) -> GateResult:
    """Check whether promotion gate criteria are met.

    Gate criteria by stage:
      candidate → verified: source_id NOT NULL, normalized_form present
      verified → enriched: language_code set, at least one component parsed
      enriched → reviewed: reviewer assigned (reviewer ≠ ingester)
      reviewed → published: all previous gates pass (final approval)
    """
    if status == RecordStatus.candidate:
        if not has_source:
            return GateResult(False, "source_id is required for promotion to verified")
        if not has_normalized_form:
            return GateResult(False, "normalized_form is required for promotion to verified")
        return GateResult(True, "Gate passed: source and normalized form present")

    if status == RecordStatus.verified:
        if not has_language:
            return GateResult(False, "language_code is required for promotion to enriched")
        if not has_components:
            return GateResult(
                False, "At least one parsed component required for promotion to enriched"
            )
        return GateResult(True, "Gate passed: language and components present")

    if status == RecordStatus.enriched:
        if not reviewer:
            return GateResult(False, "A reviewer must be assigned for promotion to reviewed")
        if reviewer == ingester:
            return GateResult(False, "Reviewer must differ from ingester (four-eyes principle)")
        return GateResult(True, "Gate passed: independent reviewer assigned")

    if status == RecordStatus.reviewed:
        return GateResult(True, "Gate passed: final publication approval")

    return GateResult(False, f"Cannot promote from status: {status.value}")


def promote(
    status: RecordStatus,
    *,
    actor: str,
    record_id: str,
    **gate_kwargs: bool | str | None,
) -> tuple[RecordStatus, TransitionRecord]:
    """Promote a record to the next stage.

    Returns the new status and an audit record.
    Raises GateError if gate criteria are not met.
    Raises InvalidTransitionError if promotion is not possible.
    """
    if status == RecordStatus.retracted:
        raise InvalidTransitionError("Cannot promote a retracted record")

    if status == RecordStatus.published:
        raise InvalidTransitionError("Record is already at the final stage")

    if status not in VALID_PROMOTIONS:
        raise InvalidTransitionError(f"No valid promotion from {status.value}")

    gate = check_promotion_gate(status, **gate_kwargs)
    if not gate.passed:
        raise GateError(gate)

    new_status = VALID_PROMOTIONS[status]
    record = TransitionRecord(
        record_id=record_id,
        from_status=status,
        to_status=new_status,
        actor=actor,
        timestamp=datetime.now(UTC),
    )
    return new_status, record


def demote(
    status: RecordStatus,
    *,
    actor: str,
    record_id: str,
    reason: str,
) -> tuple[RecordStatus, TransitionRecord]:
    """Demote a record to the previous stage.

    A reason is always required for demotion.
    Returns the new status and an audit record.
    """
    if status == RecordStatus.retracted:
        raise InvalidTransitionError("Cannot demote a retracted record")

    if status == RecordStatus.candidate:
        raise InvalidTransitionError("Record is already at the lowest stage")

    if status not in VALID_DEMOTIONS:
        raise InvalidTransitionError(f"No valid demotion from {status.value}")

    new_status = VALID_DEMOTIONS[status]
    record = TransitionRecord(
        record_id=record_id,
        from_status=status,
        to_status=new_status,
        actor=actor,
        timestamp=datetime.now(UTC),
        reason=reason,
    )
    return new_status, record


def retract(
    status: RecordStatus,
    *,
    actor: str,
    record_id: str,
    reason: str,
) -> tuple[RecordStatus, TransitionRecord]:
    """Retract a record (soft-delete with audit trail).

    Can be retracted from any stage. Reason is required.
    Retracted records are excluded from analysis but preserved in DB.
    """
    if status == RecordStatus.retracted:
        raise InvalidTransitionError("Record is already retracted")

    record = TransitionRecord(
        record_id=record_id,
        from_status=status,
        to_status=RecordStatus.retracted,
        actor=actor,
        timestamp=datetime.now(UTC),
        reason=reason,
    )
    return RecordStatus.retracted, record
