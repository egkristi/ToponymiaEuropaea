"""Old Prussian language module for toponymic analysis.

Old Prussian (Prūsiskan) was a Western Baltic language spoken in what
is now Kaliningrad Oblast, NE Poland, and Lithuania Minor until ~1700 CE:
- Extinct by early 18th century due to Teutonic Knights' colonization
- Left extensive toponymic substrate in East Prussia (now Kaliningrad/Warmia-Masuria)
- Related to Lithuanian/Latvian but distinct
- Many town names preserve Prussian roots under German/Polish overlays
- Viking contacts: Wulfstan's description of Estland (=Prussia) in Alfred's Orosius
- Truso (Elbląg) was a major Viking trading post in Prussian territory

Key references:
- Mažiulis 1988–1997 "Prūsų kalbos etimologinis žodynas"
- Toporov 1975–1990 "Prusskij jazyk"
- Gerullis 1922 "Die altpreußischen Ortsnamen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldPrussianModule(BaseLanguageModule):
    """Language module for Old Prussian toponyms."""

    language_code = "prg"  # ISO 639-3 for Old Prussian
    language_name = "Old Prussian"
    family = "Indo-European"
    branch = "Baltic > Western Baltic"
    period = "1200–1700 CE (attested)"
    script = "Latn"

    prefixes = [
        "Pil-",  # castle (pilsāts; cf. Pillau/Baltijsk)
        "Kaim-",  # village (< kaims)
        "Gal-",  # end, boundary (cf. Galinden)
        "Sar-",  # reddish
        "Nadr-",  # Nadravian (tribal, Nadrau)
        "Sam-",  # Sambian/Samland (tribal)
        "Prus-",  # Prussian
        "War-",  # river prefix (warm-?)
        "Til-",  # Tilsit (< tilžė marsh)
    ]

    suffixes = [
        "-kaims",  # village (cf. Lithuanian -kaimis, Karkaims)
        "-ape",  # river (cf. Lith. upė, Angerapp→Angrapa)
        "-garbs",  # mountain (cf. Lith. kalnas?)
        "-pelk",  # swamp (cf. Baltic *pelkē, Lith. pelkė)
        "-lauks",  # field (cf. Lith. laukas)
        "-medis",  # forest, tree (cf. Lith. medis)
        "-angis",  # narrow (in river names)
        "-awa",  # river (< IE *akwa, cf. Got. aƕa)
        "-pilsāts",  # castle-place
        "-wangus",  # meadow, cleared land
        "-kelan",  # road, path
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "pil": "castle, fortress (pilsāts)",
        "kaim": "village, settlement (kaims)",
        "gal": "end, boundary (gallan)",
        "sar": "reddish, red",
        "nadr": "Nadravian (Baltic tribal name)",
        "sam": "Sambian (Baltic tribal name; Samland)",
        "prus": "Prussian (tribal name)",
        "war": "water, river (related)",
        "til": "marshy area (tilžė)",
        "kaims": "village",
        "ape": "river (cf. Lithuanian upė)",
        "garbs": "mountain, hill",
        "pelk": "swamp, bog",
        "lauks": "field, open land",
        "medis": "forest, tree, wood",
        "angis": "narrow, snake (in hydronyms)",
        "awa": "river, water",
        "wangus": "meadow, cleared land",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Prussian toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            if matched_prefix and stem.lower().startswith(matched_prefix):
                results.append(
                    SegmentationResult(
                        component=stem[: len(matched_prefix)],
                        position=0,
                        morph_type="compound_modifier",
                        lemma=matched_prefix,
                        confidence=0.7,
                    )
                )
                mid = stem[len(matched_prefix) :]
                if mid:
                    results.append(
                        SegmentationResult(
                            component=mid,
                            position=1,
                            morph_type="stem",
                            lemma=mid.lower(),
                            confidence=0.4,
                        )
                    )
            else:
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="compound_modifier",
                        lemma=stem.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.75,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.4,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="simplex",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Old Prussian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Old Prussian diagnostic suffixes
        pruss_suffixes = ["kaims", "ape", "pelk", "lauks", "wangus"]
        for marker in pruss_suffixes:
            if form_lower.endswith(marker):
                evidence.append(f"Old Prussian suffix -{marker}")
                score += 0.4
                break

        # Old Prussian diagnostic prefixes/elements
        pruss_elements = ["pil", "sam", "nadr", "gal"]
        for marker in pruss_elements:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Old Prussian element {marker}-")
                score += 0.25
                break

        # Prussian tribal reference
        if "prus" in form_lower:
            evidence.append("Prussian tribal name")
            score += 0.3

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–1700 CE (attested Prussian)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old Prussian components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            meaning = self.ELEMENT_MEANINGS.get(comp.lemma.lower().rstrip("-"))
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp.lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                    )
                )
        return candidates
