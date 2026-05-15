"""Old Persian language module for toponymic analysis.

Old Persian (c. 525–300 BCE) was the Iranian language of the Achaemenid
Empire, known from royal cuneiform inscriptions (Behistun, Persepolis).
Critical for understanding how Near Eastern toponyms were transmitted
to the Greek world and thence to European knowledge.
Distinct from Middle Persian (Pahlavi) and Modern Persian (already in persian.py).

Key references:
- Kent 1953 "Old Persian: Grammar, Texts, Lexicon"
- Schmitt 2014 "Wörterbuch der altpersischen Königsinschriften"
- Tavernier 2007 "Iranica in the Achaemenid Period"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldPersianModule(BaseLanguageModule):
    """Language module for Old Persian toponyms."""

    language_code = "peo"
    language_name = "Old Persian"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Western Iranian > Old Persian"
    period = "c. 525–300 BCE (Achaemenid Empire)"
    script = "Xpeo"

    prefixes = [
        "Pars-",  # Persia itself (Pārsa)
        "Haxā-",  # from, out of
        "Upa-",  # near, by (cf. Skt. upa-)
        "Ava-",  # down (Avestan cognate)
        "Vi-",  # apart, through
    ]

    suffixes = [
        "-pārsa",  # Persia (ethnic/place)
        "-kāna",  # place of, -land (Sagartia = Asagarta-kāna?)
        "-āna",  # place suffix
        "-garda",  # city/enclosure (cf. Samarkand)
        "-stāna",  # place/land (early form of -stan)
        "-daya",  # wall, fortress
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "pars": "Pārsa (Persia – the homeland)",
        "parsa": "Pārsa (Persia, the Persian people)",
        "persepolis": "Pārsa (Greek: Persepolis = city of Persians)",
        "pasargadae": "Pāθragāda (camp/city of the Persians?)",
        "hagmatana": "Hagmatāna (meeting place – Ecbatana/Hamadan)",
        "ecbatana": "Hagmatāna (Greek form – meeting place)",
        "susa": "Šūšā (Old Persian form of Elamite Susa)",
        "babylon": "Bābiruš (Old Persian for Babylon < Akk.)",
        "sparda": "Sparda (Sardis, Lydia)",
        "mudraya": "Mudrāya (Egypt in Old Persian)",
        "haraiva": "Haraiva (Aria/Herat – rich in water)",
        "bakhtrish": "Bāxtriš (Bactria – land of camels?)",
        "suguda": "Suguda (Sogdia)",
        "hinduš": "Hinduš (India, Sindh)",
        "garda": "garda (city, enclosure, fortified place)",
        "stana": "stāna (place, standing – > -stan)",
        "daya": "didā/daya (wall, fortress)",
        "bandaka": "bandaka (vassal, subject)",
        "dahyu": "dahyu (land, province, people)",
        "xšaça": "xšaça (kingdom, power)",
        "arta": "arta (truth, cosmic order – cf. Vedic ṛta)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Persian toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower().replace("ā", "a").replace("š", "sh")

        sorted_prefixes = sorted(
            [p.rstrip("-").lower().replace("ā", "a").replace("š", "sh") for p in self.prefixes],
            key=len,
            reverse=True,
        )

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        sorted_suffixes = sorted(
            [s.lstrip("-").lower().replace("ā", "a").replace("š", "sh") for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]
            if remainder.startswith(("-", " ")):
                remainder = remainder[1:]
                prefix_part = form[: len(matched_prefix) + 1]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="prefix",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.7,
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
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        else:
            known = self.ELEMENT_MEANINGS.get(form_lower)
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    meaning=known,
                    confidence=0.6 if known else 0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Old Persian in origin."""
        form_lower = form.lower().replace("ā", "a")
        score = 0.0
        evidence: list[str] = []

        op_toponyms = [
            "parsa",
            "persepolis",
            "pasargadae",
            "hagmatana",
            "ecbatana",
            "sparda",
            "bakhtrish",
            "suguda",
            "haraiva",
        ]
        for name in op_toponyms:
            if name in form_lower:
                evidence.append(f"Known Old Persian toponym '{name}'")
                score += 0.5
                break

        if form_lower.endswith(("stan", "stana")):
            evidence.append("Iranian place suffix -stāna (place/land)")
            score += 0.3

        if form_lower.endswith(("gard", "garda")):
            evidence.append("Iranian city suffix -garda (enclosure)")
            score += 0.3

        op_elements = ["arta", "xshaca", "dahyu", "pars"]
        for elem in op_elements:
            if elem in form_lower:
                evidence.append(f"Old Persian element '{elem}'")
                score += 0.3
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Achaemenid (525–300 BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old Persian components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-").replace("ā", "a").replace("š", "sh")
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
                        sources=["Kent 1953", "Schmitt 2014"],
                    )
                )
        return candidates
