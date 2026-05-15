"""Proto-Italic language module.

Proto-Italic is the reconstructed common ancestor of the Italic languages
(Latin, Oscan, Umbrian, Faliscan, etc.), dating to the 2nd millennium BCE.
Key toponymic elements include *teutā (people/territory > Teutoni),
*kastrom (settlement > castro/chester), and *wīkos (village > -wick/-wich).
Important for understanding the earliest layer of Italian and western
Mediterranean place-names.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ProtoItalicModule(BaseLanguageModule):
    """Language module for Proto-Italic toponyms."""

    language_code = "itc"
    language_name = "Proto-Italic"
    family = "Indo-European"
    branch = "Italic (reconstructed ancestor)"
    period = "2nd millennium BCE (reconstructed)"
    script = "Latn"

    suffixes = [
        "-kastrom",  # settlement, fort (> castro/chester)
        "-aikom",  # settlement (> Latin -vīcus)
        "-toutā",  # people, territory
        "-akrom",  # hill, high point (> Latin acer)
        "-onā",  # river suffix
        "-entom",  # participial
    ]

    prefixes = [
        "Teut-",  # people/territory (> Teutoni, Tuderto-)
        "Nouo-",  # new (> Latin novus)
        "Albo-",  # white (> Latin albus)
        "Medi-",  # middle (> Latin medius)
        "Magno-",  # great (> Latin magnus)
    ]

    stems = [
        "teutā",  # people (> Oscan touto, Latin tōtus)
        "kastrom",  # fort (> Latin castrum, Oscan castrous)
        "wīkos",  # village (> Latin vīcus)
        "oppidom",  # fortified town (> Latin oppidum)
        "ager",  # field (> Latin ager)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Proto-Italic toponym."""
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
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.5,
                )
            )
        else:
            # Check for known prefixes
            matched_prefix = None
            for prefix in sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True):
                if form_lower.startswith(prefix.lower()):
                    matched_prefix = prefix
                    break

            if matched_prefix:
                results.append(
                    SegmentationResult(
                        component=form[: len(matched_prefix)],
                        position=0,
                        morph_type="compound_modifier",
                        lemma=matched_prefix,
                        confidence=0.5,
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
        """Classify whether a name form is likely Proto-Italic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"PItal. element *-{suffix}")
                score += 0.35
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"PItal. element *{prefix}-")
                score += 0.3
                break

        # Italic reflexes in modern forms
        italic_reflexes = ["castr", "teut", "vic", "oppid"]
        for reflex in italic_reflexes:
            if reflex in form_lower:
                evidence.append(f"Italic reflex *{reflex}-")
                score += 0.25
                break

        # Osco-Umbrian specific markers
        if "tud" in form_lower or "tout" in form_lower:
            evidence.append("Osco-Umbrian *toutā reflex")
            score += 0.2

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="bronze-age-italic" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "kastrom": ("*kastrom", "settlement, fort", ["Latin castrum", "Oscan castrous"]),
            "toutā": ("*teutā", "people, territory", ["Oscan touto", "Umbrian tota"]),
            "aikom": ("*woikom", "settlement, village", ["Latin vīcus", "Oscan víkfo"]),
            "teut": ("*teutā", "people, territory", ["Oscan touto", "Celtic *teutā"]),
            "nouo": ("*nowos", "new", ["Latin novus", "Oscan nuvlanús"]),
            "albo": ("*albos", "white", ["Latin albus", "Umbrian alfu"]),
            "medi": ("*medios", "middle", ["Latin medius", "Oscan mefiaí"]),
            "magno": ("*magnos", "great", ["Latin magnus"]),
            "akrom": ("*akrom", "point, summit", ["Latin ācer", "Oscan akrid"]),
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
                        sound_changes=["PIE *dh > PItal. *f (initially)", "PIE *bh > PItal. *f"],
                        sources=["de Vaan 2008", "Buck 1904"],
                    )
                )

        return candidates
