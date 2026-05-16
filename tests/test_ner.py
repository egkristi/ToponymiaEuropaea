"""Tests for Historical NER module."""

from __future__ import annotations

from toponymia.nlp.ner import HistoricalNER


class TestHistoricalNER:
    """Test rule-based historical NER."""

    def setup_method(self) -> None:
        self.ner = HistoricalNER()

    def test_extract_latin_place(self) -> None:
        text = "terram in Sandvika iuxta ecclesiam"
        entities = self.ner.extract_entities(text, language="lat")
        place_entities = [e for e in entities if e.entity_type == "PLACE"]
        assert len(place_entities) >= 1
        names = [e.text for e in place_entities]
        assert "Sandvika" in names

    def test_extract_latin_de_place(self) -> None:
        text = "Johannes de Bergheim presbiter"
        entities = self.ner.extract_entities(text, language="lat")
        place_entities = [e for e in entities if e.entity_type == "PLACE"]
        names = [e.text for e in place_entities]
        assert "Bergheim" in names

    def test_extract_old_norse_place(self) -> None:
        text = "hann bjó í Niðarós ok átti jǫrð at Steinker"
        entities = self.ner.extract_entities(text, language="non")
        place_entities = [e for e in entities if e.entity_type == "PLACE"]
        names = [e.text for e in place_entities]
        assert any("Ni" in n or "Steinker" in n for n in names)

    def test_extract_title(self) -> None:
        text = "Hákon konungr gaf Ólafi jarli land í Þrándheimi"
        entities = self.ner.extract_entities(text, language="non")
        titles = [e for e in entities if e.entity_type == "TITLE"]
        title_texts = [e.text for e in titles]
        assert "konungr" in title_texts
        assert "jarli" in title_texts

    def test_extract_deity(self) -> None:
        text = "á Þórsnes var hof mikit"
        entities = self.ner.extract_entities(text, language="non")
        deities = [e for e in entities if e.entity_type == "DEITY"]
        assert len(deities) >= 1
        assert any("Þórs" in e.text for e in deities)

    def test_extract_ethnonym(self) -> None:
        text = "Finnar komu norðan ok Kvænar austan"
        entities = self.ner.extract_entities(text, language="non")
        ethnonyms = [e for e in entities if e.entity_type == "ETHNONYM"]
        texts = [e.text for e in ethnonyms]
        assert any("Finn" in t for t in texts)
        assert any("Kvæn" in t for t in texts)

    def test_reject_function_words(self) -> None:
        text = "in anno domini MCCXLV de ecclesie sancti"
        entities = self.ner.extract_entities(text, language="lat")
        place_entities = [e for e in entities if e.entity_type == "PLACE"]
        place_names = [e.text.lower() for e in place_entities]
        # Should not extract common function words as places
        assert "anno" not in place_names
        assert "domini" not in place_names

    def test_extract_attestations(self) -> None:
        text = "terram in Berghæim in parrochia Sandvika"
        attestations = self.ner.extract_attestations(
            text, year=1295, source="DN I 85", language="lat"
        )
        assert len(attestations) >= 1
        att = attestations[0]
        assert att["year"] == 1295
        assert att["source"] == "DN I 85"
        assert att["language"] == "lat"
        assert att["entity_type"] == "PLACE"

    def test_empty_text(self) -> None:
        entities = self.ner.extract_entities("", language="lat")
        assert entities == []

    def test_deduplication(self) -> None:
        # Same place mentioned twice by different patterns shouldn't produce duplicates
        text = "in Bergheim de Bergheim"
        entities = self.ner.extract_entities(text, language="lat")
        place_entities = [e for e in entities if e.entity_type == "PLACE"]
        # Each occurrence at a different position is OK, but same position shouldn't duplicate
        positions = [(e.start, e.end) for e in place_entities]
        assert len(positions) == len(set(positions))
