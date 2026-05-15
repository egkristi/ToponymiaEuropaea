"""Romani language module for toponymic analysis.

Romani (rom) is an Indo-Aryan language spoken by Roma communities across
Europe. While Roma have been historically nomadic and few places bear
official Romani names, internal community toponyms and informal place
references use Romani vocabulary: gav (village), bar (stone), pani (water),
drom (road), vast (hand/place). Contact vocabulary from every host country
(Greek, Romanian, Hungarian, Slavic, German) is integrated into local
Romani dialects, creating distinctive hybrid place references.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class RomaniModule(BaseLanguageModule):
    """Language module for Romani toponyms."""

    language_code = "rom"
    language_name = "Romani"
    family = "Indo-European"
    branch = "Indo-Iranian > Indo-Aryan"
    period = "Medieval–Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Baro-",
        "Tikno-",
        "Nevo-",
        "Purano-",
    ]

    suffixes = [
        "-ava",
        "-ica",
        "-esti",
        "-ipe",
        "-imos",
        "-ipe",
    ]

    stems = [
        "gav",
        "bar",
        "pani",
        "drom",
        "vast",
        "kher",
        "vesh",
        "len",
        "phuv",
        "yag",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "baro": "big, great",
            "tikno": "small, little",
            "nevo": "new",
            "purano": "old",
            "gav": "village",
            "bar": "stone, rock",
            "pani": "water",
            "drom": "road, way",
            "vast": "hand, place",
            "kher": "house",
            "vesh": "forest",
            "len": "river",
            "phuv": "earth, ground",
            "yag": "fire",
            "ava": "place (suffix)",
            "ipe": "abstract noun suffix",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Romani toponym into morphological components."""
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
                        confidence=0.4,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=pos + 1,
                        morph_type="suffix",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.5,
                    )
                )
                return results

        # Try matching known stems within the form
        pos = len(results)
        for stem in sorted(self.stems, key=len, reverse=True):
            if form_lower == stem or form_lower.startswith(stem):
                results.append(
                    SegmentationResult(
                        component=form[: len(stem)],
                        position=pos,
                        morph_type="stem",
                        lemma=stem,
                        meaning=self._element_meaning(stem),
                        confidence=0.5,
                    )
                )
                if len(form) > len(stem):
                    results.append(
                        SegmentationResult(
                            component=form[len(stem) :],
                            position=pos + 1,
                            morph_type="suffix",
                            confidence=0.3,
                        )
                    )
                return results

        results.append(
            SegmentationResult(
                component=form,
                position=pos,
                morph_type="stem",
                confidence=0.2,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Romani."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        romani_words = ["gav", "bar", "pani", "drom", "kher", "vesh", "phuv"]
        for word in romani_words:
            if word in form_lower:
                evidence.append(f"Romani lexical element '{word}'")
                score += 0.35
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Romani prefix {prefix}-")
                score += 0.25
                break

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Romani-contact suffix -{suffix}")
                score += 0.15
                break

        indic_features = ["ph", "bh", "dh", "kh"]
        for feat in indic_features:
            if feat in form_lower:
                evidence.append(f"Indo-Aryan aspirate '{feat}'")
                score += 0.2
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
            "gav": ("grāma", "village (< Skt. grāma)", ["Skt. grāma", "Hi. gāṁv"]),
            "bar": ("*bāra", "stone, garden", ["Hi. bāṛā", "Skt. vāṭa"]),
            "pani": ("pānīya", "water (< Skt.)", ["Hi. pānī", "Skt. pānīya"]),
            "drom": ("*dromo-", "road (< Gk. dromos)", ["Gk. dromos"]),
            "kher": ("gṛha", "house (< Skt.)", ["Hi. ghar", "Skt. gṛha"]),
            "vesh": ("*vṛkṣa", "forest (< Skt. tree)", ["Skt. vṛkṣa"]),
            "phuv": ("*bhūmi", "earth (< Skt.)", ["Skt. bhūmi", "Hi. bhūm"]),
            "vast": ("hasta", "hand (< Skt.)", ["Skt. hasta", "Hi. hāth"]),
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
                        confidence=0.6,
                        cognates=cognates,
                        sources=["Turner, Comparative Dictionary of Indo-Aryan Languages"],
                    )
                )
        return candidates
