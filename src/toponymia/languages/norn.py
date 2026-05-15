"""Norn language module for toponymic analysis.

Norn was the North Germanic language of Orkney, Shetland, and Caithness,
descended from Old Norse but developing independently from ~800 to ~1700 CE:
- Orkney/Shetland were Norwegian territory until 1468–1472 (pawned to Scotland)
- Norn persisted as a spoken language until mid-18th century
- Left massive toponymic substrate: most place-names in Orkney/Shetland are Norn
- Shows unique phonetic developments from ON (e.g., ON á > Norn o/å)
- Critical for understanding Norse expansion in the North Atlantic
- Intermediate between Faroese and mainland Scandinavian developments

Diagnostic Norn forms vs. standard ON:
- ON ey > Norn -ay/-a (Shapinsay, Sanday, Rousay)
- ON vágr > Norn -waa/-wa (Kirkwall < Kirkjuvágr)
- ON setr > Norn -setter/-ster (Grimbister < Grímr + bólstaðr)
- ON bólstaðr > Norn -bister/-buster/-ster (Scrabster, Lybster)
- ON staðir > Norn -sta/-ston (Grimeston)

Key references:
- Jakobsen 1897 "The Dialect and Place Names of Shetland"
- Marwick 1952 "Orkney Farm-Names"
- Stewart 1987 "Shetland Place-Names"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class NornModule(BaseLanguageModule):
    """Language module for Norn (Orkney/Shetland Norse) toponyms."""

    language_code = "nrn"  # ISO 639-3 for Norn
    language_name = "Norn"
    family = "Indo-European"
    branch = "Germanic > North Germanic > West Scandinavian > Insular"
    period = "800–1750 CE"
    script = "Latn"

    prefixes = [
        "Kirk-",  # church (< ON kirkja; Kirkwall)
        "Brek-",  # slope (< ON brekka)
        "Burg-",  # fort (< ON borg)
        "Gar-",  # enclosure (< ON garðr)
        "Grim-",  # personal name/mask (< ON Grímr)
        "Helli-",  # flat stone (< ON hella)
        "Ling-",  # heather (< ON lyng)
        "Muck-",  # dung (< ON myki → good land)
        "Sand-",  # sand (< ON sandr)
        "Skeld-",  # slope (< ON skjald)
        "Skel-",  # shell (< ON skel)
        "Strom-",  # current (< ON straumr)
        "Voe-",  # bay (< ON vágr)
    ]

    suffixes = [
        # bólstaðr derivatives (THE diagnostic Norn suffix)
        "-bister",  # farmstead (< ON bólstaðr; Grimbister, Kirbister)
        "-buster",  # variant (Lybster, Scrabster)
        "-ster",  # reduced form (Scrabster, Lybster, Thurster)
        "-setter",  # shieling (< ON setr; Murkle Setter)
        # vágr derivatives
        "-wall",  # bay (< ON vágr; Kirkwall < Kirkjuvágr)
        "-waa",  # bay variant
        "-voe",  # inlet (< ON vágr; Hamnavoe)
        # ey derivatives
        "-ay",  # island (< ON ey; Sanday, Westray, Shapinsay)
        "-a",  # reduced (Rousay < Hrólfsey)
        # staðir derivatives
        "-ston",  # place (< ON staðir; Grimeston)
        "-sta",  # reduced (Hammarsta)
        # Other
        "-quoy",  # enclosure (< ON kví; Stenigar Quoy)
        "-garth",  # yard (< ON garðr; Applegarth)
        "-geo",  # narrow inlet (< ON gjá; Geo of Sclaites)
        "-wick",  # bay (< ON vík; Lerwick, Wick)
        "-ness",  # headland (< ON nes; Skaw Ness)
        "-dale",  # valley (< ON dalr; Rackwick Dale)
        "-firth",  # fjord (< ON fjörðr; Pentland Firth)
        "-ham",  # harbour? (< ON hamn; Hamnavoe)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "kirk": "church (< ON kirkja)",
        "brek": "slope, hillside (< ON brekka)",
        "burg": "fort, broch (< ON borg)",
        "gar": "enclosure, farm (< ON garðr)",
        "sand": "sand, sandy ground",
        "strom": "current, tidal stream (< ON straumr)",
        "voe": "bay, inlet (< ON vágr)",
        "bister": "farmstead (< ON bólstaðr)",
        "buster": "farmstead (variant of bólstaðr)",
        "ster": "farmstead (reduced bólstaðr)",
        "setter": "shieling, summer pasture (< ON setr/sætr)",
        "wall": "bay (< ON vágr → Kirkwall)",
        "ay": "island (< ON ey)",
        "ston": "place, farmstead (< ON staðir)",
        "quoy": "enclosure, pen (< ON kví)",
        "garth": "yard, enclosed ground (< ON garðr)",
        "geo": "narrow rocky inlet (< ON gjá)",
        "wick": "bay, inlet (< ON vík)",
        "ness": "headland, promontory (< ON nes)",
        "dale": "valley (< ON dalr)",
        "firth": "fjord, sea inlet (< ON fjörðr)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Norn toponym into components."""
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
                    confidence=0.9,
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
                    confidence=0.9,
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
        """Classify whether a toponym is likely Norn."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # bólstaðr derivatives are THE diagnostic Norn marker
        bolstadr = ["bister", "buster", "bster", "bist"]
        for marker in bolstadr:
            if marker in form_lower:
                evidence.append(f"Norn bólstaðr reflex '{marker}'")
                score += 0.5
                break

        # Other highly diagnostic Norn suffixes
        norn_suffixes = ["quoy", "setter", "voe", "geo"]
        for marker in norn_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Norn suffix -{marker}")
                score += 0.35
                break

        # Norse island suffixes in Norn form
        if form_lower.endswith("ay") and len(form_lower) > 3:
            evidence.append("Norn island suffix -ay (< ON ey)")
            score += 0.25

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="800–1750 CE (Norn)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Norn components."""
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
