"""Georgian language module for toponymic analysis.

Georgian (ქართული, kat) is a Kartvelian language, unrelated to Indo-European,
spoken in Georgia (South Caucasus). It has a unique script (Mkhedruli) and
agglutinative morphology. Key toponymic patterns: suffixes -eti (land of),
-isi (place), -eli (from/of), -uri (adj.); prefixes Sa- (place of), Me-
(place where). Tbilisi < tbili 'warm' + -isi 'place'. Rich in descriptive
geography: mountains, rivers, valleys of the Caucasus.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class GeorgianModule(BaseLanguageModule):
    """Language module for Georgian toponyms."""

    language_code = "kat"
    language_name = "Georgian"
    family = "Kartvelian"
    branch = "South Caucasian (Kartvelian)"
    period = "Modern (1700 CE–present)"
    script = "Geor"

    prefixes = [
        "Sa-",
        "Me-",
        "Na-",
        "Tsa-",
    ]

    suffixes = [
        "-eti",
        "-isi",
        "-eli",
        "-uri",
        "-ari",
        "-uli",
        "-iani",
        "-ati",
        "-obi",
        "-oni",
        "-ubi",
        "-tsikhe",
    ]

    stems = [
        "tbili",
        "mtsvane",
        "tetri",
        "shavi",
        "tsq'ali",
        "mta",
        "ghele",
        "kari",
        "qala",
        "didi",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "sa": "place of (circumfix prefix)",
            "me": "place where (prefix)",
            "na": "former place (prefix)",
            "tsa": "at, by (prefix)",
            "eti": "land of, region",
            "isi": "place",
            "eli": "from, of (origin)",
            "uri": "adjectival (belonging to)",
            "ari": "place of",
            "uli": "diminutive/locative",
            "iani": "place of (people)",
            "ati": "collective/place",
            "obi": "region, area",
            "oni": "place",
            "tsikhe": "fortress",
            "tbili": "warm",
            "mtsvane": "green",
            "tetri": "white",
            "shavi": "black",
            "mta": "mountain",
            "ghele": "river",
            "kari": "wind, gate",
            "qala": "town (< Arabic)",
            "didi": "great, large",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Georgian toponym into morphological components."""
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
                        confidence=0.65,
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
                        confidence=0.7,
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
        """Classify whether a name form belongs to Georgian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Georgian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 2:
                evidence.append(f"Georgian prefix {prefix}-")
                score += 0.25
                break

        georgian_clusters = ["ts", "dz", "kh", "gh", "tsk", "tsq"]
        for cl in georgian_clusters:
            if cl in form_lower:
                evidence.append(f"Georgian consonant cluster '{cl}'")
                score += 0.2
                break

        georgian_stems = ["tbil", "kutai", "batumi", "mtskhet", "gori"]
        for stem in georgian_stems:
            if stem in form_lower:
                evidence.append(f"Georgian toponymic stem '{stem}'")
                score += 0.25
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
            "eti": ("-eti", "land of, region", ["Svan. -et"]),
            "isi": ("-isi", "place (locative)", ["OGeo. -isi"]),
            "tsikhe": ("c'ixe", "fortress", ["OGeo. c'ixe"]),
            "tbili": ("tbili", "warm", ["OGeo. tbili"]),
            "mta": ("mt'a", "mountain", ["Svan. mūšg"]),
            "qala": ("qala", "town (< Ar. qal'a)", ["Ar. qal'a", "Pers. qal'eh"]),
            "didi": ("didi", "great, large", ["OGeo. didi"]),
            "kari": ("k'ari", "gate, door", ["OGeo. k'ari"]),
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
                        sources=["Klimov, Etymological Dictionary of Kartvelian Languages"],
                    )
                )
        return candidates
