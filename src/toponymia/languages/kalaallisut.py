"""Kalaallisut (Greenlandic) language module for toponymic analysis.

Kalaallisut is the Eskimo-Aleut language of Greenland, essential for
understanding Norse-Inuit toponymic interaction:
- Norse settled Greenland ~985 CE (Erik the Red), colony lasted to ~1450
- Norse place-names: Brattahlíð, Garðar, Herjólfsnes, Eystribyggð
- After Norse disappearance, Inuit names replaced or coexisted
- Danish colonization (1721+) created a THIRD naming layer
- Modern Greenland uses Kalaallisut as primary with Danish secondary:
  - Nuuk (= headland) vs. Godthåb (= Good Hope)
  - Ilulissat (= icebergs) vs. Jakobshavn
  - Qaqortoq (= white) vs. Julianehåb
  - Sisimiut (= people at the fox holes) vs. Holsteinsborg

Understanding the layers:
1. Inuit substrate (pre-Norse, continuous): Kalaallisut names
2. Norse superstrate (985–1450): Old Norse names (now mostly lost/archaeological)
3. Danish colonial overlay (1721–): Danish administrative names
4. Modern Greenlandic revival: Kalaallisut names restored as official

This module handles the Kalaallisut layer. Norse names are handled by
the Old Norse module; Danish names by the Danish module.

Key references:
- Petersen 1967 "Grønlands stednavne"
- Kleivan & Sonne 1985 "Eskimos: Greenland and Canada"
- Grønlands Stednavnenævn (Place Name Commission of Greenland)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KalaallisutModule(BaseLanguageModule):
    """Language module for Kalaallisut (Greenlandic) toponyms."""

    language_code = "kal"  # ISO 639-3 for Kalaallisut
    language_name = "Kalaallisut"
    family = "Eskimo-Aleut"
    branch = "Eskimo > Inuit"
    period = "~2500 BCE – present (in Greenland from ~1200 CE Thule culture)"
    script = "Latn"

    prefixes = [
        "Qaqqar-",  # mountain (Qaqqarsuaq = big mountain)
        "Nuu-",  # headland, cape (Nuuk, Nuussuaq)
        "Iluli-",  # iceberg (Ilulissat)
        "Sisi-",  # fox hole area (Sisimiut)
        "Qaqor-",  # white (Qaqortoq)
        "Nars-",  # plain, flat (Narsaq, Narsarsuaq)
        "Uum-",  # heart (Uummannaq)
        "Kan-",  # ? (Kangerlussuaq)
        "Itas-",  # ? (Itasalik → has many)
        "Ilu-",  # inside (Ilulissat = inside + many)
    ]

    suffixes = [
        # Locative/descriptive suffixes
        "-suaq",  # big (Nuussuaq, Qaqqarsuaq)
        "-nnguaq",  # small, little
        "-toq",  # which has / is (Qaqortoq = white-one)
        "-sat",  # plural marker (Ilulissat = icebergs)
        "-ssat",  # plural variant
        "-miut",  # people of (Sisimiut = people at fox holes)
        "-mut",  # towards (directional)
        "-mik",  # with (instrumental)
        # Geographic generics
        "-lussuaq",  # big fjord (Kangerlussuaq)
        "-rsuaq",  # big (variant after vowel)
        "-sarsuaq",  # big plain (Narsarsuaq)
        "-raq",  # small version
        "-it",  # plural (Ilulissat, various)
        "-up",  # genitive (Nuup = of Nuuk)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "qaqqar": "mountain (qaqqaq)",
        "nuu": "headland, cape, point (nuuk)",
        "iluli": "iceberg (ilulisaq)",
        "sisi": "area with fox burrows",
        "qaqor": "white (qaqortoq)",
        "nars": "plain, flat area (narsaq)",
        "uum": "heart-shaped (uummannaq)",
        "kan": "? (in Kangerlussuaq = big fjord)",
        "suaq": "big, great (-suaq augmentative)",
        "nnguaq": "small, cute (-nnguaq diminutive)",
        "toq": "one which is/has (participial)",
        "sat": "plural (many of)",
        "miut": "inhabitants of, people at",
        "lussuaq": "big fjord (kangerluk + -suaq)",
        "it": "plural marker",
        "up": "genitive case (of X)",
    }

    # Common full Kalaallisut place-name elements
    FULL_ELEMENTS: dict[str, str] = {
        "nuuk": "headland, cape",
        "ilulissat": "icebergs (ilulisaq plural)",
        "qaqortoq": "the white one",
        "sisimiut": "people at the fox holes",
        "narsaq": "plain, flat area",
        "narsarsuaq": "big plain",
        "uummannaq": "heart-shaped (mountain)",
        "kangerlussuaq": "big fjord",
        "aasiaat": "spiders (place with many spiders)",
        "maniitsoq": "the uneven one (rough terrain)",
        "paamiut": "people at the river mouth",
        "tasiilaq": "the place with a calm lake",
        "qaanaaq": "? (northernmost town)",
        "upernavik": "the spring place (upernaaq = spring)",
        "kangaatsiaq": "small promontory",
        "kujalleq": "south, southern (kommune)",
        "sermersooq": "much ice (kommune name)",
        "qeqqata": "the middle one (kommune)",
        "avannaata": "the northern one (kommune)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kalaallisut toponym into components.

        Kalaallisut is polysynthetic — words are built by agglutination.
        Segmentation identifies root + suffixes.
        """
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Check for known full elements first
        if form_lower in self.FULL_ELEMENTS:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="simplex",
                    lemma=form_lower,
                    confidence=0.9,
                )
            )
            return results

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
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
                    morph_type="root",
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
                        morph_type="derivational_suffix",
                        lemma=middle.lower(),
                        confidence=0.4,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="inflectional_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="root",
                    lemma=matched_prefix,
                    confidence=0.75,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="suffix_chain",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.5,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="root",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="inflectional_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="simplex",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Kalaallisut."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Known Greenlandic place-name
        if form_lower in self.FULL_ELEMENTS:
            evidence.append(f"Known Kalaallisut toponym '{form}'")
            score += 0.9
        else:
            # Kalaallisut phonotactics: double consonants, -q endings
            if form_lower.endswith(("q", "t")):
                evidence.append("Kalaallisut word-final consonant (-q/-t)")
                score += 0.2

            # Double vowels (aa, ii, uu) are distinctive
            double_vowels = ["aa", "ii", "uu", "ee", "oo"]
            for dv in double_vowels:
                if dv in form_lower:
                    evidence.append(f"Kalaallisut long vowel '{dv}'")
                    score += 0.15
                    break

            # Diagnostic Kalaallisut clusters
            inuit_clusters = ["qq", "ss", "ll", "nn", "ng", "ts"]
            for cl in inuit_clusters:
                if cl in form_lower:
                    evidence.append(f"Kalaallisut consonant cluster '{cl}'")
                    score += 0.15
                    break

            # Suffixes diagnostic of Kalaallisut
            kal_suffixes = ["suaq", "miut", "toq", "ssat", "sat"]
            for marker in kal_suffixes:
                if form_lower.endswith(marker):
                    evidence.append(f"Kalaallisut suffix -{marker}")
                    score += 0.3
                    break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Inuit presence ~1200 CE – present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Kalaallisut components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            # Check full elements first
            meaning = self.FULL_ELEMENTS.get(comp.lemma.lower())
            if not meaning:
                meaning = self.ELEMENT_MEANINGS.get(comp.lemma.lower().rstrip("-"))
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp.lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                    )
                )
        return candidates
