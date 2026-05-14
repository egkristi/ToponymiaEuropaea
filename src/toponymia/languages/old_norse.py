"""Old Norse language module.

Handles morphological segmentation and classification of Old Norse
toponymic elements. Old Norse (norrønt) was spoken ca. 700-1350 CE
and is the source of the majority of Scandinavian place name elements.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldNorseModule(BaseLanguageModule):
    """Language module for Old Norse (norrønt) toponyms."""

    language_code = "non"  # ISO 639-3 for Old Norse
    language_name = "Old Norse"
    family = "Indo-European"
    branch = "Germanic > North Germanic"
    period = "700-1350 CE"
    script = "Latn"

    # Common Old Norse toponymic suffixes (settlement names)
    suffixes = [
        "-heim",
        "-heimr",  # home, settlement
        "-staðir",
        "-stad",  # place, farm
        "-bý",
        "-by",
        "-bø",  # farm, settlement
        "-land",  # land
        "-vin",
        "-vin",  # meadow (very old, possibly pre-Norse)
        "-nes",
        "-nes",  # headland, promontory
        "-ey",
        "-øy",  # island
        "-vík",
        "-vik",  # bay, inlet
        "-fjǫrðr",
        "-fjord",  # fjord
        "-dalr",
        "-dal",  # valley
        "-berg",
        "-berg",  # mountain, rock
        "-haug",
        "-haugr",  # mound, hill
        "-setr",
        "-seter",  # mountain pasture
        "-þveit",
        "-tveit",  # clearing
        "-ruð",
        "-rud",  # clearing
        "-aker",
        "-akr",  # field
        "-eng",  # meadow
        "-holt",  # small forest
        "-lundr",
        "-lund",  # grove
        "-vǫllr",
        "-voll",  # field, plain
        "-á",
        "-å",  # river
        "-vatn",  # lake
        "-hǫfn",
        "-havn",  # harbor
        "-sund",  # strait
        "-hof",
        "-hov",  # temple
        "-vé",  # sacred enclosure
        "-hǫrgr",
        "-horg",  # altar, shrine
    ]

    # Common Old Norse toponymic prefixes/first elements
    prefixes = [
        "Þór-",
        "Tor-",  # Thor (deity)
        "Óðinn-",
        "Odin-",  # Odin (deity)
        "Freyr-",
        "Frøy-",  # Freyr (deity)
        "Freyja-",  # Freyja (deity)
        "Njǫrðr-",
        "Njord-",  # Njord (deity)
        "Ullr-",
        "Ull-",  # Ull (deity)
        "Týr-",  # Tyr (deity)
        "Baldr-",  # Baldr (deity)
        "Austr-",
        "Øst-",  # east
        "Vestr-",
        "Vest-",  # west
        "Norðr-",
        "Nord-",  # north
        "Suðr-",
        "Sør-",
        "Syd-",  # south
        "Nýr-",
        "Ny-",  # new
        "Gamall-",
        "Gaml-",  # old
        "Mikill-",
        "Stor-",  # great, large
        "Lítill-",
        "Lill-",  # small
        "Hvít-",
        "Kvit-",  # white
        "Svartr-",
        "Svart-",  # black
        "Rauðr-",
        "Raud-",  # red
        "Grœnn-",
        "Grøn-",  # green
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Norse toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try suffix matching (longest match first)
        sorted_suffixes = sorted(
            [s.lstrip("-") for s in self.suffixes],
            key=len,
            reverse=True,
        )

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
            # No recognized suffix—return whole form as stem
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
        """Classify whether a name form is likely Old Norse."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Check suffixes
        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.4
                break

        # Check prefixes
        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Check for Old Norse phonological features
        on_features = ["ð", "þ", "ǫ", "ø", "æ", "å"]
        for feat in on_features:
            if feat in form_lower:
                evidence.append(f"phonological feature '{feat}'")
                score += 0.1

        confidence = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="old-norse" if confidence > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old Norse components."""
        candidates: list[EtymologyCandidate] = []

        # Suffix meanings (partial, extensible)
        suffix_meanings = {
            "heim": ("heimr", "home, settlement", ["English -ham", "German -heim"]),
            "heimr": ("heimr", "home, settlement", ["English -ham", "German -heim"]),
            "by": ("býr", "farm, settlement", ["Danish -by", "English -by (Danelaw)"]),
            "bø": ("býr/bœr", "farm, settlement", ["Danish -by"]),
            "stad": ("staðr", "place, farm", ["German -stätte", "English -stead"]),
            "nes": ("nes", "headland, promontory", ["English -ness"]),
            "vik": ("vík", "bay, inlet", ["English -wick"]),
            "ey": ("ey", "island", ["English -ey/-ay"]),
            "øy": ("ey", "island", ["English -ey/-ay"]),
            "dal": ("dalr", "valley", ["English -dale", "German -tal"]),
            "berg": ("berg", "mountain, rock", ["German Berg", "English barrow"]),
            "hov": ("hof", "temple, cult building", []),
            "lund": ("lundr", "grove (sacred)", ["Swedish -lund"]),
            "rud": ("ruð", "clearing", ["English -rod/-royd"]),
            "tveit": ("þveit", "clearing, cut piece", []),
            "voll": ("vǫllr", "field, plain", ["English -wall/-wald"]),
        }

        for comp in components:
            key = comp.lemma.lower().lstrip("-") if comp.lemma else comp.component.lower()

            if key in suffix_meanings:
                lemma, meaning, cognates = suffix_meanings[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=cognates,
                    )
                )

        return candidates
