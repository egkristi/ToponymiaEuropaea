"""Coptic language module for toponymic analysis.

Coptic is the final stage of the Egyptian language (3rd–17th c. CE, with
liturgical survival to the present). Written in a Greek-derived alphabet
with additional Demotic characters. Critical for understanding the
Egyptian→Greek→Latin transmission chain of place-names.

Coptic toponymy bridges ancient and modern:
- Cairo (< Coptic Kashrōm? or Arabic al-Qāhira)
- Aswan (< Coptic Suan < Egyptian swnt)
- Memphis (< Coptic Menfi < Egyptian mn-nfr)
- Thebes (< Coptic Tape < Egyptian tꜣ-ipt)

Relevant to European studies through:
- Hellenistic/Roman administration Greco-Coptic toponyms
- Christian pilgrimage literature preserving Coptic names
- Arabic conquest transmission to broader Islamic world

Key references:
- Crum 1939 "A Coptic Dictionary"
- Černý 1976 "Coptic Etymological Dictionary"
- Timm 1984–92 "Das christlich-koptische Ägypten" (6 vols)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CopticModule(BaseLanguageModule):
    """Language module for Coptic toponyms."""

    language_code = "cop"
    language_name = "Coptic"
    family = "Afro-Asiatic"
    branch = "Egyptian > Coptic"
    period = "3rd–17th c. CE (liturgical survival)"
    script = "Copt"

    prefixes = [
        "Pi-",  # masculine definite article (Pimom)
        "Ti-",  # feminine definite article
        "P-",  # article before consonant
        "T-",  # feminine article before consonant
        "Pma-",  # p-ma (the place of)
        "Smin-",  # from smn (establish: Esna < Smin)
        "Pshi-",  # p-ši (the lake)
        "Kash-",  # variant of Coptic city root
        "Suan-",  # swn (trade: Aswan)
        "Pap-",  # p-api (the head)
        "Rak-",  # place (Rakote → Alexandria)
    ]

    suffixes = [
        "-oou",  # plural masculine (topos → topooou)
        "-oue",  # plural variant
        "-ōm",  # place suffix (Kashrōm)
        "-ōn",  # locative (Fayyūm < Pa-yōm)
        "-ite",  # gentilic (Thebaite)
        "-noute",  # god (theophoric)
        "-pe",  # this/the (demonstrative place)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "pi": "the (masc. definite article)",
        "ti": "the (fem. definite article)",
        "pma": "the place, the location",
        "smin": "to establish, to found (< Eg. smn)",
        "pshi": "the lake, the body of water",
        "kash": "elevated, high (settlement)",
        "suan": "trade, market (< Eg. swnt → Aswan)",
        "pap": "the head, the chief place",
        "rak": "place, ground (Rakote → Alexandria)",
        "tape": "head, summit (< Eg. tꜣ-ipt → Thebes)",
        "menfi": "enduring beauty (< Eg. mn-nfr → Memphis)",
        "shmoun": "eight (Hermopolis < city of eight gods)",
        "psoi": "the canal, waterway",
        "pahour": "the great one (< Eg. pꜣ-wr)",
        "atrib": "estate of Horus (Athribis)",
        "pemdje": "the middle, central (Oxyrhynchus area)",
        "shmin": "the place of Min (Akhmim < Šmin)",
        "siout": "guardian (Asyut < Eg. sꜣwt)",
        "yom": "sea, lake (Fayyūm < pa-yōm = the lake)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Coptic toponym into components."""
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
                    morph_type="prefix",
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
                        morph_type="stem",
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
                    morph_type="prefix",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.8,
                )
            )
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="stem",
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
        """Classify whether a toponym is likely Coptic in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        cop_prefixes = ["pi", "ti", "pma", "pshi", "suan", "rak"]
        for prefix in cop_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Coptic article/prefix '{prefix}-'")
                score += 0.4
                break

        cop_roots = ["tape", "menfi", "shmoun", "shmin", "siout", "yom", "atrib"]
        for root in cop_roots:
            if root in form_lower:
                evidence.append(f"Coptic toponym root '{root}'")
                score += 0.35
                break

        cop_suffixes = ["oou", "oue", "noute"]
        for suffix in cop_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Coptic suffix '-{suffix}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="3rd–17th c. CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Coptic components."""
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
                        sound_changes=["Egyptian > Coptic vowel shift"],
                        sources=["Crum 1939", "Černý 1976", "Timm 1984–92"],
                    )
                )
        return candidates
