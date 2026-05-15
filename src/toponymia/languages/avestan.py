"""Avestan language module for toponymic analysis.

Avestan is the sacred language of Zoroastrianism, preserved in the Avesta
scripture. Texts were composed between approximately 1000-300 BCE, though
the language itself may date to 1500 BCE or earlier. As a liturgical language,
it preserves archaic Indo-Iranian geographic terminology.

Avestan toponymic features:
- Preserves Proto-Iranian geographic vocabulary
- Geographic names in Avesta: Airyanəm Vaēǰō (Iranian homeland),
  Harahvaitī (= Saraswati/Arachosia), Mouru (Merv), Bāxδī (Balkh)
- Key for understanding the deepest layer of Iranian toponymy
- Vendīdād chapter 1 lists 16 "perfect lands" — earliest Iranian gazetteer

Key references:
- Kellens & Pirart 1988-91 "Les textes vieil-avestiques"
- Gnoli 1980 "Zoroaster's Time and Homeland"
- Witzel 2000 "The Home of the Aryans"
- Skjærvø 1995 "Old and Middle Iranian"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AvestanModule(BaseLanguageModule):
    """Language module for Avestan-origin toponyms."""

    language_code = "ave"
    language_name = "Avestan"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian"
    period = "Old Avestan ~1500–1000 BCE; Young Avestan ~1000–300 BCE; DEAD (liturgical)"
    script = "Avst (Avestan script, created ~5th c. CE for recording)"

    prefixes = [
        "Airya-",  # Aryan, Iranian (Airyanəm Vaēǰō)
        "Harah-",  # flowing (Harahvaitī)
        "Vī-",  # apart (vī-dāiti)
        "Upa-",  # near (upā-iri-)
    ]

    suffixes = [
        "-vaitī",  # having, possessing (Harahvaitī = having ponds)
        "-vaēǰah",  # seed, abode (Airyanəm Vaēǰō)
        "-stāna",  # place, land (> Persian -stan)
        "-gātu",  # place, seat
        "-δāti",  # creation (Vendīdād = against demons-law)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "airya": "Aryan, noble (< PIIr *arya-; > Iran)",
        "vaēǰah": "seed, expanse, abode (Airyanəm Vaēǰō = Iranian expanse)",
        "harah": "flowing, having ponds (< *saras-; cf. Skt. saras)",
        "vaitī": "possessing, having (fem. suffix)",
        "mouru": "Merv (Margiana; < *margu- = meadow)",
        "bāxδī": "Balkh (Bactria; < *Bāxtrī-)",
        "suguda": "Sogdia (< *suxta- = burnt?)",
        "haraiva": "Herat (Aria; < *saraya- = lake?)",
        "varkāna": "Hyrcania (wolf-land; < *vṛka- = wolf)",
        "stāna": "place, land (> -stan)",
        "gātu": "place, seat, throne",
        "āp": "water (Avestan āpō; > Persian āb)",
        "gairi": "mountain (> Persian gīr; cf. Skt. giri)",
        "raŋhā": "river (Avestan name; > Volga? disputed)",
        "zray": "sea, lake (Avestan zrayah-; cf. Aral?)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Avestan-origin toponym into components."""
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
                    confidence=0.7,
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
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="prefix",
                    lemma=matched_prefix,
                    confidence=0.65,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="stem",
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
        """Classify whether a toponym has Avestan origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Known Avestan geographic names (from Vendīdād)
        known = {
            "airyan": "Airyanəm Vaēǰō (Iranian homeland)",
            "harahvait": "Harahvaitī (Arachosia; = Sarasvatī)",
            "mouru": "Mouru (Merv/Margiana)",
            "bāxδ": "Bāxδī (Balkh/Bactria)",
            "suguda": "Suguda (Sogdia)",
            "haraiva": "Haraiva (Herat/Aria)",
            "varkāna": "Varkāna (Hyrcania/wolf-land)",
            "raŋhā": "Raŋhā (great river; Volga?)",
        }
        for name, note in known.items():
            if name in form_lower:
                evidence.append(f"Avestan geographic name: {note}")
                score += 0.6
                break

        # Avestan suffixes
        avestan_suffixes = ["vaitī", "vaēǰah", "stāna", "gātu"]
        for marker in avestan_suffixes:
            if form_lower.endswith(marker):
                evidence.append(f"Avestan suffix -{marker}")
                score += 0.3
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Avestan period (1500–300 BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Avestan components."""
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
                        cognates=["Sanskrit " + comp.lemma, "Old Persian"],
                        sound_changes=["Avestan h- < PIIr *s- (RUKI)"],
                        sources=["Gnoli 1980", "Kellens & Pirart 1988"],
                    )
                )
        return candidates
