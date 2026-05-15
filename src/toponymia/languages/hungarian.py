"""Hungarian (Magyar) language module for toponymic analysis.

Hungarian is a Finno-Ugric language with a unique toponymic system:
- Magyars migrated from Ural region to Carpathian Basin in 896 CE
- Created distinctive Uralic-origin place-name patterns in Central Europe
- Viking-Hungarian contact: Both raided Europe 9th-10th century
- Norse sources mention "Ungararíki" (Hungarian Kingdom)
- Hungarian toponyms often fossilize pre-Slavic and Turkic substrate
- Important for understanding population movements in Danube Basin

Key references:
- Kiss 1988 "Földrajzi nevek etimológiai szótára"
- Kristó 2000 "Magyarország településeinek nevei az Árpád-korban"
- Rácz 2016 "Régi magyar településnévtípusok"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class HungarianModule(BaseLanguageModule):
    """Language module for Hungarian toponyms."""

    language_code = "hun"  # ISO 639-3 for Hungarian
    language_name = "Hungarian"
    family = "Uralic"
    branch = "Finno-Ugric > Ugric"
    period = "896 CE – present (in Carpathian Basin)"
    script = "Latn"

    prefixes = [
        "Nagy-",  # great (Nagykanizsa, Nagyszeben)
        "Kis-",  # small (Kiskőrös, Kiskunság)
        "Felső-",  # upper (Felsőörs)
        "Alsó-",  # lower (Alsóörs)
        "Új-",  # new (Újpest, Újvidék)
        "Ó-",  # old (Óbuda)
        "Fehér-",  # white (Fehérvár, Székesfehérvár)
        "Fekete-",  # black (Feketehalom)
        "Szép-",  # beautiful
        "Szent-",  # saint (Szentendre, Szentgotthárd; < Latin sanctus)
        "Puszta-",  # plain, deserted (puszta)
        "Magyar-",  # Hungarian (ethnic qualifier)
    ]

    suffixes = [
        "-vár",  # castle, fortification (Temesvár, Kolozsvár)
        "-város",  # city (Hódmezővásárhely)
        "-falu",  # village (Munkácsfalva, -falva)
        "-falva",  # village (possessive)
        "-hegy",  # mountain, hill (Gellérthegy)
        "-halom",  # mound, tumulus (Kunhalom)
        "-völgy",  # valley (Bánhidavölgy)
        "-mező",  # field, meadow (Hódmezővásárhely)
        "-patak",  # stream (Sárospatak)
        "-tó",  # lake (Balatontó)
        "-szék",  # seat, administrative center (Székesfehérvár)
        "-háza",  # house (Nyíregyháza, -háza possessive)
        "-puszta",  # deserted place, plain
        "-sziget",  # island (Csepelsziget, Margitsziget)
        "-telek",  # plot, estate (Újtelek)
        "-kő",  # stone, rock (Miskakő)
        "-erdő",  # forest (Bánffyerdő)
        "-pata",  # stream (archaic, cf. -patak)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "nagy": "great, large",
        "kis": "small, little",
        "felső": "upper",
        "alsó": "lower",
        "új": "new",
        "ó": "old",
        "fehér": "white",
        "fekete": "black",
        "szép": "beautiful",
        "szent": "saint, holy (< Lat. sanctus)",
        "puszta": "deserted, plain (steppe)",
        "magyar": "Hungarian (Magyar)",
        "vár": "castle, fortification",
        "város": "city",
        "falu": "village",
        "falva": "village (possessive)",
        "hegy": "mountain, hill",
        "halom": "mound, tumulus",
        "völgy": "valley",
        "mező": "field, meadow",
        "patak": "stream, brook",
        "tó": "lake",
        "szék": "seat, administrative center",
        "háza": "house (possessive)",
        "sziget": "island",
        "telek": "plot, estate",
        "kő": "stone, rock",
        "erdő": "forest",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Hungarian toponym into components."""
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

        if matched_prefix and matched_suffix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.85,
                )
            )
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="stem",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.85,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_modifier",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.85,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.5,
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
        """Classify whether a toponym is likely Hungarian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        hun_suffixes = [
            "vár",
            "város",
            "falu",
            "falva",
            "hegy",
            "halom",
            "völgy",
            "mező",
            "patak",
            "háza",
            "sziget",
            "erdő",
        ]
        for marker in hun_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Hungarian suffix -{marker}")
                score += 0.4
                break

        hun_prefixes = ["nagy", "kis", "felső", "alsó", "szent", "fehér", "fekete"]
        for marker in hun_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Hungarian prefix {marker}-")
                score += 0.3
                break

        # Hungarian-specific characters
        hun_chars = ["ő", "ű", "á", "é", "gy", "sz", "cs", "zs"]
        for ch in hun_chars:
            if ch in form_lower:
                evidence.append(f"Hungarian orthography '{ch}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="896 CE – present (Magyar)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Hungarian components."""
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
