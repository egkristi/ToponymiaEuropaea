"""Irish/Scottish Gaelic (Goidelic) language module for toponymic analysis.

Gaelic toponymy covers both Irish (Gaeilge) and Scottish Gaelic (Gàidhlig).
Characterized by:
- Prefixed elements: baile, druim, ard, cill, dún, loch, inis, cluain
- Genitive-case specifics: mutation and lenition in compound names
- Anglicization layers: Gaelic → English spelling (Baile Átha Cliath → Dublin)
- Shared stock of elements across Ireland and Scotland

Key references:
- Flanagan & Flanagan 1994 "Irish Place Names"
- Watson 1926 "Celtic Place-Names of Scotland"
- Joyce 1869–1913 "Irish Names of Places" (3 vols)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class GaelicModule(BaseLanguageModule):
    """Language module for Irish/Scottish Gaelic (Goidelic) toponyms."""

    language_code = "ga"  # ISO 639-1 for Irish; also covers Scottish Gaelic (gd)
    language_name = "Irish/Scottish Gaelic"
    family = "Indo-European"
    branch = "Celtic > Insular Celtic > Goidelic"
    period = "600 CE–present"
    script = "Latn"

    # Common Gaelic toponymic prefixes (primary elements in Gaelic names)
    prefixes = [
        "Baile-",  # town, townland
        "Bally-",  # Anglicized form of baile
        "Druim-",  # ridge
        "Drum-",  # Anglicized form of druim
        "Ard-",  # height, promontory
        "Cill-",  # church (< Latin cella)
        "Kill-",  # Anglicized form of cill
        "Dún-",  # fort
        "Dun-",  # Anglicized form of dún
        "Loch-",  # lake
        "Lough-",  # Anglicized form of loch
        "Inis-",  # island
        "Inch-",  # Anglicized form of inis
        "Cluain-",  # meadow, pasture
        "Clon-",  # Anglicized form of cluain
        "Ráth-",  # ring fort
        "Rath-",  # Anglicized form
        "Lios-",  # ring fort, enclosure
        "Lis-",  # Anglicized form
        "Cnoc-",  # hill
        "Knock-",  # Anglicized form
        "Carraig-",  # rock
        "Carrick-",  # Anglicized form
        "Doire-",  # oak-wood
        "Derry-",  # Anglicized form
        "Achadh-",  # field
        "Agha-",  # Anglicized form
        "Gleann-",  # valley
        "Glen-",  # Anglicized form
        "Béal-",  # mouth (of river)
        "Bel-",  # Anglicized form
        "Srath-",  # broad valley
        "Strath-",  # Anglicized (Scottish)
        "Tulach-",  # mound, hillock
        "Tully-",  # Anglicized form
        "Cúil-",  # corner, nook
        "Cool-",  # Anglicized form
    ]

    # Common Gaelic toponymic suffixes (less common than prefixes in Gaelic)
    suffixes = [
        "-more",  # mór (great)
        "-beg",  # beag (small)
        "-duff",  # dubh (black)
        "-ban",  # bán (white)
        "-roe",  # rua (red)
        "-glass",  # glas (green/grey)
        "-agh",  # -ach (place of)
        "-an",  # diminutive
        "-ane",  # Anglicized diminutive
        "-ster",  # Norse suffix in Gaelic areas
        "-ey",  # Norse ey (island) in Gaelic areas
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Gaelic toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Gaelic is prefix-heavy: try prefix matching first
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
        """Classify whether a name form is likely Gaelic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Check prefixes (primary signal for Gaelic names)
        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Gaelic prefix {prefix}-")
                score += 0.5
                break

        # Check suffixes
        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Gaelic suffix -{suffix}")
                score += 0.3
                break

        # Gaelic orthographic features
        gaelic_features = ["bh", "mh", "dh", "gh", "th", "ch", "fh"]
        for feat in gaelic_features:
            if feat in form_lower:
                evidence.append(f"Gaelic lenition '{feat}'")
                score += 0.15
                break

        # Fada (long vowels) in original forms
        fada_chars = ["á", "é", "í", "ó", "ú", "à", "è", "ì", "ò", "ù"]
        for char in fada_chars:
            if char in form.lower():
                evidence.append(f"Gaelic fada/grave accent '{char}'")
                score += 0.1
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="gaelic" if confidence > 0.5 else None,
        )

    ELEMENT_MEANINGS: dict[str, tuple[str, str, list[str]]] = {
        # --- Settlement/habitation ---
        "baile": ("baile", "town, townland, homestead", ["Scots bally-"]),
        "bally": ("baile", "town, townland (Anglicized)", []),
        "ráth": ("ráth", "ring fort", ["English rath"]),
        "rath": ("ráth", "ring fort (Anglicized)", []),
        "lios": ("lios", "ring fort, enclosure", []),
        "lis": ("lios", "ring fort (Anglicized)", []),
        "dún": ("dún", "fort, fortified place", ["Welsh din", "Scots dun-"]),
        "dun": ("dún", "fort (Anglicized)", []),
        "caiseal": ("caiseal", "stone fort", ["< Latin castellum"]),
        "cashel": ("caiseal", "stone fort (Anglicized)", []),
        # --- Ecclesiastical ---
        "cill": ("cill", "church, churchyard", ["< Latin cella"]),
        "kill": ("cill", "church (Anglicized)", []),
        "teampall": ("teampall", "church", ["< Latin templum"]),
        "domhnach": ("domhnach", "church (Sunday)", ["< Latin dominicum"]),
        # --- Landscape ---
        "druim": ("druim", "ridge, hill-back", ["Scots drum-"]),
        "drum": ("druim", "ridge (Anglicized)", []),
        "ard": ("ard", "height, promontory", []),
        "cnoc": ("cnoc", "hill", ["Scots knock-"]),
        "knock": ("cnoc", "hill (Anglicized)", []),
        "tulach": ("tulach", "mound, hillock", []),
        "tully": ("tulach", "mound (Anglicized)", []),
        "gleann": ("gleann", "valley", ["Scots glen"]),
        "glen": ("gleann", "valley (Anglicized)", []),
        "srath": ("srath", "broad valley, river-plain", ["Scots strath"]),
        "strath": ("srath", "broad valley (Anglicized)", []),
        "cluain": ("cluain", "meadow, pasture", []),
        "clon": ("cluain", "meadow (Anglicized)", []),
        "achadh": ("achadh", "field", []),
        "agha": ("achadh", "field (Anglicized)", []),
        "carraig": ("carraig", "rock", []),
        "carrick": ("carraig", "rock (Anglicized)", []),
        "béal": ("béal", "mouth (of river)", []),
        "bel": ("béal", "river-mouth (Anglicized)", []),
        # --- Water features ---
        "loch": ("loch", "lake", ["Scots loch"]),
        "lough": ("loch", "lake (Anglicized)", []),
        "inis": ("inis", "island", ["Welsh ynys"]),
        "inch": ("inis", "island (Anglicized)", []),
        "abhainn": ("abhainn", "river", ["Welsh afon"]),
        "owen": ("abhainn", "river (Anglicized)", []),
        # --- Vegetation ---
        "doire": ("doire", "oak-wood", []),
        "derry": ("doire", "oak-wood (Anglicized)", []),
        "coill": ("coill", "wood, forest", []),
        # --- Descriptive adjectives ---
        "mór": ("mór", "great, large", ["Welsh mawr"]),
        "more": ("mór", "great (Anglicized)", []),
        "beag": ("beag", "small", ["Welsh bach"]),
        "beg": ("beag", "small (Anglicized)", []),
        "dubh": ("dubh", "black, dark", ["Welsh du"]),
        "duff": ("dubh", "black (Anglicized)", []),
        "bán": ("bán", "white", []),
        "ban": ("bán", "white (Anglicized)", []),
        "rua": ("rua", "red", []),
        "roe": ("rua", "red (Anglicized)", []),
        "glas": ("glas", "green, grey", ["Welsh glas"]),
        "glass": ("glas", "green (Anglicized)", []),
    }

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Gaelic components."""
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
