"""Mirandese language module for toponymic analysis.

Mirandese (mirandés) is an Astur-Leonese Romance language spoken in
the Terra de Miranda region of northeastern Portugal (Miranda do Douro).
It is the only officially recognized minority language in Portugal.
Its toponymy reflects its Leonese heritage and Portuguese contact.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MirandeseModule(BaseLanguageModule):
    """Language module for Mirandese toponyms."""

    language_code = "mwl"
    language_name = "Mirandese"
    family = "Indo-European"
    branch = "Romance > Western > Ibero-Romance > Astur-Leonese"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Val-",
        "Fonte-",
        "Lhano-",
        "Monte-",
        "San-",
        "Ribo-",
        "Cabeço-",
        "Fraga-",
        "Penha-",
        "Canhada-",
    ]

    suffixes = [
        "-ino",
        "-eiro",
        "-oso",
        "-iego",
        "-ica",
        "-ales",
        "-anha",
        "-ido",
        "-ino",
        "-anca",
        "-iço",
        "-eno",
    ]

    stems = [
        "fonte",
        "lhano",
        "val",
        "monte",
        "ribo",
        "fraga",
        "penha",
        "cabeço",
        "canhada",
        "lhamedo",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()
        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                results.append(
                    SegmentationResult(
                        component=stem, position=0, morph_type="compound_modifier", confidence=0.6
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=1,
                        morph_type="compound_head",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.7,
                    )
                )
                return results
        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.65,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(prefix) :], position=1, morph_type="stem", confidence=0.5
                    )
                )
                return results
        results.append(
            SegmentationResult(component=form, position=0, morph_type="stem", confidence=0.3)
        )
        return results

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "val": "valley",
            "fonte": "spring, fountain",
            "lhano": "plain, flat area",
            "monte": "mountain, woodland",
            "san": "saint",
            "ribo": "riverbank",
            "cabeço": "hilltop",
            "fraga": "crag, rocky place",
            "penha": "rock, cliff",
            "canhada": "narrow valley",
            "ino": "diminutive",
            "eiro": "place of, agent (< -arium)",
            "oso": "full of, abounding in",
            "iego": "pertaining to",
            "ica": "diminutive",
            "ales": "collective",
            "anha": "related to",
            "ido": "characterized by",
            "anca": "place of",
            "iço": "diminutive/pejorative",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Mirandese."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Mirandese suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Mirandese prefix {prefix}-")
                score += 0.25
                break
        # Mirandese lh- initial (palatalized l-, like Asturian ll-)
        if form_lower.startswith("lh"):
            evidence.append("Mirandese initial lh- (palatalized L-)")
            score += 0.35
        # Mirandese diphthongs ie, uo
        if "ie" in form_lower or "uo" in form_lower:
            evidence.append("Mirandese diphthong (ie/uo)")
            score += 0.15
        # Leonese features: -iego suffix
        if form_lower.endswith("iego"):
            evidence.append("Leonese -iego suffix")
            score += 0.2
        # Distinction from Portuguese: preserved /f/
        if "nh" in form_lower:
            evidence.append("Nasal palatal nh (shared with Portuguese orthography)")
            score += 0.1
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "fonte": ("fontem", "spring", ["Pt. fonte", "Sp. fuente", "Ast. fonte"]),
            "lhano": ("planum", "flat area", ["Ast. llanu", "Sp. llano"]),
            "monte": ("montem", "mountain", ["Pt. monte", "Sp. monte"]),
            "val": ("vallem", "valley", ["Pt. vale", "Sp. valle"]),
            "penha": ("pinnam", "cliff", ["Pt. penha", "Sp. peña"]),
            "fraga": ("*fragam", "crag (Celtic/pre-Roman)", ["Pt. fraga", "Gl. fraga"]),
            "ribo": ("ripam", "riverbank", ["Pt. riba", "Sp. ribera"]),
            "cabeço": ("*capitium", "hilltop", ["Pt. cabeço"]),
            "canhada": ("*cannadam", "narrow valley", ["Pt. canhada"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.65,
                        cognates=cognates,
                        sources=["Ferreira 2001", "Mourinho 1987"],
                    )
                )
        return candidates
