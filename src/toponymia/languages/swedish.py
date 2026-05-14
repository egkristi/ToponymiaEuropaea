"""Swedish (svenska) language module for toponymic analysis.

Swedish toponymy is characterized by:
- East Scandinavian development from Old Norse
- Distinctive suffixes: -torp, -rud, -ås, -inge, -sta/-tuna
- Historical layers: pre-Viking (e.g. -inge, -sta), Viking, medieval
- Regional variation (Götaland vs Svealand vs Norrland)
- Influence from Finnish in the north and east

Key references:
- Wahlberg 2003 "Svenskt ortnamnslexikon"
- Hellquist 1903-06 "Studier öfver de svenska sjönamnen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SwedishModule(BaseLanguageModule):
    """Language module for Swedish (svenska) toponyms."""

    language_code = "sv"  # ISO 639-1 for Swedish
    language_name = "Swedish"
    family = "Indo-European"
    branch = "Germanic > North Germanic > East Scandinavian"
    period = "1350 CE–present"
    script = "Latn"

    # Common Swedish toponymic suffixes
    suffixes = [
        "-by",  # village (< ON býr)
        "-torp",  # outlying farm (< ON þorp)
        "-rud",
        "-ryd",  # clearing (< ON ruð)
        "-ås",  # ridge (< ON áss)
        "-inge",
        "-unge",  # group of people / meadow
        "-sta",
        "-stuga",  # place (< ON staðr)
        "-tuna",  # enclosed farmstead
        "-bo",  # dwelling (< ON bú)
        "-lund",  # grove (< ON lundr)
        "-skog",  # forest (< ON skógr)
        "-berg",  # mountain (< ON berg)
        "-holm",  # islet
        "-ö",  # island (< ON ey)
        "-näs",  # headland (< ON nes)
        "-vik",  # bay (< ON vík)
        "-fjärd",  # fjord, bay
        "-dal",  # valley (< ON dalr)
        "-sjö",  # lake (< ON sjór)
        "-å",  # river (< ON á)
        "-bäck",  # stream (< ON bekkr)
        "-fors",  # waterfall/rapids
        "-hamn",  # harbor (< ON hǫfn)
        "-sund",  # strait
        "-gård",  # farm (< ON garðr)
        "-hus",  # house
        "-kyrka",  # church
        "-köping",  # market town
        "-aker",
        "-åker",  # field (< ON akr)
        "-äng",  # meadow
        "-mark",  # field, border
        "-höjd",  # height
        "-hög",  # mound (< ON haugr)
        "-bro",  # bridge
        "-vad",  # ford
        "-löv",  # inheritance (< ON leif)
        "-hem",  # home (< ON heimr)
        "-land",  # land
        "-borg",  # fortification
        "-sand",  # sandy ground
        "-mo",  # heath
    ]

    # Common Swedish toponymic prefixes/first elements
    prefixes = [
        "Stor-",  # great
        "Lill-",  # small
        "Ny-",  # new
        "Gammal-",  # old
        "Norr-",  # north
        "Söder-",  # south
        "Öster-",  # east
        "Väster-",  # west
        "Över-",  # upper
        "Nedre-",  # lower
        "Vit-",  # white
        "Svart-",  # black
        "Röd-",  # red
        "Grön-",  # green
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Swedish toponym into morphological components."""
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
        """Classify whether a name form is likely Swedish."""
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

        # Swedish-specific orthographic features
        swedish_features = ["ä", "ö", "å"]
        for feat in swedish_features:
            if feat in form_lower:
                evidence.append(f"Swedish orthographic feature '{feat}'")
                score += 0.1
                break

        # Swedish-specific suffix patterns
        swedish_specific = ["-köping", "-tuna", "-sta", "-fjärd", "-sjö"]
        for pattern in swedish_specific:
            p = pattern.lstrip("-")
            if form_lower.endswith(p):
                evidence.append(f"distinctly Swedish suffix -{p}")
                score += 0.2
                break

        confidence = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="swedish" if confidence > 0.5 else None,
        )

    # Element meanings for Swedish toponyms
    ELEMENT_MEANINGS: dict[str, tuple[str, str, list[str]]] = {
        # --- Settlement suffixes ---
        "by": ("býr", "village, settlement", ["ON býr", "Danish -by"]),
        "torp": ("þorp", "outlying farm", ["Danish -trup/-drup", "English -thorp"]),
        "rud": ("ruð", "clearing", ["Norwegian -rud", "English -royd"]),
        "ryd": ("ruð", "clearing", ["Norwegian -rud"]),
        "sta": ("staðr", "place, farm", ["< ON staðir"]),
        "tuna": ("tún", "enclosed farmstead", []),
        "bo": ("bú", "dwelling, estate", ["English -by?"]),
        "gård": ("garðr", "farm, enclosure", ["English -garth"]),
        "hus": ("hús", "house", ["English house"]),
        "hem": ("heimr", "home, settlement", ["English -ham", "German -heim"]),
        "köping": ("kaupangr", "market town", ["English -chipping"]),
        # --- Landscape ---
        "lund": ("lundr", "grove", ["Danish -lund"]),
        "skog": ("skógr", "forest", []),
        "berg": ("berg", "mountain, rock", ["German Berg"]),
        "holm": ("holmr", "islet", ["English holme"]),
        "näs": ("nes", "headland, promontory", ["English -ness"]),
        "dal": ("dalr", "valley", ["English -dale"]),
        "ås": ("áss", "ridge", []),
        "inge": ("*ingi", "meadow/people of", ["Danish -inge"]),
        "höjd": ("hæð", "height, hill", ["English heath?"]),
        "hög": ("haugr", "mound, hill", ["English howe"]),
        "mark": ("mǫrk", "field, borderland", ["English march"]),
        "äng": ("eng", "meadow", []),
        "aker": ("akr", "cultivated field", ["English acre"]),
        "åker": ("akr", "cultivated field", ["English acre"]),
        "mo": ("mór", "heath, sandy ground", ["English moor"]),
        "sand": ("sandr", "sandy plain", ["English sand"]),
        "land": ("land", "land, estate", ["English land"]),
        "borg": ("borg", "fortification", ["English -bury/-borough"]),
        # --- Water features ---
        "ö": ("ey", "island", ["English -ey"]),
        "vik": ("vík", "bay", ["English -wick"]),
        "fjärd": ("fjǫrðr", "fjord, bay", ["English firth"]),
        "sjö": ("sjór", "lake", ["English sea"]),
        "å": ("á", "river", ["German Ache"]),
        "bäck": ("bekkr", "stream", ["English beck"]),
        "fors": ("fors", "waterfall, rapids", ["Norwegian foss"]),
        "hamn": ("hǫfn", "harbor", ["English haven"]),
        "sund": ("sund", "strait", ["English sound"]),
        "vad": ("vað", "ford", ["English -wade"]),
        "bro": ("brú", "bridge", []),
        # --- Directional modifiers ---
        "norr": ("norðr", "north", ["English north"]),
        "söder": ("suðr", "south", ["English south"]),
        "öster": ("austr", "east", ["English east"]),
        "väster": ("vestr", "west", ["English west"]),
        "stor": ("stórr", "great, large", []),
        "lill": ("lítill", "small", ["English little"]),
        "ny": ("nýr", "new", ["English new"]),
        "gammal": ("gamall", "old", []),
        "över": ("yfir", "upper", ["English over"]),
        "nedre": ("neðri", "lower", ["English nether"]),
        # --- Colour modifiers ---
        "vit": ("hvítr", "white", ["English white"]),
        "svart": ("svartr", "black", ["English swart"]),
        "röd": ("rauðr", "red", ["English red"]),
        "grön": ("grœnn", "green", ["English green"]),
    }

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Swedish components."""
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
        """Look up the etymology of a Swedish toponymic element."""
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
