"""Welsh (Cymraeg) language module for toponymic analysis.

Welsh toponymy represents the P-Celtic (Brythonic) tradition:
- Prefixed generic elements: llan-, aber-, pen-, cwm-, tre-
- Soft mutation in compounds: pont → bont, coed → goed
- Definite article: y/yr/'r absorbed into names
- Continuous use since Roman withdrawal (~400 CE)
- Rich stratigraphy: pre-Celtic, Brythonic, Latin loans, English adaptations

Key references:
- Owen & Morgan 2007 "Dictionary of the Place-Names of Wales"
- Charles 1938 "Non-Celtic Place-Names in Wales"
- Thomas 1938 "Some Welsh River Names"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class WelshModule(BaseLanguageModule):
    """Language module for Welsh (Cymraeg) toponyms."""

    language_code = "cy"  # ISO 639-1 for Welsh
    language_name = "Welsh"
    family = "Indo-European"
    branch = "Celtic > Insular Celtic > Brythonic"
    period = "600 CE–present"
    script = "Latn"

    # Common Welsh toponymic prefixes (primary elements)
    prefixes = [
        "Llan-",  # church enclosure
        "Aber-",  # river-mouth, confluence
        "Pen-",  # head, top, end
        "Cwm-",  # valley (combe)
        "Tre-",  # town, homestead (< tref)
        "Tref-",  # town, homestead
        "Caer-",  # fort (< Latin castra)
        "Pont-",  # bridge (< Latin pontem)
        "Bont-",  # bridge (mutated)
        "Coed-",  # wood, forest
        "Bryn-",  # hill
        "Craig-",  # rock, crag
        "Nant-",  # stream, valley
        "Llyn-",  # lake
        "Rhyd-",  # ford
        "Maes-",  # field
        "Dinas-",  # hill-fort, city
        "Dol-",  # meadow
        "Glan-",  # river-bank
        "Betws-",  # chapel (< English bead-house)
        "Bedd-",  # grave
        "Eglwys-",  # church (< Latin ecclesia)
        "Ffynnon-",  # well, spring
        "Ynys-",  # island
        "Mynydd-",  # mountain
        "Hafod-",  # summer dwelling
        "Hendre-",  # winter dwelling, old settlement
        "Garth-",  # enclosure, hill
        "Castell-",  # castle (< Latin castellum)
        "Pant-",  # hollow, valley
        "Cefn-",  # ridge
        "Blaen-",  # head of valley, source
    ]

    # Welsh toponymic suffixes (less common than prefixes)
    suffixes = [
        "-wen",  # gwyn/gwen (white, blessed)
        "-gwyn",  # white, blessed
        "-ddu",  # du (black)
        "-fach",  # bach (small, mutated)
        "-bach",  # small
        "-fawr",  # mawr (great, mutated)
        "-mawr",  # great
        "-newydd",  # new
        "-hen",  # old
        "-uchaf",  # upper
        "-isaf",  # lower
        "-coch",  # red
        "-glas",  # green, blue
        "-llwyd",  # grey
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Welsh toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Welsh is prefix-dominant
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

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="compound_modifier",
                    confidence=0.5,
                )
            )
        else:
            # Try suffix matching
            sorted_suffixes = sorted(
                [s.lstrip("-").lower() for s in self.suffixes],
                key=len,
                reverse=True,
            )
            matched_suffix = None
            for suffix in sorted_suffixes:
                if form_lower.endswith(suffix) and len(form_lower) > len(suffix):
                    matched_suffix = suffix
                    break

            if matched_suffix:
                stem = form[: len(form) - len(matched_suffix)]
                suffix_part = form[len(form) - len(matched_suffix) :]
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="stem",
                        confidence=0.5,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=suffix_part,
                        position=1,
                        morph_type="suffix",
                        lemma=matched_suffix,
                        confidence=0.6,
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
        """Classify whether a name form is likely Welsh."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Check prefixes (strongest signal)
        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Welsh prefix {prefix}-")
                score += 0.5
                break

        # Check suffixes
        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Welsh suffix -{suffix}")
                score += 0.3
                break

        # Welsh orthographic features (distinctive)
        welsh_digraphs = ["ll", "dd", "ff", "rh", "ng", "ch"]
        for digraph in welsh_digraphs:
            if digraph in form_lower:
                evidence.append(f"Welsh digraph '{digraph}'")
                score += 0.2
                break

        # Welsh-specific characters: 'w' as vowel (medial position)
        if "w" in form_lower and not form_lower.startswith("w") and form_lower.count("w") > 0:
            evidence.append("Welsh 'w' as vowel")
            score += 0.1

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="welsh" if confidence > 0.5 else None,
        )

    ELEMENT_MEANINGS: dict[str, tuple[str, str, list[str]]] = {
        # --- Ecclesiastical ---
        "llan": ("llan", "church enclosure, parish", ["Breton lan-", "Cornish lan-"]),
        "eglwys": ("eglwys", "church", ["< Latin ecclesia"]),
        "betws": ("betws", "chapel, oratory", ["< English bead-house"]),
        "bedd": ("bedd", "grave", ["Irish bed"]),
        # --- Settlement ---
        "tre": ("tref", "town, homestead", ["Breton tre-", "Cornish tre-"]),
        "tref": ("tref", "town, homestead", ["Breton tre-", "Cornish tre-"]),
        "caer": ("caer", "fort, fortified town", ["< Latin castra"]),
        "dinas": ("dinas", "hill-fort, city", ["< Latin *dunum?"]),
        "castell": ("castell", "castle", ["< Latin castellum"]),
        "hendre": ("hendre", "winter dwelling, old settlement", []),
        "hafod": ("hafod", "summer dwelling", []),
        # --- Water ---
        "aber": ("aber", "river-mouth, confluence", ["Breton aber-"]),
        "llyn": ("llyn", "lake", ["Irish linn"]),
        "nant": ("nant", "stream, valley", ["Breton nant"]),
        "rhyd": ("rhyd", "ford", ["Irish rit"]),
        "ffynnon": ("ffynnon", "well, spring", ["< Latin fontana"]),
        "pont": ("pont", "bridge", ["< Latin pontem"]),
        "bont": ("pont", "bridge (mutated)", []),
        "glan": ("glan", "river-bank, shore", []),
        "ynys": ("ynys", "island", ["Irish inis"]),
        # --- Landscape ---
        "pen": ("pen", "head, top, end", ["Breton pen-", "Cornish pen-"]),
        "cwm": ("cwm", "valley, coombe", ["English coombe"]),
        "bryn": ("bryn", "hill", []),
        "craig": ("craig", "rock, crag", ["English crag"]),
        "mynydd": ("mynydd", "mountain", ["Breton menez"]),
        "coed": ("coed", "wood, forest", []),
        "maes": ("maes", "field, plain", []),
        "dol": ("dol", "meadow, water-meadow", []),
        "garth": ("garth", "enclosure, ridge", ["English garth"]),
        "pant": ("pant", "hollow, valley", []),
        "cefn": ("cefn", "ridge, back", []),
        "blaen": ("blaen", "head of valley, source", []),
        # --- Descriptive ---
        "gwyn": ("gwyn", "white, fair, blessed", ["Irish finn"]),
        "gwen": ("gwen", "white, fair (feminine)", []),
        "du": ("du", "black, dark", ["Irish dubh"]),
        "ddu": ("du", "black (mutated)", []),
        "bach": ("bach", "small, little", ["Irish beag"]),
        "fach": ("bach", "small (mutated)", []),
        "mawr": ("mawr", "great, large", ["Irish mór"]),
        "fawr": ("mawr", "great (mutated)", []),
        "hen": ("hen", "old", ["Irish sean"]),
        "newydd": ("newydd", "new", ["Irish nua"]),
        "coch": ("coch", "red", []),
        "glas": ("glas", "green, blue, grey", ["Irish glas"]),
        "llwyd": ("llwyd", "grey, brown", ["Irish liath"]),
    }

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Welsh components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in self.ELEMENT_MEANINGS:
                proto_form, meaning, cognates = self.ELEMENT_MEANINGS[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=proto_form,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=cognates,
                    )
                )
        return candidates
