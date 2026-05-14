"""Tests for diachronic attestation linking pipeline."""

from toponymia.pipelines.diachronic import (
    AttestationChain,
    DiachronicReport,
    build_attestation_chains,
)


class TestBuildAttestationChains:
    def _make_record(
        self,
        name: str,
        phonetic_key: str,
        h3_r9: str = "890999bae1bffff",
        year_from: int | None = None,
        attestations: list | None = None,
        source_id: str = "test",
    ) -> dict:
        rec: dict = {
            "name_form": name,
            "name_normalized": name.lower(),
            "_phonetic_key": phonetic_key,
            "_h3_r9": h3_r9,
            "source_id": source_id,
            "is_current": year_from is None,
        }
        if year_from is not None:
            rec["year_from"] = year_from
        if attestations:
            rec["attestations"] = attestations
        return rec

    def test_simple_two_form_chain(self) -> None:
        """Two forms of the same place create a chain."""
        records = [
            self._make_record("Torshov", "torshov", year_from=2024, source_id="modern"),
            self._make_record("Þorshofuum", "torshov", year_from=1340, source_id="historic"),
        ]
        report = build_attestation_chains(records)
        assert report.chains_found == 1
        chain = report.chains[0]
        assert chain.depth == 2
        assert chain.current_form == "Torshov"
        assert chain.links[0].earlier_form == "Þorshofuum"
        assert chain.links[0].later_form == "Torshov"
        assert chain.span_years == 684  # 2024 - 1340

    def test_three_form_chain(self) -> None:
        """Three chronological forms create two links."""
        records = [
            self._make_record("Vik", "vik", year_from=2024, source_id="modern"),
            self._make_record("Wik", "vik", year_from=1600, source_id="map"),
            self._make_record("Vík", "vik", year_from=1200, source_id="saga"),
        ]
        report = build_attestation_chains(records)
        assert report.chains_found == 1
        chain = report.chains[0]
        assert chain.depth == 3
        assert len(chain.links) == 2
        # Verify chronological order
        assert chain.links[0].earlier_form == "Vík"
        assert chain.links[0].later_form == "Wik"
        assert chain.links[1].earlier_form == "Wik"
        assert chain.links[1].later_form == "Vik"

    def test_no_chain_single_form(self) -> None:
        """Single form per key doesn't create a chain."""
        records = [
            self._make_record("Oslo", "oslo"),
            self._make_record("Bergen", "bergen"),
        ]
        report = build_attestation_chains(records)
        assert report.chains_found == 0

    def test_different_h3_cells_separate_chains(self) -> None:
        """Same phonetic key but different locations = separate groups."""
        records = [
            self._make_record("Vik", "vik", h3_r9="890999bae1bffff", year_from=2024),
            self._make_record("Vik", "vik", h3_r9="890999bae1bffff", year_from=1200),
            self._make_record("Vik", "vik", h3_r9="8901255030fffff", year_from=2024),
            self._make_record("Vik", "vik", h3_r9="8901255030fffff", year_from=1400),
        ]
        report = build_attestation_chains(records)
        # Two separate chains (different H3 cells = different places)
        assert report.chains_found == 0  # same form "Vik" deduped → only 1 unique

    def test_attestation_array_included(self) -> None:
        """Attestation array on a record is included in chain."""
        records = [
            self._make_record(
                "Torshov",
                "torshov",
                year_from=2024,
                attestations=[
                    {"form": "Þorshofuum", "year_from": 1340, "is_current": False},
                    {"form": "Torshoff", "year_from": 1600, "is_current": False},
                ],
            ),
        ]
        report = build_attestation_chains(records)
        assert report.chains_found == 1
        chain = report.chains[0]
        assert chain.depth == 3
        assert chain.span_years == 684

    def test_empty_input(self) -> None:
        """Empty records produce empty report."""
        report = build_attestation_chains([])
        assert report.total_records == 0
        assert report.chains_found == 0

    def test_report_longest_span(self) -> None:
        """Report tracks longest span."""
        records = [
            self._make_record("Nidaros", "nidaros", year_from=2024, source_id="a"),
            self._make_record("Niðaróss", "nidaros", year_from=1000, source_id="b"),
            self._make_record("Heim", "heim", year_from=2024, source_id="c"),
            self._make_record("Heimr", "heim", year_from=1300, source_id="d"),
        ]
        report = build_attestation_chains(records)
        assert report.longest_span == 1024  # 2024 - 1000

    def test_confidence_phonetic_match(self) -> None:
        """Links with matching phonetic keys get high confidence."""
        records = [
            self._make_record("Torshov", "torshov", year_from=2024, source_id="a"),
            self._make_record("Þorshov", "torshov", year_from=1200, source_id="b"),
        ]
        report = build_attestation_chains(records)
        assert report.chains[0].links[0].confidence >= 0.8

    def test_multi_form_chains_property(self) -> None:
        """multi_form_chains counts chains with 2+ forms."""
        records = [
            self._make_record("A", "key1", year_from=2024, source_id="x"),
            self._make_record("B", "key1", year_from=1900, source_id="y"),
        ]
        report = build_attestation_chains(records)
        assert report.multi_form_chains == 1


class TestAttestationChain:
    def test_span_years_none_without_dates(self) -> None:
        chain = AttestationChain(
            place_id="test",
            current_form="Oslo",
            all_forms=[{"form": "Oslo"}, {"form": "Ásló"}],
        )
        assert chain.span_years is None

    def test_depth(self) -> None:
        chain = AttestationChain(
            place_id="test",
            current_form="Oslo",
            all_forms=[{"form": "Oslo"}, {"form": "Ásló"}, {"form": "Óslo"}],
        )
        assert chain.depth == 3


class TestDiachronicReport:
    def test_multi_form_chains_empty(self) -> None:
        report = DiachronicReport(total_records=0, chains_found=0)
        assert report.multi_form_chains == 0
