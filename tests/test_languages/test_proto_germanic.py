"""Tests for the Proto-Germanic and Old English language modules."""

from toponymia.languages.proto_germanic import OldEnglishModule, ProtoGermanicModule


class TestProtoGermanicModule:
    """Tests for ProtoGermanicModule."""

    def setup_method(self):
        self.module = ProtoGermanicModule()

    def test_metadata(self):
        assert self.module.language_code == "gem"
        assert self.module.language_name == "Proto-Germanic"
        assert self.module.family == "Indo-European"
        assert "Germanic" in self.module.branch

    def test_classify_reconstructed_form(self):
        result = self.module.classify("*haimaz")
        assert result.confidence > 0.5
        assert "reconstructed" in result.evidence[0].lower()

    def test_classify_non_germanic(self):
        result = self.module.classify("Roma")
        assert result.confidence < 0.3

    def test_segment_basic(self):
        results = self.module.segment("*haimaz")
        assert len(results) >= 1
        assert results[0].morph_type == "stem"

    def test_etymologize(self):
        from toponymia.languages.base import SegmentationResult

        comps = [SegmentationResult(component="*haimaz", position=0, morph_type="stem")]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "home" in candidates[0].meaning or "village" in candidates[0].meaning


class TestOldEnglishModule:
    """Tests for OldEnglishModule."""

    def setup_method(self):
        self.module = OldEnglishModule()

    def test_metadata(self):
        assert self.module.language_code == "ang"
        assert self.module.language_name == "Old English"
        assert "West Germanic" in self.module.branch

    def test_classify_ham_suffix(self):
        result = self.module.classify("Birmingham")
        assert result.confidence > 0.4
        assert any("suffix" in e for e in result.evidence)

    def test_classify_ton_suffix(self):
        result = self.module.classify("Paddington")
        assert result.confidence > 0.4

    def test_classify_ley_suffix(self):
        result = self.module.classify("Barnsley")
        assert result.confidence >= 0.4

    def test_classify_chester_suffix(self):
        result = self.module.classify("Manchester")
        assert result.confidence > 0.4
        assert any("Latin" in e or "chester" in e for e in result.evidence)

    def test_classify_ingham_patronymic(self):
        result = self.module.classify("Buckingham")
        assert result.confidence > 0.5
        assert any("patronymic" in e for e in result.evidence)

    def test_classify_non_english(self):
        result = self.module.classify("Trondheim")
        # Should score low for OE (it's Norse)
        assert result.confidence < 0.5

    def test_segment_birmingham(self):
        results = self.module.segment("Birmingham")
        assert len(results) >= 2
        # -ingham is matched as a compound suffix (OE -ingas + hām)
        assert any(r.lemma == "ingham" for r in results)

    def test_segment_paddington(self):
        results = self.module.segment("Paddington")
        # -ington is matched as a compound suffix (OE -ingas + tūn)
        assert len(results) >= 2
        assert any(r.lemma == "ington" for r in results)

    def test_segment_oxford(self):
        results = self.module.segment("Oxford")
        assert len(results) >= 2
        assert any(r.lemma == "ford" for r in results)

    def test_segment_no_recognized_suffix(self):
        results = self.module.segment("Gwynedd")
        assert len(results) == 1
        assert results[0].morph_type == "stem"
        assert results[0].confidence < 0.5

    def test_etymologize_ham(self):
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="ham", position=1, morph_type="compound_head", lemma="ham"
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "hām" in candidates[0].lemma
        assert "homestead" in candidates[0].meaning

    def test_etymologize_ford(self):
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="ford", position=1, morph_type="compound_head", lemma="ford"
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "ford" in candidates[0].lemma
        assert "crossing" in candidates[0].meaning

    def test_etymologize_chester(self):
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="chester",
                position=1,
                morph_type="compound_head",
                lemma="chester",
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "castra" in candidates[0].meaning.lower() or "fort" in candidates[0].meaning.lower()
