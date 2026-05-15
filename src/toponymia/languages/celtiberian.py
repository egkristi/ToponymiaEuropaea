"""Celtiberian language module for toponymic analysis.

Celtiberian (xce) is a Continental Celtic language spoken in central Spain
(3rd–1st c. BCE). Known from inscriptions including the Botorrita bronzes,
coin legends, and tesserae. Distinct from Iberian (non-IE).

Toponymic hallmarks:
- Suffixes: -briga (fortress), -cama (?, debated)
- Elements shared with Gaulish but with Hispano-Celtic phonology
- City names: Segobriga (near Cuenca), Numantia, Contrebia, Uxama
- Celtiberian script (adapted Iberian semi-syllabary)

Key references: Jordán Cólera 2004, Untermann 1997 "MLH IV",
               Villar et al. 2001
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "briga": "fortified place / hill-fort",
    "cama": "unknown (place element?)",
    "ama": "water? / settlement?",
    "avo": "ethnic / place suffix",
    "aeco": "adjectival / ethnic",
    "icum": "place / ethnic suffix",
}

_PREFIXES: dict[str, str] = {
    "sego": "victory / strength",
    "contr": "coming together (< *kom-treb-)",
    "uxo": "high / upper",
    "arco": "bear? / high?",
    "nemeto": "sacred grove",
    "luto": "swamp / marsh",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "segobriga": ("segobriga", "Segobriga (< sego- 'victory' + -briga 'fort')"),
    "numantia": ("numantia", "Numantia (Soria, contested etymology)"),
    "contrebia": ("contrebia", "Contrebia (< *kom-treb-ia 'coming together')"),
    "uxama": ("uxama", "Burgo de Osma (< *uxo- 'high' + -ama)"),
    "arcobriga": ("arcobriga", "Monreal de Ariza (< arco- + -briga)"),
    "nertobriga": ("nertobriga", "La Almunia (< nerto- 'strength' + -briga)"),
    "turiaso": ("turiaso", "Tarazona (Celtiberian mint city)"),
    "bilbilis": ("bilbilis", "Calatayud (Celtiberian name)"),
    "clunia": ("clunia", "Peñalba de Castro (< *klounio- meadow?)"),
    "termes": ("termes", "Tiermes (Celtiberian city)"),
    "segontia": ("segontia", "Sigüenza (< sego- + -ontia)"),
}


class CeltiberianModule(BaseLanguageModule):
    """Language module for Celtiberian (xce) toponyms."""

    language_code = "xce"
    language_name = "Celtiberian"
    family = "Indo-European"
    branch = "Celtic > Continental Celtic > Hispano-Celtic"
    period = "3rd–1st c. BCE"
    script = "Latn"

    suffixes = list(_SUFFIXES.keys())
    prefixes = list(_PREFIXES.keys())

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

        # Check for -briga compound (most common)
        if "briga" in fl and fl.index("briga") > 0:
            split_idx = fl.index("briga")
            stem = form[:split_idx]
            sfx_part = form[split_idx:]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_modifier",
                    confidence=0.65,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="compound_head",
                    lemma="briga",
                    meaning="fortified place / hill-fort",
                    confidence=0.75,
                )
            )
            return results

        # Try prefix matching
        matched_prefix = ""
        matched_pfx_meaning = ""
        for pfx, meaning in sorted(_PREFIXES.items(), key=lambda x: -len(x[0])):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                matched_prefix = pfx
                matched_pfx_meaning = meaning
                break

        if matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    meaning=matched_pfx_meaning,
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    confidence=0.4,
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
            evidence.append(f"Known Celtiberian toponym: {fl}")

        if "briga" in fl:
            score += 0.35
            evidence.append("Contains -briga (Celtic fortress)")

        for pfx in sorted(_PREFIXES, key=len, reverse=True):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                score += 0.25
                evidence.append(f"Celtiberian prefix {pfx}-")
                break

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if sfx != "briga" and fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.2
                evidence.append(f"Celtiberian suffix -{sfx}")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="celtiberian" if score > 0.4 else None,
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
                        cognates=["cf. Gaulish -dunum", "Welsh din"],
                        sources=["Jordán Cólera 2004", "Untermann 1997"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=["cf. Gaulish cognates"],
                        sources=["Untermann 1997"],
                    )
                )
            elif cl in _PREFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_PREFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=[],
                        sources=["Villar et al. 2001"],
                    )
                )
        return candidates
