"""Modern Greek language module for toponymic analysis.

Modern Greek (Νέα Ελληνικά, ell) is the Hellenic language spoken in Greece
and Cyprus today. Its toponymy derives from ancient, Byzantine, and modern
strata. Key suffixes: -poli/-polis (city), -kastro (castle < Lat. castrum),
-chori (village). Note: byzantine_greek.py covers medieval Greek; this module
handles modern demotic forms and post-Ottoman-era naming conventions.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ModernGreekModule(BaseLanguageModule):
    """Language module for Modern Greek toponyms."""

    language_code = "ell"
    language_name = "Modern Greek"
    family = "Indo-European"
    branch = "Hellenic"
    period = "Modern (1453 CE–present)"
    script = "Grek"

    prefixes = [
        "Nea-",
        "Neo-",
        "Agios-",
        "Agia-",
        "Mega-",
        "Mikro-",
        "Ano-",
        "Kato-",
        "Palaio-",
    ]

    suffixes = [
        "-poli",
        "-polis",
        "-kastro",
        "-chori",
        "-chorion",
        "-oupoli",
        "-itsa",
        "-aki",
        "-aina",
        "-iko",
        "-issa",
        "-onas",
        "-ata",
    ]

    stems = [
        "petra",
        "potamos",
        "limni",
        "vouno",
        "kampos",
        "nero",
        "pyrgos",
        "chora",
        "megalo",
        "lefko",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "nea": "new (fem.)",
            "neo": "new (neut.)",
            "agios": "saint (masc.)",
            "agia": "saint (fem.)",
            "mega": "great",
            "mikro": "small",
            "ano": "upper",
            "kato": "lower",
            "palaio": "old",
            "poli": "city",
            "polis": "city",
            "kastro": "castle (< Lat. castrum)",
            "chori": "village",
            "chorion": "village (learned form)",
            "oupoli": "city (compound)",
            "itsa": "diminutive",
            "aki": "diminutive",
            "petra": "stone, rock",
            "potamos": "river",
            "limni": "lake",
            "vouno": "mountain",
            "kampos": "plain",
            "nero": "water",
            "pyrgos": "tower",
            "chora": "town, country",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Modern Greek toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

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
                        confidence=0.75,
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
        """Classify whether a name form belongs to Modern Greek."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Greek suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Greek prefix {prefix}-")
                score += 0.3
                break

        greek_elements = ["thessa", "niki", "athen", "patra", "pyrgos"]
        for elem in greek_elements:
            if elem in form_lower:
                evidence.append(f"Greek toponymic element '{elem}'")
                score += 0.2
                break

        greek_clusters = ["th", "ph", "ch", "ou", "ei"]
        for cl in greek_clusters:
            if cl in form_lower:
                evidence.append(f"Greek phonetic transcription '{cl}'")
                score += 0.15
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
            "poli": ("πόλις", "city", ["AGk. polis", "En. -polis"]),
            "polis": ("πόλις", "city", ["AGk. polis", "En. metropolis"]),
            "kastro": ("castrum", "castle (< Lat.)", ["It. castello", "Sp. castillo"]),
            "chori": ("χωρίον", "village", ["AGk. khōrion"]),
            "petra": ("πέτρα", "stone, rock", ["AGk. petra", "Lat. petra"]),
            "potamos": ("ποταμός", "river", ["AGk. potamos"]),
            "pyrgos": ("πύργος", "tower", ["AGk. pyrgos", "Lat. burgus"]),
            "limni": ("λίμνη", "lake", ["AGk. limnē"]),
            "vouno": ("βουνό", "mountain (< Slavic?)", ["Slavic *vŭnŭ?"]),
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
                        confidence=0.7,
                        cognates=cognates,
                        sources=["Babiniotis, Etymological Dictionary of Modern Greek"],
                    )
                )
        return candidates
