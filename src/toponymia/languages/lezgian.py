"""Lezgian language module for toponymic analysis.

Lezgian (лезги чӀал, lez) is a Northeast Caucasian (Lezgic) language spoken
in southern Dagestan (Russia) and northern Azerbaijan by ~800,000 speakers.
Key toponymic patterns: suffixes -ar (locative), -khyur (village), -kkal
(fortress); stems vats (brother), kal (fortress), suw (water). Border
region between Russia and Azerbaijan with layered Turkic/Persian influence.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LezgianModule(BaseLanguageModule):
    """Language module for Lezgian toponyms."""

    language_code = "lez"
    language_name = "Lezgian"
    family = "Northeast Caucasian"
    branch = "Lezgic (Dagestani)"
    period = "Modern (1800 CE–present)"
    script = "Cyrl"

    prefixes = [
        "Ts-",
        "K'-",
    ]

    suffixes = [
        "-ar",
        "-khyur",
        "-kkal",
        "-val",
        "-ikh",
        "-un",
        "-ul",
        "-dag",
    ]

    stems = [
        "vats",
        "kal",
        "suw",
        "k'wal",
        "dag",
        "mikh",
        "tar",
        "qazh",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "ts": "at, near (prefix)",
            "k'": "under (prefix)",
            "ar": "locative (place of)",
            "khyur": "village, settlement",
            "kkal": "fortress, stronghold",
            "val": "place, area",
            "ikh": "territory",
            "un": "belonging to (genitive)",
            "ul": "place (locative)",
            "dag": "mountain (< Turkic)",
            "vats": "brother (clan element)",
            "kal": "fortress",
            "suw": "water",
            "k'wal": "house, home",
            "mikh": "place, locality",
            "tar": "tree, forest",
            "qazh": "narrow passage",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Lezgian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 2:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.55,
                    )
                )
                form = form[len(prefix) :]
                form_lower = form.lower()
                break

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                pos = len(results)
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=pos,
                        morph_type="stem",
                        confidence=0.5,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=pos + 1,
                        morph_type="suffix",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.65,
                    )
                )
                return results

        pos = len(results)
        results.append(
            SegmentationResult(
                component=form,
                position=pos,
                morph_type="stem",
                confidence=0.3,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Lezgian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Lezgian suffix -{suffix}")
                score += 0.3
                break

        lezgic_clusters = ["ts'", "k'", "q'", "kh", "ch'"]
        for cl in lezgic_clusters:
            if cl in form_lower:
                evidence.append(f"Lezgic phonological element '{cl}'")
                score += 0.2
                break

        known_stems = ["akhty", "qusar", "derbent", "kasumkent", "kurakh"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Lezgian toponym stem '{stem}'")
                score += 0.3
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "ar": ("-ar", "locative (place of)", ["Tabasaran -ar"]),
            "khyur": ("xüar", "village", ["Tabasaran xür"]),
            "kkal": ("kkal", "fortress", ["Agul kkal"]),
            "vats": ("vac", "brother (clan territory)", ["Tabasaran vac"]),
            "kal": ("kal", "fortress, stronghold", []),
            "suw": ("süw", "water", ["Agul shiv"]),
            "k'wal": ("k'wal", "house, home", ["Tabasaran k'ul"]),
            "dag": ("dag", "mountain (< Turkic dağ)", ["Az. dağ", "Turk. dağ"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower().rstrip("-")
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.55,
                        cognates=cognates,
                        sources=["Haspelmath, A Grammar of Lezgian"],
                    )
                )
        return candidates
