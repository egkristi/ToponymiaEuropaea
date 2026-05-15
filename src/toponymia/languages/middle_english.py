"""Middle English language module.

Middle English (1100-1500 CE) developed after the Norman Conquest.
Norman French influence introduced a significant layer of re-namings
and additions to English toponymy: Beau- prefix, -castle, -mount.
Important for dating English place-name forms and identifying the
Anglo-Norman stratum.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MiddleEnglishModule(BaseLanguageModule):
    """Language module for Middle English toponyms."""

    language_code = "enm"
    language_name = "Middle English"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Anglo-Frisian"
    period = "1100-1500 CE"
    script = "Latn"

    suffixes = [
        "-castle",  # Norman addition
        "-mount",  # Norman addition
        "-borough",  # < OE burh, ME respelling
        "-bridge",  # < OE brycg
        "-bury",  # < OE burh/byrig
        "-chester",  # < Lat. castra, via OE ceaster
        "-field",  # < OE feld
        "-ford",  # < OE ford
        "-ham",  # < OE hām
        "-minster",  # < OE mynster < Lat. monasterium
        "-ton",  # < OE tūn
        "-wick",  # < OE wīc
        "-worth",  # < OE worþ
        "-ley",  # < OE lēah
        "-hurst",  # < OE hyrst
    ]

    prefixes = [
        "Beau-",  # Norman: beautiful
        "Bel-",  # Norman: beautiful
        "Mont-",  # Norman: mountain
        "Pont-",  # Norman: bridge
        "Chapel-",  # Norman: chapel
        "Castle-",  # Norman: castle
        "Kirk-",  # Norse influence (church)
        "New-",  # ME new (replacing OE niwe)
        "Great-",  # ME distinguishing prefix
        "Little-",  # ME distinguishing prefix
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Middle English toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()):
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            if stem:
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="compound_modifier",
                        confidence=0.6,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.7,
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
        """Classify whether a name form is likely Middle English."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.4
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Norman-French layer indicators
        norman_markers = ["beau", "bel", "mont", "pont", "castle"]
        for m in norman_markers:
            if m in form_lower:
                evidence.append(f"Anglo-Norman element '{m}'")
                score += 0.2
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="post-conquest" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "castle": ("castel", "castle (< AN)", ["AN castel", "Lat. castellum"]),
            "mount": ("mount", "hill (< AN mont)", ["AN mont", "Lat. mons"]),
            "borough": ("burgh", "fortified place", ["OE burh", "ON borg"]),
            "bridge": ("brigge", "bridge", ["OE brycg"]),
            "bury": ("bury", "fortification", ["OE burh/byrig"]),
            "chester": ("cestre", "Roman fort", ["Lat. castra"]),
            "ford": ("ford", "river crossing", ["OE ford"]),
            "ham": ("ham", "homestead", ["OE hām"]),
            "ton": ("toun", "enclosed settlement", ["OE tūn"]),
            "ley": ("leye", "clearing, meadow", ["OE lēah"]),
            "minster": ("mynstre", "monastery", ["Lat. monasterium"]),
        }

        candidates: list[EtymologyCandidate] = []
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in meanings:
                lemma, meaning, cognates = meanings[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=cognates,
                        sound_changes=["OE ā > ME ō", "OE ȳ > ME i/u/e"],
                        sources=["MED", "EPNS surveys"],
                    )
                )

        return candidates
