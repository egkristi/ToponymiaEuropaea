"""Basque (Euskara) language module for toponymic analysis.

Basque is a pre-Indo-European language isolate in the western Pyrenees.
Its toponymy provides unique insights into pre-IE European naming:
- Rich topographic vocabulary: harri (stone), mendi (mountain), ibar (valley)
- Agglutinative morphology: suffixed elements
- Ancient substrate visible in wider area (Aquitanian inscriptions)
- No known genetic relatives

Key references:
- Michelena 1989 "Fonética histórica vasca"
- Gorrotxategi 1984 "Estudio sobre la onomástica indígena de Aquitania"
- Salaberri 2015 "Araba/Álava. Los nombres de nuestros pueblos"
- Belasko 2004 "Diccionario etimológico de los nombres de los pueblos"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class BasqueModule(BaseLanguageModule):
    """Language module for Basque (Euskara) toponyms."""

    language_code = "eu"  # ISO 639-1 for Basque
    language_name = "Basque (Euskara)"
    family = "Language isolate (pre-Indo-European)"
    branch = "Vasconic"
    period = "pre-Roman–present"
    script = "Latn"

    # Common Basque toponymic prefixes/initial elements
    prefixes = [
        "Harri-",  # stone, rock
        "Mendi-",  # mountain
        "Ibar-",  # valley
        "Iri-",  # settlement, town
        "Uri-",  # water, town (variant)
        "Etxe-",  # house
        "Elizondo-",  # by the church
        "Eliza-",  # church (< Latin ecclesia)
        "Gara-",  # high, summit
        "Gorri-",  # red, bare
        "Zubi-",  # bridge
        "Larre-",  # pasture, heath
        "Baso-",  # forest, wild
        "Erreka-",  # stream, ravine
        "Aran-",  # valley (shared with pre-Basque?)
        "Alde-",  # side, near
    ]

    # Common Basque toponymic suffixes
    suffixes = [
        "-aga",  # place of (collective: Arriaga = place of stones)
        "-eta",  # place of (collective: Lizarraga < lizar + aga)
        "-tegi",  # place, shelter (Etxeberritegi)
        "-alde",  # area near
        "-bide",  # road, path
        "-goien",  # upper part
        "-barren",  # lower part, interior
        "-berri",  # new
        "-zahar",  # old
        "-zuri",  # white
        "-beltz",  # black
        "-gorri",  # red, bare
        "-andi",  # large, great
        "-txiki",  # small
        "-pe",  # under, below
        "-gain",  # on top, above
        "-arte",  # between
        "-ondo",  # near, beside
        "-aurre",  # front, before
        "-atze",  # back, behind
    ]

    # Element meanings for etymology
    ELEMENT_MEANINGS: dict[str, str] = {
        "harri": "stone, rock",
        "mendi": "mountain",
        "ibar": "valley, riverside meadow",
        "iri": "settlement, town",
        "uri": "water; settlement",
        "etxe": "house",
        "eliza": "church (< Latin ecclesia)",
        "gara": "height, summit",
        "gorri": "red, bare (of vegetation)",
        "zubi": "bridge",
        "larre": "pasture, heath",
        "baso": "forest, wild land",
        "erreka": "stream, ravine",
        "aran": "valley (possibly pre-Basque)",
        "alde": "side, area near",
        "aga": "place of (collective suffix)",
        "eta": "abundance of, place of",
        "tegi": "place, shelter, building",
        "bide": "road, path, way",
        "goien": "upper part, summit",
        "barren": "lower, interior",
        "berri": "new",
        "zahar": "old",
        "zuri": "white",
        "beltz": "black",
        "andi": "large, great",
        "txiki": "small",
        "pe": "under, below",
        "gain": "top, above",
        "arte": "between (oak tree)",
        "ondo": "near, beside; good",
        "aurre": "front, before",
        "atze": "back, behind",
        "lur": "earth, land",
        "ur": "water",
        "ibai": "river",
        "aintzira": "lake, marsh",
        "aitz": "rock, cliff",
        "lepo": "pass, mountain col",
        "ate": "gate, pass",
        "zulo": "hole, cave",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Basque toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try suffix matching (Basque is agglutinative, suffixes important)
        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        # Also try prefix/initial element matching
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

        if matched_prefix and matched_suffix:
            prefix_part = form[: len(matched_prefix)]
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=len(results),
                    morph_type="derivational_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="compound_modifier",
                    lemma=remainder.lower(),
                    confidence=0.5,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_head",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="derivational_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        else:
            # Check if the whole form is a known element
            if form_lower in self.ELEMENT_MEANINGS:
                results.append(
                    SegmentationResult(
                        component=form,
                        position=0,
                        morph_type="simplex",
                        lemma=form_lower,
                        confidence=0.7,
                    )
                )
            else:
                results.append(
                    SegmentationResult(
                        component=form,
                        position=0,
                        morph_type="simplex",
                        lemma=form_lower,
                        confidence=0.3,
                    )
                )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Basque in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Check for Basque elements anywhere in the name
        basque_elements = [
            "harri",
            "mendi",
            "ibar",
            "etxe",
            "gorri",
            "zubi",
            "larre",
            "baso",
            "erreka",
            "berri",
            "zahar",
            "zuri",
            "beltz",
            "gain",
            "ondo",
            "aitz",
            "ibai",
        ]
        for elem in basque_elements:
            if elem in form_lower:
                evidence.append(f"Basque element '{elem}'")
                score += 0.35
                break

        # Check for Basque suffixes
        basque_suffixes = [
            "aga",
            "eta",
            "tegi",
            "alde",
            "bide",
            "goien",
            "barren",
            "pe",
            "gain",
            "arte",
        ]
        for suffix in basque_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                evidence.append(f"Basque suffix -{suffix}")
                score += 0.3
                break

        # Check for typical Basque phonological features
        # (tx, ts, tz are distinctively Basque)
        basque_phonology = ["tx", "ts", "tz", "rr"]
        for phon in basque_phonology:
            if phon in form_lower:
                evidence.append(f"Basque phoneme '{phon}'")
                score += 0.15
                break

        # Check for absence of IE features and presence of Basque
        # vowel-final structure (common in Basque)
        if form_lower[-1:] in ("a", "e", "i", "o", "u") and score > 0:
            evidence.append("Vowel-final (common in Basque)")
            score += 0.05

        score = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="pre-Roman–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Basque components."""
        candidates: list[EtymologyCandidate] = []

        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get(lemma_key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma_key,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=[],
                    )
                )

        return candidates
