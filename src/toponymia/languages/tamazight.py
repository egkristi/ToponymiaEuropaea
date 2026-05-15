"""Central Atlas Tamazight language module for toponymic analysis.

Central Atlas Tamazight (Tamaziɣt) is a Berber language spoken by ~4 million
people in the Atlas Mountains of Morocco. It is one of the principal languages
of the Amazigh peoples.

Tamazight toponymy is relevant to European place-name studies through:
- Moorish-period transmission of Berber names to Iberia (711–1492)
- Gibraltar area preserving Berber names via Arabic transmission
- Trans-Mediterranean trade and contact (Berber-Iberian links)
- French/Spanish colonial cartography of Morocco

Characterized by:
- Prefixes: Imi- (mouth of), Tizi- (pass), Aït- (sons of)
- Suffixes: -n (genitive), -t (feminine), -wen (plural)
- Consonantal roots (shared Berber typology)
- State alternation: free vs. annexed state

Key references:
- Galand 1983 "Toponymie berbère: recherches en onomastique"
- Pellat 1955 "Description de la terre (El Bekri)"
- Chaker 1998 "Encyclopédie berbère"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class TamazightModule(BaseLanguageModule):
    """Language module for Central Atlas Tamazight toponyms."""

    language_code = "tzm"
    language_name = "Central Atlas Tamazight"
    family = "Afro-Asiatic"
    branch = "Berber > Northern Berber > Atlas"
    period = "Antiquity–present"
    script = "Latn"

    prefixes = [
        "Aït-",  # sons of, clan (Aït Baha)
        "Imi-",  # mouth of, opening (Iminifri)
        "Tizi-",  # mountain pass, col (Tizi n'Test)
        "Agh-",  # variant fort/enclosure
        "Agadir-",  # granary, fortified store (Agadir)
        "Tafr-",  # slope, escarpment
        "Anz-",  # gazelle (Anzal)
        "Ifr-",  # cave (Ifrane)
        "Azrou-",  # rock (Azrou)
        "Toud-",  # mountain (Toubkal variant)
        "Igh-",  # fort, place
        "Amz-",  # hold, possess
    ]

    suffixes = [
        "-n",  # genitive/of (Tizi n'Tichka)
        "-t",  # feminine marker (Tamazight, Tiznit)
        "-wen",  # masculine plural (iduren → idurenwen)
        "-in",  # plural (Imazighen)
        "-an",  # adjectival/locative
        "-al",  # place of (Anzal)
        "-as",  # nominal derivation
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ait": "sons of, clan of (tribal affiliation)",
        "imi": "mouth, opening, entrance (of valley/cave)",
        "tizi": "mountain pass, col, high crossing",
        "agadir": "fortified granary, collective storehouse",
        "ifr": "cave, grotto, shelter",
        "azrou": "rock, stone, rocky place",
        "adrar": "mountain, high ground",
        "igh": "fortified place, hilltop settlement",
        "tafr": "slope, escarpment, cliff",
        "anz": "gazelle (animal toponym)",
        "toud": "mountain, peak (Toubkal)",
        "amz": "to hold, possess (settlement claim)",
        "agdal": "enclosed meadow, protected pasture",
        "targa": "irrigation canal, channel",
        "asif": "river, watercourse, wadi",
        "taddart": "house, village, settlement",
        "ighrem": "fortress, fortified village",
        "afella": "summit, top, upper part",
        "tawrirt": "small hill, hillock",
        "anammer": "slope facing south (sunny side)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Tamazight toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

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
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
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
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.8,
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
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
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
        """Classify whether a toponym is likely Tamazight in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        tzm_prefixes = ["ait", "imi", "tizi", "agadir", "ifr", "azrou", "igh"]
        for prefix in tzm_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Tamazight prefix '{prefix}-'")
                score += 0.45
                break

        tzm_roots = ["adrar", "asif", "taddart", "ighrem", "agdal", "targa"]
        for root in tzm_roots:
            if root in form_lower:
                evidence.append(f"Tamazight root '{root}'")
                score += 0.3
                break

        tzm_suffixes = ["wen", "in"]
        for suffix in tzm_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Tamazight suffix '-{suffix}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Antiquity–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Tamazight components."""
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
                        sound_changes=[],
                        sources=["Galand 1983", "Chaker 1998"],
                    )
                )
        return candidates
