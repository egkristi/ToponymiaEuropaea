"""Lydian language module for toponymic analysis.

Lydian (xld) is an Anatolian/IE language spoken in western Anatolia
(7th–3rd c. BCE). Limited corpus of ~100 inscriptions, mostly from Sardis.
Important substrate in western Turkish place-names.

Toponymic hallmarks:
- Suffixes: -da (locative?), -lis/-li (ethnic/adjectival), -nd-
- Capital Sardis (Sfard in Lydian)
- Anatolian vowel harmony features
- Connection to Etruscan debated (Tyrsenian hypothesis)

Key references: Gusmani 1964 "Lydisches Wörterbuch",
Melchert 2004 "Lydian" in Cambridge Encyclopedia of Ancient Languages
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "da": "locative / place",
    "lis": "ethnic / adjectival",
    "li": "ethnic / adjectival",
    "nd": "place (Anatolian substrate)",
    "as": "genitive / nominal",
    "id": "patronymic?",
    "av": "possessive",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "sfard": ("śfard", "Sardis (Lydian name)"),
    "sardis": ("śfard-is", "Sardis (Greek adaptation)"),
    "mermnad": ("mermnad", "Mermnad dynasty toponym"),
    "koloe": ("koloe", "Lake Koloe (near Sardis)"),
    "hypaipa": ("hypaipa", "Hypaipa (Lydian town)"),
    "tmolus": ("tmolus", "Mt. Tmolus (Bozdağ)"),
    "philadelphia": ("philadelphia", "Philadelphia (Alaşehir)"),
    "thyateira": ("thyateira", "Thyateira (Akhisar)"),
    "magnesia": ("magnesia", "Magnesia ad Sipylum"),
}

_PHONOLOGICAL_MARKERS = {"sf", "śf", "ñ", "λ"}


class LydianModule(BaseLanguageModule):
    """Language module for Lydian (xld) toponyms."""

    language_code = "xld"
    language_name = "Lydian"
    family = "Indo-European"
    branch = "Anatolian"
    period = "7th–3rd c. BCE"
    script = "Lydi"

    suffixes = list(_SUFFIXES.keys())
    prefixes: list[str] = []

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        if fl in _KNOWN_ELEMENTS:
            lemma, meaning = _KNOWN_ELEMENTS[fl]
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=lemma,
                    meaning=meaning,
                    confidence=0.75,
                )
            )
            return results

        matched_suffix = ""
        matched_meaning = ""
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                matched_suffix = sfx
                matched_meaning = meaning
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            sfx_part = form[len(form) - len(matched_suffix) :]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    confidence=0.45,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_meaning,
                    confidence=0.5,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.25,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        fl = form.lower()
        score = 0.0
        evidence: list[str] = []

        if fl in _KNOWN_ELEMENTS:
            score += 0.7
            evidence.append(f"Known Lydian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.25
                evidence.append(f"Lydian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Lydian phonological marker '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="lydian" if score > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            cl = comp.component.lower()
            if cl in _KNOWN_ELEMENTS:
                lemma, meaning = _KNOWN_ELEMENTS[cl]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.65,
                        cognates=[],
                        sound_changes=[],
                        sources=["Gusmani 1964", "Melchert 2004"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.5,
                        cognates=[],
                        sources=["Gusmani 1964"],
                    )
                )
        return candidates
