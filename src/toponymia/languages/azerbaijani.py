"""Azerbaijani language module for toponymic analysis.

Azerbaijani (Azərbaycanca) is an Oghuz Turkic language spoken in Azerbaijan
and northwestern Iran. It serves as a bridge between Turkish and Central Asian
Turkic toponymic traditions.

Azerbaijani toponymic features:
- Turkic compound structure: modifier + head (Ağdaş = white stone)
- Persian loanwords in settlement names (-abad, -bad, -stan)
- Arabic influence through Islamic period
- Caucasian substrate elements
- Key suffixes: -bad (city), -kend (village), -gah (place)
- Geographic terms: qala (fortress), dağ (mountain), çay (river)
- Notable names: Bakı (Baku), Gəncə, Naxçıvan, Şəki, Lənkəran

Key references:
- Həsənov 2001 "Azərbaycan toponimiyasının əsasları"
- Budagov & Geybullayev 1998 "Explanatory Dictionary of Azerbaijan Toponyms"
- Janashia 2005 "Caucasian Toponymy"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AzerbaijaniModule(BaseLanguageModule):
    """Language module for Azerbaijani-origin toponyms."""

    language_code = "aze"
    language_name = "Azerbaijani"
    family = "Turkic"
    branch = "Oghuz"
    period = "Proto-Azerbaijani 11th c.; Modern Azerbaijani 16th c.–"
    script = "Latn (since 1991); Cyrl (Soviet); Arab (historical)"

    prefixes = [
        "Ağ-",  # white (Ağdam, Ağdaş)
        "Qara-",  # black (Qarabağ, Qaradağ)
        "Göy-",  # blue/green (Göyçay, Göygöl)
        "Qızıl-",  # red/gold (Qızılağac)
        "Yeni-",  # new (Yeni Yol)
        "Köhnə-",  # old
        "Aşağı-",  # lower
        "Yuxarı-",  # upper
    ]

    suffixes = [
        "-bad",  # city (Əhmədbad; from Persian)
        "-abad",  # settlement (Salyanabad)
        "-stan",  # land of (Dağıstan)
        "-kend",  # village (Lənkəran < Lan-karan; Gəncə < Ganja-kend?)
        "-gah",  # place, station (Qışlaqgah)
        "-lı",  # having, with (Daşkəsənli)
        "-lar",  # plural (Qubalılar)
        "-çay",  # river (Göyçay)
        "-dağ",  # mountain (Qaradağ)
        "-göl",  # lake (Göygöl)
        "-bağ",  # garden (Qarabağ)
        "-qala",  # fortress (Naxçıvan < Naqš-i Jahān?)
        "-bulaq",  # spring (Şorbulaq)
        "-su",  # water (Ağsu)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ağ": "white",
        "qara": "black, large",
        "göy": "blue, green, sky",
        "qızıl": "red, gold",
        "yeni": "new",
        "köhnə": "old",
        "dağ": "mountain",
        "çay": "river, stream",
        "göl": "lake",
        "su": "water",
        "qala": "fortress, citadel",
        "bağ": "garden (< Persian bāgh)",
        "bulaq": "spring, source",
        "kend": "village, settlement",
        "bad": "city (< Persian -bād)",
        "abad": "settlement (< Persian ābād)",
        "gah": "place, station",
        "daş": "stone, rock",
        "yol": "road, path",
        "düz": "plain, flat",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Azerbaijani-origin toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes], key=len, reverse=True
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes], key=len, reverse=True
        )

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix and matched_suffix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="stem",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_modifier",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.75,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.5,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym has Azerbaijani origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        az_suffixes = ["kend", "gah", "bulaq", "göl", "çay", "dağ", "qala"]
        for marker in az_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Azerbaijani suffix -{marker}")
                score += 0.4
                break

        az_prefixes = ["ağ", "qara", "göy", "qızıl"]
        for marker in az_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Azerbaijani prefix {marker}-")
                score += 0.3
                break

        # Azerbaijani-specific phonology (ə, ı, ğ)
        if "ə" in form_lower or "ğ" in form_lower:
            evidence.append("Azerbaijani-specific graphemes (ə, ğ)")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Turkic/Azerbaijani period" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Azerbaijani components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            meaning = self.ELEMENT_MEANINGS.get(comp.lemma.lower().rstrip("-"))
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp.lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=["Turkish " + comp.lemma],
                    )
                )
        return candidates
