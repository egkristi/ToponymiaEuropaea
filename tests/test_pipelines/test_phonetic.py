"""Tests for the Nordic phonetic normalizer."""

from toponymia.pipelines.phonetic import NordicPhoneticNormalizer


class TestPhoneticKey:
    """Tests for individual phonetic key computation."""

    def setup_method(self) -> None:
        self.normalizer = NordicPhoneticNormalizer()

    def test_basic_lowercase(self) -> None:
        result = self.normalizer.phonetic_key("Bergen")
        assert result.key == "bergen"
        assert result.original == "Bergen"

    def test_thorn_to_t(self) -> None:
        result = self.normalizer.phonetic_key("Þórshöfn")
        assert "þ" not in result.key
        assert result.key.startswith("t")
        assert "þ→t" in result.rules_applied

    def test_eth_to_d(self) -> None:
        result = self.normalizer.phonetic_key("Viðareiði")
        assert "ð" not in result.key
        assert "ð→d" in result.rules_applied

    def test_o_ogonek_to_o(self) -> None:
        result = self.normalizer.phonetic_key("Bjǫrgvin")
        assert "ǫ" not in result.key
        assert "ǫ→o" in result.rules_applied

    def test_swedish_o_umlaut(self) -> None:
        result = self.normalizer.phonetic_key("Malmö")
        assert result.key == "malmø"
        assert "ö→ø" in result.rules_applied

    def test_swedish_a_umlaut(self) -> None:
        result = self.normalizer.phonetic_key("Gävle")
        assert result.key == "gævle"
        assert "ä→æ" in result.rules_applied

    def test_danish_aa(self) -> None:
        result = self.normalizer.phonetic_key("Aalborg")
        assert result.key == "ålborg"
        assert "aa→å" in result.rules_applied

    def test_w_to_v(self) -> None:
        result = self.normalizer.phonetic_key("Wasa")
        assert result.key == "vasa"
        assert "w→v" in result.rules_applied

    def test_hv_to_kv(self) -> None:
        result = self.normalizer.phonetic_key("Hvaler")
        assert result.key == "kvaler"
        assert "hv→kv" in result.rules_applied


class TestSuffixNormalization:
    """Tests for suffix equivalence rules."""

    def setup_method(self) -> None:
        self.normalizer = NordicPhoneticNormalizer()

    def test_hem_to_heim(self) -> None:
        result = self.normalizer.phonetic_key("Solhem")
        assert result.key == "solheim"
        assert "hem→heim" in result.rules_applied

    def test_sted_to_stad(self) -> None:
        result = self.normalizer.phonetic_key("Fredriksted")
        assert result.key == "fredrikstad"
        assert "sted→stad" in result.rules_applied

    def test_nas_to_nes(self) -> None:
        result = self.normalizer.phonetic_key("Sigtunänäs")
        assert result.key.endswith("nes")
        assert "næs→nes" in result.rules_applied

    def test_vig_to_vik(self) -> None:
        result = self.normalizer.phonetic_key("Skalvig")
        assert result.key == "skalvik"
        assert "vig→vik" in result.rules_applied

    def test_bjerg_to_berg(self) -> None:
        result = self.normalizer.phonetic_key("Skovbjerg")
        assert result.key == "skovberg"
        assert "bjerg→berg" in result.rules_applied

    def test_bye_to_by(self) -> None:
        result = self.normalizer.phonetic_key("Kongsbye")
        assert result.key == "kongsby"
        assert "bye→by" in result.rules_applied


class TestEquivalence:
    """Tests for cross-source equivalence detection."""

    def setup_method(self) -> None:
        self.normalizer = NordicPhoneticNormalizer()

    def test_vik_vig_equivalent(self) -> None:
        assert self.normalizer.are_equivalent("Narvik", "Narvig")

    def test_hem_heim_equivalent(self) -> None:
        assert self.normalizer.are_equivalent("Trondheim", "Trondhem")

    def test_o_umlaut_oe_equivalent(self) -> None:
        assert self.normalizer.are_equivalent("Malmö", "Malmø")

    def test_unrelated_not_equivalent(self) -> None:
        assert not self.normalizer.are_equivalent("Bergen", "Stavanger")

    def test_w_v_equivalent(self) -> None:
        assert self.normalizer.are_equivalent("Wasa", "Vasa")


class TestFindDuplicates:
    """Tests for batch duplicate detection."""

    def setup_method(self) -> None:
        self.normalizer = NordicPhoneticNormalizer()

    def test_finds_variant_groups(self) -> None:
        names = ["Trondheim", "Trondhem", "Bergen", "Stavanger"]
        dupes = self.normalizer.find_duplicates(names)
        assert len(dupes) == 1
        group = list(dupes.values())[0]
        assert "Trondheim" in group
        assert "Trondhem" in group

    def test_no_duplicates(self) -> None:
        names = ["Bergen", "Oslo", "Stavanger"]
        dupes = self.normalizer.find_duplicates(names)
        assert len(dupes) == 0

    def test_multiple_groups(self) -> None:
        names = ["Malmö", "Malmø", "Narvik", "Narvig", "Oslo"]
        dupes = self.normalizer.find_duplicates(names)
        assert len(dupes) == 2


class TestConfigOptions:
    """Tests for normalizer configuration options."""

    def test_disable_on_rules(self) -> None:
        normalizer = NordicPhoneticNormalizer(apply_on_rules=False)
        result = normalizer.phonetic_key("Þórshöfn")
        assert "þ" in result.key  # þ not converted

    def test_disable_cross_nordic(self) -> None:
        normalizer = NordicPhoneticNormalizer(apply_cross_nordic=False)
        result = normalizer.phonetic_key("Wasa")
        assert result.key == "wasa"  # w→v is cross-nordic, so disabled

    def test_disable_suffix(self) -> None:
        normalizer = NordicPhoneticNormalizer(apply_suffix_normalization=False)
        result = normalizer.phonetic_key("Trondhem")
        assert result.key.endswith("hem")  # hem not → heim

    def test_batch_keys(self) -> None:
        normalizer = NordicPhoneticNormalizer()
        results = normalizer.batch_keys(["Bergen", "Oslo"])
        assert "Bergen" in results
        assert "Oslo" in results
        assert results["Bergen"].key == "bergen"

    def test_language_hint_preserved(self) -> None:
        normalizer = NordicPhoneticNormalizer()
        result = normalizer.phonetic_key("Þingvellir", language="isl")
        assert result.language == "isl"
