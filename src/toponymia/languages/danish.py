"""Danish (dansk) language module for toponymic analysis.

Danish toponymy is characterized by:
- Simplified morphology compared to Old Norse
- Distinctive suffixes: -by, -torp/-drup, -toft, -lev, -løse, -sted
- Historical layers: pre-Viking, Viking Age, medieval
- Influence from Low German in late medieval period
- Sound shifts: stød, vowel lowering, consonant lenition

Key references:
- Jørgensen 2008 "Danske stednavne"
- Hald 1965 "Vore Stednavne"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class DanishModule(BaseLanguageModule):
    """Language module for Danish (dansk) toponyms."""

    language_code = "da"  # ISO 639-1 for Danish
    language_name = "Danish"
    family = "Indo-European"
    branch = "Germanic > North Germanic > East Scandinavian"
    period = "1350 CE–present"
    script = "Latn"

    # Common Danish toponymic suffixes
    suffixes = [
        "-by",  # farm, settlement (< ON býr)
        "-torp",
        "-drup",
        "-trup",
        "-rup",  # outlying farm (< ON þorp)
        "-toft",
        "-tofte",  # homestead site (< ON topt)
        "-lev",
        "-løv",  # inheritance, estate (< ON leif)
        "-løse",
        "-løs",  # meadow/pasture (< *lausa)
        "-sted",
        "-sted",  # place (< ON staðr)
        "-inge",
        "-ung",  # group of people
        "-holt",  # small wood
        "-lund",  # grove
        "-skov",  # forest (< ON skógr)
        "-holm",  # islet
        "-næs",
        "-nes",  # headland
        "-vig",
        "-vik",  # bay
        "-borg",  # fortification
        "-bæk",  # stream (< ON bekkr)
        "-å",  # river (< ON á)
        "-sø",  # lake (< ON sær)
        "-bjerg",  # hill, mountain (< ON berg)
        "-dal",  # valley (< ON dalr)
        "-havn",  # harbor (< ON hǫfn)
        "-ager",  # field (< ON akr)
        "-mark",  # field, borderland
        "-gård",
        "-gaard",  # farm (< ON garðr)
        "-hus",  # house
        "-kirke",  # church
        "-rød",
        "-rud",  # clearing (< ON ruð)
        "-vad",  # ford
        "-bro",  # bridge
        "-sund",  # strait
        "-ø",  # island (< ON ey)
        "-høj",  # mound, hill (< ON haugr)
        "-led",
        "-lede",  # gate, passage
        "-ager",  # field
    ]

    # Common Danish toponymic prefixes/first elements
    prefixes = [
        "Stor-",  # great
        "Lille-",  # small
        "Ny-",  # new
        "Gammel-",  # old
        "Nørre-",  # north
        "Sønder-",  # south
        "Øster-",  # east
        "Vester-",  # west
        "Over-",  # upper
        "Neder-",  # lower
        "Hvid-",  # white
        "Sort-",  # black
        "Rød-",  # red
        "Grøn-",  # green
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Danish toponym into morphological components."""
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
            if form_lower.endswith(suffix.lower()) and len(form_lower) > len(suffix):
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
        """Classify whether a name form is likely Danish."""
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

        # Danish-specific phonological markers
        danish_features = ["æ", "ø", "å"]
        for feat in danish_features:
            if feat in form_lower:
                evidence.append(f"Danish orthographic feature '{feat}'")
                score += 0.1
                break

        # Danish-specific suffix patterns (lenited forms)
        lenited = ["-drup", "-trup", "-rup", "-løse", "-lev"]
        for pattern in lenited:
            p = pattern.lstrip("-")
            if form_lower.endswith(p):
                evidence.append(f"Danish lenited form -{p}")
                score += 0.2
                break

        confidence = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="danish" if confidence > 0.5 else None,
        )

    # Element meanings for Danish toponyms
    ELEMENT_MEANINGS: dict[str, tuple[str, str, list[str]]] = {
        # --- Settlement suffixes ---
        "by": ("býr", "farm, settlement", ["ON býr", "English -by (Danelaw)"]),
        "torp": ("þorp", "outlying farm", ["English -thorp", "German -dorf"]),
        "drup": ("þorp", "outlying farm (lenited)", ["< torp"]),
        "trup": ("þorp", "outlying farm (lenited)", ["< torp"]),
        "rup": ("þorp", "outlying farm (lenited)", ["< torp"]),
        "toft": ("topt", "homestead site", ["English -toft (Danelaw)"]),
        "tofte": ("topt", "homestead site", ["English -toft (Danelaw)"]),
        "lev": ("leif", "inheritance, estate", []),
        "løv": ("leif", "inheritance, estate", []),
        "løse": ("*lausa", "meadow, pasture", []),
        "sted": ("staðr", "place", ["English -stead", "German -stätte"]),
        "inge": ("*ingi", "people of, group", ["English -ing"]),
        "gård": ("garðr", "farm, enclosure", ["English -garth"]),
        "gaard": ("garðr", "farm, enclosure", ["English -garth"]),
        "hus": ("hús", "house", ["English house", "German Haus"]),
        # --- Landscape ---
        "holt": ("holt", "small wood, copse", ["English holt"]),
        "lund": ("lundr", "grove", ["Swedish -lund"]),
        "skov": ("skógr", "forest", ["English shaw"]),
        "holm": ("holmr", "islet, water-meadow", ["English holme"]),
        "næs": ("nes", "headland", ["English -ness"]),
        "borg": ("borg", "fortification, castle", ["English -bury/-borough"]),
        "bjerg": ("berg", "hill, mountain", ["German Berg"]),
        "dal": ("dalr", "valley", ["English -dale"]),
        "høj": ("haugr", "mound, hill", ["English howe"]),
        "mark": ("mǫrk", "field, borderland", ["English march"]),
        "ager": ("akr", "cultivated field", ["English acre"]),
        # --- Water features ---
        "bæk": ("bekkr", "stream", ["English beck (Northern)"]),
        "å": ("á", "river", ["German Ache"]),
        "sø": ("sær/sjór", "lake", ["English sea"]),
        "vig": ("vík", "bay", ["English -wick"]),
        "havn": ("hǫfn", "harbor", ["English haven"]),
        "sund": ("sund", "strait", ["English sound"]),
        "ø": ("ey", "island", ["English -ey"]),
        "vad": ("vað", "ford", ["English -wade"]),
        "bro": ("brú", "bridge", []),
        # --- Sacred/administrative ---
        "kirke": ("kirkja", "church", ["English church"]),
        "rød": ("ruð", "clearing", ["English -royd"]),
        "rud": ("ruð", "clearing", ["English -royd"]),
        # --- Directional modifiers ---
        "nørre": ("norðr", "north", ["English north"]),
        "sønder": ("suðr", "south", ["English south"]),
        "øster": ("austr", "east", ["English east"]),
        "vester": ("vestr", "west", ["English west"]),
        "stor": ("stórr", "great, large", []),
        "lille": ("lítill", "small", ["English little"]),
        "ny": ("nýr", "new", ["English new"]),
        "gammel": ("gamall", "old", []),
        "over": ("yfir", "upper", ["English over"]),
        "neder": ("neðri", "lower", ["English nether"]),
    }

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Danish components."""
        candidates: list[EtymologyCandidate] = []

        for comp in components:
            key = comp.lemma.lower().lstrip("-") if comp.lemma else comp.component.lower()

            if key in self.ELEMENT_MEANINGS:
                lemma, meaning, cognates = self.ELEMENT_MEANINGS[key]
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

    def get_etymology(self, element: str) -> EtymologyCandidate | None:
        """Look up the etymology of a Danish toponymic element."""
        key = element.lower().lstrip("-")
        if key in self.ELEMENT_MEANINGS:
            lemma, meaning, cognates = self.ELEMENT_MEANINGS[key]
            return EtymologyCandidate(
                lemma=lemma,
                meaning=meaning,
                language_code=self.language_code,
                confidence=0.8,
                cognates=cognates,
            )
        return None
