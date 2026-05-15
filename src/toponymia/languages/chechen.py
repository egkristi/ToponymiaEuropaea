"""Chechen language module for toponymic analysis.

Chechen (нохчийн мотт, che) is a Northeast Caucasian (Nakh) language spoken
in Chechnya and Ingushetia (Russia). Key toponymic patterns: suffixes -chu
(inside/place), -n (locative), -akhk (settlement); stems lam (mountain),
khi (water), are (plain). Tower architecture and clan territories reflected
in place-names. Related to Ingush and Bats.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ChechenModule(BaseLanguageModule):
    """Language module for Chechen toponyms."""

    language_code = "che"
    language_name = "Chechen"
    family = "Northeast Caucasian"
    branch = "Nakh (Vainakh)"
    period = "Modern (1800 CE–present)"
    script = "Cyrl"

    prefixes = [
        "Nakh-",
        "Nokh-",
    ]

    suffixes = [
        "-chu",
        "-n",
        "-akhk",
        "-aul",
        "-nie",
        "-ta",
        "-che",
        "-urt",
    ]

    stems = [
        "lam",
        "khi",
        "are",
        "berd",
        "urt",
        "ali",
        "ghala",
        "duk",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "nakh": "people (prefix)",
            "nokh": "plough, arable (prefix)",
            "chu": "inside, within (locative)",
            "n": "genitive/locative case",
            "akhk": "settlement, village",
            "aul": "village (< Turkic)",
            "nie": "place (locative suffix)",
            "ta": "locative (at, on)",
            "che": "inside, within",
            "urt": "flat ground, plateau",
            "lam": "mountain",
            "khi": "water, river",
            "are": "plain, flat area",
            "berd": "cliff, bank",
            "ali": "spring, stream",
            "ghala": "tower, fortress",
            "duk": "ridge, crest",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Chechen toponym into morphological components."""
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
                        confidence=0.6,
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
        """Classify whether a name form belongs to Chechen."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Chechen suffix -{suffix}")
                score += 0.3
                break

        nakh_clusters = ["kh", "gh", "chk", "lam", "duk"]
        for cl in nakh_clusters:
            if cl in form_lower:
                evidence.append(f"Nakh phonological element '{cl}'")
                score += 0.2
                break

        known_stems = ["urus", "shatoi", "vedeno", "itum", "sharoy"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Chechen toponym stem '{stem}'")
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
            "lam": ("lam", "mountain", ["Ingush lam", "Bats lam"]),
            "khi": ("ẋi", "water, river", ["Ingush ẋi"]),
            "are": ("are", "plain, flat area", ["Ingush are"]),
            "ghala": ("ġala", "tower, fortress", ["Ingush ġala"]),
            "chu": ("-chu", "inside, locative", ["Ingush -cho"]),
            "akhk": ("-aḥk", "settlement", []),
            "duk": ("duq", "ridge, mountain crest", ["Ingush duq"]),
            "berd": ("berd", "cliff, bank", ["Ingush berd"]),
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
                        confidence=0.6,
                        cognates=cognates,
                        sources=["Vagapov, Etymological Dictionary of Chechen"],
                    )
                )
        return candidates
