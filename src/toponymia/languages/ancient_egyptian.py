"""Ancient Egyptian language module for toponymic analysis.

Ancient Egyptian is an Afroasiatic language documented from c. 3100 BCE to the
7th century CE. Its massive toponymic legacy survives through Greek and Latin
adaptations that transmitted Egyptian place-names across the Mediterranean world.

Ancient Egyptian toponymy is relevant to European studies through:
- Greek adaptations: Waset → Thebes, Ineb-hedj → Memphis, Iunu → Heliopolis
- Roman transmission of Egyptian names into Latin geographic tradition
- Biblical place-names preserved in European languages
- Classical geographers (Herodotus, Strabo, Ptolemy) recording Egyptian names
- Coptic continuation providing phonological bridge

Characterized by:
- Compound names: element + determinative (niwt = city, spat = nome)
- Theophoric names: deity + epithet (pr-Imn = house of Amun)
- Topographic descriptions: mw (water), dw (mountain), wḥꜥt (oasis)

Key references:
- Gauthier 1925–31 "Dictionnaire des noms géographiques" (7 vols)
- Gardiner 1947 "Ancient Egyptian Onomastica"
- Zibelius 1972 "Afrikanische Orts- und Völkernamen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AncientEgyptianModule(BaseLanguageModule):
    """Language module for Ancient Egyptian toponyms."""

    language_code = "egy"
    language_name = "Ancient Egyptian"
    family = "Afro-Asiatic"
    branch = "Egyptian"
    period = "c. 3100 BCE – 7th c. CE"
    script = "Egyp"  # Egyptian hieroglyphs

    prefixes = [
        "Per-",  # pr (house of, temple of: Per-Amun)
        "Iunu-",  # iwnw (pillar city: Heliopolis)
        "Ineb-",  # inb (wall: Ineb-hedj = Memphis)
        "Khem-",  # ḫm (shrine: Khem/Letopolis)
        "Men-",  # mn (established, enduring)
        "Neb-",  # nb (lord of, all)
        "Waset-",  # wꜣst (scepter city: Thebes)
        "Abu-",  # ꜣbw (elephant: Elephantine/Aswan)
        "Dja-",  # ḏꜥ (crossing: variant)
        "Ta-",  # tꜣ (land of)
        "Het-",  # ḥwt (estate, mansion)
    ]

    suffixes = [
        "-niwt",  # niwt (city, town)
        "-hedj",  # ḥḏ (white: Ineb-hedj)
        "-nefer",  # nfr (beautiful, good)
        "-wer",  # wr (great)
        "-hotep",  # ḥtp (peace, satisfied)
        "-amun",  # imn (Amun: theophoric)
        "-aten",  # itn (Aten: solar disk)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "per": "pr (house, temple, domain of)",
        "iunu": "iwnw (pillar city, Heliopolis)",
        "ineb": "inb (wall, fortification)",
        "khem": "ḫm (shrine, sacred precinct)",
        "men": "mn (established, enduring, stable)",
        "neb": "nb (lord of, possessor, all)",
        "waset": "wꜣst (scepter, power → Thebes)",
        "abu": "ꜣbw (elephant, ivory → Aswan)",
        "ta": "tꜣ (land, earth, country)",
        "het": "ḥwt (estate, great house, mansion)",
        "dja": "ḏꜥ (crossing, ford)",
        "niwt": "niwt (city, town, settlement)",
        "hedj": "ḥḏ (white, bright, silver)",
        "nefer": "nfr (beautiful, good, perfect)",
        "wer": "wr (great, large, senior)",
        "hotep": "ḥtp (peace, offering, content)",
        "amun": "imn (the hidden one, Amun deity)",
        "aten": "itn (solar disk, Aten deity)",
        "kemet": "kmt (black land, Egypt)",
        "deshret": "dšrt (red land, desert)",
        "iteru": "itrw (river, the Nile)",
        "menat": "mnꜥt (nurse, Thebes epithet)",
        "swenet": "swnt (trade, market → Syene/Aswan)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Ancient Egyptian toponym into components."""
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
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
        """Classify whether a toponym is likely Ancient Egyptian in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        egy_prefixes = ["per", "iunu", "ineb", "khem", "men", "waset", "abu", "het"]
        for prefix in egy_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Egyptian prefix '{prefix}-'")
                score += 0.45
                break

        egy_roots = ["kemet", "deshret", "iteru", "niwt", "hotep", "amun", "nefer"]
        for root in egy_roots:
            if root in form_lower:
                evidence.append(f"Egyptian element '{root}'")
                score += 0.35
                break

        egy_suffixes = ["hotep", "nefer", "amun", "aten"]
        for suffix in egy_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Egyptian theophoric suffix '-{suffix}'")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="c. 3100 BCE – 7th c. CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Ancient Egyptian components."""
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
                        sources=["Gauthier 1925–31", "Gardiner 1947"],
                    )
                )
        return candidates
