"""Luwian language module for toponymic analysis.

Luwian (xlu) is an Anatolian/IE language spoken in southern and western
Anatolia (16th–7th c. BCE). Written in Hieroglyphic Luwian and cuneiform.
Major toponymic substrate in Turkey.

Toponymic hallmarks:
- Suffixes: -wanda (place with water?), -ssa/-ssa (place),
  -nda (place, cf. Arzawa-Luwian), -alla (possessive)
- Troy = Wilusa, Tarhuntassa, Arzawa
- Important for understanding Anatolian place-name layers

Key references: Melchert 1993 "Cuneiform Luvian Lexicon",
Hawkins 2000 "Corpus of Hieroglyphic Luwian Inscriptions"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "wanda": "place (associated with water?)",
    "ssa": "place suffix",
    "nda": "place suffix",
    "alla": "possessive / belonging to",
    "iya": "adjectival",
    "assa": "place suffix (< older -ašša)",
    "ura": "nominal / place",
    "awa": "territory / land",
    "zzi": "verbal/agentive",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "wilusa": ("wilusa", "Wilusa (= Troy / Ilion)"),
    "tarhuntassa": ("tarḫuntašša", "Tarhuntassa (storm-god's city)"),
    "arzawa": ("arzawa", "Arzawa (western Anatolian kingdom)"),
    "lukka": ("lukka", "Lukka lands (= Lycia)"),
    "karkamissa": ("karkamišša", "Carchemish"),
    "milawanda": ("millawanda", "Milawanda (= Miletus)"),
    "apasa": ("apaša", "Apaša (= Ephesus?)"),
    "parha": ("parḫa", "Parha (= Perge?)"),
    "adanawa": ("adanawa", "Adanawa (= Adana region)"),
    "tarsa": ("tarša", "Tarša (= Tarsus)"),
    "harrана": ("ḫarrana", "Harran"),
    "pala": ("pala", "Pala (northern territory)"),
}

_PHONOLOGICAL_MARKERS = {"wn", "nd", "šš", "zz"}


class LuwianModule(BaseLanguageModule):
    """Language module for Luwian (xlu) toponyms."""

    language_code = "xlu"
    language_name = "Luwian"
    family = "Indo-European"
    branch = "Anatolian"
    period = "16th–7th c. BCE"
    script = "Hluw"

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
                    confidence=0.8,
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
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_meaning,
                    confidence=0.6,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        fl = form.lower()
        score = 0.0
        evidence: list[str] = []

        if fl in _KNOWN_ELEMENTS:
            score += 0.7
            evidence.append(f"Known Luwian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Luwian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Luwian phonological cluster '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="luwian" if score > 0.4 else None,
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
                        confidence=0.7,
                        cognates=[],
                        sound_changes=[],
                        sources=["Melchert 1993", "Hawkins 2000"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.55,
                        cognates=[],
                        sources=["Melchert 1993"],
                    )
                )
        return candidates
