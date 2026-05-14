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
        "-vin",  # meadow (very old, possibly pre-Norse)
        "-nes",  # headland, promontory
        "-ey",
        "-øy",  # island
        "-vík",
        "-vik",  # bay, inlet
        "-fjǫrðr",
        "-fjord",  # fjord
        "-dalr",
        "-dal",  # valley
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
        "-ló",
        "-lo",  # meadow by water
        "-óss",
        "-ós",
        "-os",  # river mouth
        "-angr",
        "-anger",  # fjord, inlet (archaic)
        "-foss",  # waterfall
        "-sand",
        "-sandr",  # sandy plain
        "-mo",  # heath
        "-borg",  # fortification
        "-fest",  # firm ground
        "-ø",  # island (modern form of ey)
        "-stein",
        "-steinn",  # stone
        "-garðr",
        "-gard",  # farm, enclosure
        "-tun",  # farmyard
        "-fjell",
        "-fjall",  # mountain
        "-skog",  # forest
        "-eid",  # isthmus
        "-ås",  # ridge
        "-bru",  # bridge
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

    # Comprehensive element meanings dictionary
    # Maps normalized forms to (lemma, meaning, cognates)
    ELEMENT_MEANINGS: dict[str, tuple[str, str, list[str]]] = {
        # --- Settlement/habitation suffixes ---
        "heim": ("heimr", "home, settlement", ["English -ham", "German -heim"]),
        "heimr": ("heimr", "home, settlement", ["English -ham", "German -heim"]),
        "by": ("býr", "farm, settlement", ["Danish -by", "English -by (Danelaw)"]),
        "bø": ("býr/bœr", "farm, settlement", ["Danish -by"]),
        "stad": ("staðr", "place, farm", ["German -stätte", "English -stead"]),
        "staðir": ("staðr", "place, farm", ["German -stätte", "English -stead"]),
        "setr": ("setr", "mountain pasture, shieling", ["English -sett"]),
        "seter": ("setr", "mountain pasture, shieling", ["English -sett"]),
        "land": ("land", "land, estate", ["English land", "German Land"]),
        "garðr": ("garðr", "farm, enclosure", ["English -garth", "Russian gorod"]),
        "gard": ("garðr", "farm, enclosure", ["English -garth", "Russian gorod"]),
        "tun": ("tún", "farmyard, enclosure", ["English town", "German Zaun"]),
        "rud": ("ruð", "clearing", ["English -rod/-royd"]),
        "ruð": ("ruð", "clearing", ["English -rod/-royd"]),
        "tveit": ("þveit", "clearing, cut piece", []),
        "þveit": ("þveit", "clearing, cut piece", []),
        "aker": ("akr", "cultivated field", ["English acre", "Latin ager"]),
        "akr": ("akr", "cultivated field", ["English acre", "Latin ager"]),
        "eng": ("eng", "meadow", ["English ing (meadow)"]),
        # --- Meadow/field elements ---
        "vin": ("vin", "meadow, pasture (archaic)", ["Gothic winja", "Latin vīnea?"]),
        "vǫllr": ("vǫllr", "field, plain", ["English -wall/-wald"]),
        "voll": ("vǫllr", "field, plain", ["English -wall/-wald"]),
        # --- Water/coast features ---
        "nes": ("nes", "headland, promontory", ["English -ness"]),
        "vik": ("vík", "bay, inlet", ["English -wick"]),
        "vík": ("vík", "bay, inlet", ["English -wick"]),
        "ey": ("ey", "island", ["English -ey/-ay"]),
        "øy": ("ey", "island", ["English -ey/-ay"]),
        "ø": ("ey", "island", ["English -ey/-ay"]),
        "fjord": ("fjǫrðr", "fjord, inlet", ["English firth"]),
        "fjǫrðr": ("fjǫrðr", "fjord, inlet", ["English firth"]),
        "sund": ("sund", "strait, sound", ["English sound"]),
        "vatn": ("vatn", "lake, water", ["English water", "German Wasser"]),
        "å": ("á", "river", ["German Ache", "Latin aqua"]),
        "á": ("á", "river", ["German Ache", "Latin aqua"]),
        "ós": ("óss", "river mouth, estuary", ["English ouse"]),
        "os": ("óss", "river mouth, estuary", ["English ouse"]),
        "óss": ("óss", "river mouth, estuary", ["English ouse"]),
        "foss": ("fors", "waterfall", ["Swedish fors"]),
        "hǫfn": ("hǫfn", "harbor", ["English haven", "German Hafen"]),
        "havn": ("hǫfn", "harbor", ["English haven", "German Hafen"]),
        "ló": ("ló", "meadow by water, flood-plain", []),
        "lo": ("ló", "meadow by water, flood-plain", []),
        # --- Terrain/landscape ---
        "berg": ("berg", "mountain, rock", ["German Berg", "English barrow"]),
        "bjǫrg": ("bjǫrg", "mountain, cliff, rock", ["German Berg"]),
        "haug": ("haugr", "mound, hill", ["English howe"]),
        "haugr": ("haugr", "mound, hill", ["English howe"]),
        "holt": ("holt", "small forest, copse", ["English holt"]),
        "lundr": ("lundr", "grove (often sacred)", ["Swedish -lund"]),
        "lund": ("lundr", "grove (often sacred)", ["Swedish -lund"]),
        "dal": ("dalr", "valley", ["English -dale", "German -tal"]),
        "dalr": ("dalr", "valley", ["English -dale", "German -tal"]),
        "ás": ("áss", "ridge, hill", ["English esker?"]),
        "ås": ("áss", "ridge, hill", ["English esker?"]),
        "fjall": ("fjall", "mountain", ["German Fels"]),
        "fjell": ("fjall", "mountain", ["German Fels"]),
        "stein": ("steinn", "stone, rock", ["English stone", "German Stein"]),
        "steinn": ("steinn", "stone, rock", ["English stone", "German Stein"]),
        "sand": ("sandr", "sand, sandy plain", ["English sand"]),
        "sandr": ("sandr", "sand, sandy plain", ["English sand"]),
        "mo": ("mór", "heath, moor", ["English moor"]),
        "mór": ("mór", "heath, moor", ["English moor"]),
        "skog": ("skógr", "forest", ["English shaw?"]),
        "skógr": ("skógr", "forest", ["English shaw?"]),
        "eid": ("eið", "isthmus, portage", []),
        "eið": ("eið", "isthmus, portage", []),
        "angr": ("angr", "fjord, inlet (archaic)", ["English anger?"]),
        "anger": ("angr", "fjord, inlet (archaic)", ["English anger?"]),
        # --- Sacred/cult ---
        "hov": ("hof", "temple, cult building", []),
        "hof": ("hof", "temple, cult building", []),
        "vé": ("vé", "sacred enclosure, sanctuary", ["German Weihe"]),
        "hǫrgr": ("hǫrgr", "altar, stone shrine", []),
        "horg": ("hǫrgr", "altar, stone shrine", []),
        # --- Modifiers: directions ---
        "austr": ("austr", "east", ["English east"]),
        "øst": ("austr", "east", ["English east"]),
        "vestr": ("vestr", "west", ["English west"]),
        "vest": ("vestr", "west", ["English west"]),
        "norðr": ("norðr", "north", ["English north"]),
        "nord": ("norðr", "north", ["English north"]),
        "suðr": ("suðr", "south", ["English south"]),
        "sør": ("suðr", "south", ["English south"]),
        "syd": ("suðr", "south", ["English south"]),
        # --- Modifiers: size/age ---
        "nýr": ("nýr", "new", ["English new", "German neu"]),
        "ny": ("nýr", "new", ["English new", "German neu"]),
        "gamall": ("gamall", "old", ["German Gemahl"]),
        "gaml": ("gamall", "old", ["German Gemahl"]),
        "mikill": ("mikill", "great, large", ["English much"]),
        "stor": ("stórr", "great, large", ["English stour (archaic)"]),
        "lítill": ("lítill", "small, little", ["English little"]),
        "lill": ("lítill", "small, little", ["English little"]),
        # --- Modifiers: colours ---
        "hvít": ("hvítr", "white", ["English white"]),
        "kvit": ("hvítr", "white", ["English white"]),
        "svartr": ("svartr", "black", ["English swart"]),
        "svart": ("svartr", "black", ["English swart"]),
        "rauðr": ("rauðr", "red", ["English red", "German rot"]),
        "raud": ("rauðr", "red", ["English red", "German rot"]),
        "grœnn": ("grœnn", "green", ["English green", "German grün"]),
        "grøn": ("grœnn", "green", ["English green", "German grün"]),
        "blá": ("blár", "blue, dark", ["English blue"]),
        "blå": ("blár", "blue, dark", ["English blue"]),
        "gulr": ("gulr", "gold, yellow", ["English gold", "German gelb"]),
        "gul": ("gulr", "gold, yellow", ["English gold", "German gelb"]),
        # --- Modifiers: deities ---
        "þór": ("Þórr", "Thor (thunder god)", ["English Thursday"]),
        "tor": ("Þórr", "Thor (thunder god)", ["English Thursday"]),
        "óðinn": ("Óðinn", "Odin (all-father)", ["English Wednesday"]),
        "odin": ("Óðinn", "Odin (all-father)", ["English Wednesday"]),
        "freyr": ("Freyr", "Freyr (fertility god)", ["English Friday?"]),
        "frøy": ("Freyr", "Freyr (fertility god)", ["English Friday?"]),
        "freyja": ("Freyja", "Freyja (fertility goddess)", []),
        "njǫrðr": ("Njǫrðr", "Njord (sea god)", []),
        "njord": ("Njǫrðr", "Njord (sea god)", []),
        "ullr": ("Ullr", "Ull (winter/hunt god)", []),
        "ull": ("Ullr", "Ull (winter/hunt god)", []),
        "týr": ("Týr", "Tyr (war god)", ["English Tuesday"]),
        "baldr": ("Baldr", "Baldr (light god)", []),
        # --- Modifiers: animals ---
        "bjǫrn": ("bjǫrn", "bear", ["English bear", "German Bär"]),
        "elgr": ("elgr", "elk, moose", ["English elk"]),
        "ulfr": ("úlfr", "wolf", ["English wolf", "German Wolf"]),
        "hrafn": ("hrafn", "raven", ["English raven"]),
        "ǫrn": ("ǫrn", "eagle", ["English erne", "German Aar"]),
        "ørn": ("ǫrn", "eagle", ["English erne", "German Aar"]),
        "lax": ("lax", "salmon", ["English lax (archaic)", "German Lachs"]),
        # --- Modifiers: nature/terrain descriptors ---
        "kirkja": ("kirkja", "church", ["English church", "German Kirche"]),
        "kirke": ("kirkja", "church", ["English church", "German Kirche"]),
        "kross": ("kross", "cross (Christian)", ["English cross", "Latin crux"]),
        "borg": ("borg", "fortification, stronghold", ["English borough"]),
        "kaupangr": ("kaupangr", "market town", ["English cheapside"]),
        "bru": ("brú", "bridge", ["German Brücke"]),
        "brú": ("brú", "bridge", ["German Brücke"]),
        "hammar": ("hamarr", "cliff, crag", ["English hammer?"]),
        "hamarr": ("hamarr", "cliff, crag", ["English hammer?"]),
        "fest": ("festr", "firm ground, fastening", ["English fast"]),
        "niðar": ("niðr", "lower, downward (river Nid)", []),
        "nidar": ("niðr", "lower, downward (river Nid)", []),
        "trond": ("Þrœndr", "Trønder (people of Trøndelag)", []),
        "stav": ("stafr", "staff, pillar, landing post", ["English staff"]),
        "staf": ("stafr", "staff, pillar, landing post", ["English staff"]),
    }

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old Norse components."""
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
