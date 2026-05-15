"""Avar (Caucasian) language module for toponymic analysis.

Avar (авар мацӀ, ava) is a Northeast Caucasian (Avar-Andic) language spoken
in Dagestan (Russia) by ~800,000 speakers. NOT the steppe Avars (Turkic/mixed,
separate module). Key toponymic patterns: suffixes -tl (locative), -b (place),
-da (at), -ib (village); mountain village toponymy. Historical capital:
Khunzakh. Dagestan = 'land of mountains' (Turkic).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AvarCaucasianModule(BaseLanguageModule):
    """Language module for Avar (Caucasian) toponyms."""

    language_code = "ava"
    language_name = "Avar (Caucasian)"
    family = "Northeast Caucasian"
    branch = "Avar-Andic (Dagestani)"
    period = "Modern (1800 CE–present)"
    script = "Cyrl"

    prefixes = [
        "Ts-",
        "Kh-",
    ]

    suffixes = [
        "-tl",
        "-b",
        "-da",
        "-ib",
        "-oh",
        "-ub",
        "-ikh",
        "-ab",
    ]

    stems = [
        "meher",
        "tl'ar",
        "rokh",
        "bak'",
        "gidatl",
        "khunz",
        "gor",
        "tlan",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "ts": "at, near (prefix)",
            "kh": "under, below (prefix)",
            "tl": "locative (on, at)",
            "b": "place, area",
            "da": "at, by (locative)",
            "ib": "village, settlement",
            "oh": "in, within",
            "ub": "place (locative)",
            "ikh": "place, territory",
            "ab": "place of",
            "meher": "sun",
            "tl'ar": "stone, rock",
            "rokh": "forest",
            "bak'": "head, top, peak",
            "gidatl": "people of the mountain",
            "khunz": "watchpost (Khunzakh)",
            "gor": "hill, mound",
            "tlan": "flat place",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Avar toponym into morphological components."""
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
        """Classify whether a name form belongs to Avar (Caucasian)."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Avar suffix -{suffix}")
                score += 0.3
                break

        avar_clusters = ["tl", "kh", "ts", "tl'", "q'"]
        for cl in avar_clusters:
            if cl in form_lower:
                evidence.append(f"Avar-Andic phonological element '{cl}'")
                score += 0.2
                break

        known_stems = ["khunz", "gidatl", "gunib", "botlikh", "tindi"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Avar toponym stem '{stem}'")
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
            "tl": ("-tl", "locative (on, at)", ["Andic *-tl"]),
            "meher": ("meḥer", "sun", []),
            "tl'ar": ("tl'ar", "stone, rock", ["Andic *tl'ar"]),
            "bak'": ("bak'", "head, peak, summit", ["Andic *bak'"]),
            "khunz": ("xunz", "watchpost, lookout (Khunzakh)", []),
            "gor": ("gor", "hill, mound", []),
            "rokh": ("rox", "forest, woods", []),
            "b": ("-b", "place (locative class marker)", []),
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
                        sources=["Saidov, Avar-Russian Dictionary"],
                    )
                )
        return candidates
