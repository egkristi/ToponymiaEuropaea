"""Proto-Germanic and Old English language module.

Handles morphological segmentation and classification of Proto-Germanic
reconstructions and Old English (Anglo-Saxon) place-name elements.

Old English place names constitute the majority of English settlement names
and reflect the Anglo-Saxon colonization of Britain (5th-11th century CE).
Proto-Germanic reconstructions (*PGmc) provide the deeper etymological
layer connecting all Germanic toponymic traditions.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ProtoGermanicModule(BaseLanguageModule):
    """Language module for Proto-Germanic reconstructions in toponymy."""

    language_code = "gem"  # ISO 639-5 for Germanic (family code)
    language_name = "Proto-Germanic"
    family = "Indo-European"
    branch = "Germanic"
    period = "500 BCE – 200 CE (reconstructed)"
    script = "Latn"

    # Proto-Germanic toponymic elements (reconstructed forms with *)
    suffixes = [
        "-*haimaz",  # home (> ON heimr, OE hām, OHG heim)
        "-*stadiz",  # place (> ON staðr, OE stede)
        "-*burgz",  # fort (> ON borg, OE burg, OHG burg)
        "-*bergaz",  # mountain (> ON berg, OE beorg)
        "-*landą",  # land (> ON land, OE land)
        "-*aujō",  # island (> ON ey, OE ēg/īeg)
        "-*wīkō",  # bay (> ON vík, OE wīc)
        "-*dalą",  # valley (> ON dalr, OE dæl)
        "-*nesją",  # headland (> ON nes, OE næss)
        "-*haugaz",  # mound (> ON haugr, OE hōh)
        "-*ford-",  # ford/crossing (> OE ford)
        "-*akvō",  # water (> ON á, OE ēa, Lat. aqua)
        "-*hultą",  # wood (> ON holt, OE holt)
        "-*wangaz",  # field (> ON vangr, OE wang)
    ]

    prefixes = [
        "*Þunraz-",  # Thunder god (> ON Þórr, OE Þunor)
        "*Wōdanaz-",  # Odin (> ON Óðinn, OE Wōden)
        "*Tīwaz-",  # Tyr/Mars (> ON Týr, OE Tīw)
        "*Frawjō-",  # Freya (> ON Freyja, OE Frēo)
        "*Ingwaz-",  # Ing (> ON Yngvi, OE Ing)
        "*Nerthuz-",  # Earth deity (> ON Njǫrðr)
        "*Austraz-",  # East (> ON austr, OE ēast)
        "*Westraz-",  # West (> ON vestr, OE west)
        "*Nurþraz-",  # North (> ON norðr, OE norþ)
        "*Sunþraz-",  # South (> ON suðr, OE sūþ)
        "*Niujaz-",  # New (> ON nýr, OE nīwe)
    ]

    # Key Proto-Germanic sound laws for identification
    stems = [
        "*haimaz",
        "*burgz",
        "*bergaz",
        "*haubidą",
        "*brunnō",
        "*felduz",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment using Proto-Germanic morphology (limited for reconstructions)."""
        results: list[SegmentationResult] = []

        # PGmc forms are typically presented as single reconstructed lexemes
        results.append(
            SegmentationResult(
                component=form,
                position=0,
                morph_type="stem",
                confidence=0.4,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a form shows Proto-Germanic characteristics."""
        evidence: list[str] = []
        score = 0.0

        form_lower = form.lower()

        # Reconstructed forms marked with *
        if form.startswith("*"):
            evidence.append("reconstructed form (asterisk)")
            score += 0.5

        # PGmc phonological features
        pgmc_features = {
            "az": "masculine a-stem ending",
            "ō": "feminine ō-stem ending",
            "iz": "i-stem ending",
            "ą": "neuter a-stem ending",
            "þ": "voiceless dental fricative",
            "hw": "labiovelar",
        }
        for feat, desc in pgmc_features.items():
            if feat in form_lower:
                evidence.append(f"PGmc feature: {desc}")
                score += 0.15

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="proto-germanic" if confidence > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates from Proto-Germanic."""
        candidates: list[EtymologyCandidate] = []

        pgmc_lexicon = {
            "haimaz": ("*haimaz", "home, village", ["ON heimr", "OE hām", "OHG heim"]),
            "burgz": ("*burgz", "fortified place", ["ON borg", "OE burg", "OHG burg"]),
            "bergaz": ("*bergaz", "mountain, hill", ["ON berg", "OE beorg", "OHG berg"]),
            "stadiz": ("*stadiz", "place, stead", ["ON staðr", "OE stede", "OHG stat"]),
            "landą": ("*landą", "land, territory", ["ON land", "OE land", "OHG lant"]),
            "akvō": ("*ahwō", "water, river", ["ON á", "OE ēa", "Lat aqua"]),
            "brunno": ("*brunnō", "spring, well", ["ON brunnr", "OE brunna", "OHG brunno"]),
            "felduz": ("*felþuz", "field, open land", ["ON fold", "OE feld", "OHG feld"]),
        }

        for comp in components:
            key = comp.component.lower().lstrip("*-")
            if key in pgmc_lexicon:
                lemma, meaning, cognates = pgmc_lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=cognates,
                        sound_changes=["Grimm's Law", "Verner's Law"],
                    )
                )

        return candidates


class OldEnglishModule(BaseLanguageModule):
    """Language module for Old English (Anglo-Saxon) toponyms.

    Old English place-name elements are the primary toponymic stratum
    in England and lowland Scotland. The module covers the period
    from the Anglo-Saxon settlement (c. 450 CE) to the Norman
    Conquest (1066 CE).
    """

    language_code = "ang"  # ISO 639-3 for Old English
    language_name = "Old English"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Anglo-Frisian"
    period = "450-1100 CE"
    script = "Latn"

    # Anglo-Saxon settlement suffixes (very productive in English toponymy)
    suffixes = [
        "-ham",  # homestead, village (< PGmc *haimaz)
        "-ton",
        "-tun",  # farmstead, estate (< OE tūn)
        "-ley",
        "-leigh",
        "-lea",  # clearing, meadow (< OE lēah)
        "-bury",
        "-burgh",
        "-borough",  # fortified place (< OE burg/burh)
        "-stead",
        "-stede",  # place, site (< OE stede)
        "-wick",
        "-wich",  # dwelling, dairy farm (< OE wīc)
        "-worth",
        "-worthy",  # enclosure (< OE worð/worðig)
        "-field",  # open land (< OE feld)
        "-ford",  # river crossing (< OE ford)
        "-minster",  # monastery (< OE mynster < Lat monasterium)
        "-ey",
        "-ea",  # island (< OE ēg/īeg)
        "-hurst",  # wooded hill (< OE hyrst)
        "-den",
        "-dene",  # valley (< OE denu)
        "-combe",
        "-comb",  # valley (< OE cumb < Celtic)
        "-thwaite",  # clearing (< ON þveit, borrowed into OE usage)
        "-thorpe",  # hamlet (< ON/OE þorp)
        "-stead",  # place (< OE stede)
        "-pool",  # pool (< OE pōl)
        "-well",  # spring, well (< OE wella)
        "-stow",
        "-stowe",  # holy place, meeting place (< OE stōw)
        "-ing",  # people of (< OE -ingas patronymic)
        "-ingham",  # homestead of (< -ingas + hām)
        "-ington",  # farm of (< -ingas + tūn)
        "-holt",  # wood (< OE holt)
        "-shaw",  # small wood (< OE sceaga)
        "-ness",  # headland (< OE næss)
        "-mouth",  # river mouth (< OE mūða)
        "-bourne",
        "-burn",  # stream (< OE burna)
        "-dale",  # valley (< OE dæl / ON dalr)
        "-bridge",  # bridge (< OE brycg)
        "-church",  # church (< OE cirice)
        "-minster",  # monastery church
        "-chester",
        "-cester",
        "-caster",  # Roman fort (< OE ceaster < Lat castra)
        "-street",  # Roman road (< OE strǣt < Lat strata)
    ]

    # Common Old English first elements
    prefixes = [
        "Ēast-",
        "East-",  # east
        "West-",  # west
        "Norþ-",
        "North-",  # north
        "Sūþ-",
        "South-",  # south
        "Stān-",
        "Stan-",
        "Stone-",  # stone
        "Ēa-",  # river
        "Brōc-",
        "Brook-",  # brook
        "Feld-",
        "Field-",  # open land
        "Wudu-",
        "Wood-",  # wood
        "Hēah-",
        "High-",  # high
        "Lȳtel-",
        "Little-",  # small
        "Micel-",
        "Much-",
        "Great-",  # great
        "Niwe-",
        "New-",  # new
        "Eald-",
        "Old-",  # old
        "Hwīt-",
        "White-",  # white
        "Blæc-",
        "Black-",  # black
        "Rēad-",
        "Red-",  # red
        "Grēne-",
        "Green-",  # green
        "Lēah-",
        "Lee-",  # clearing/meadow (as first element)
        "Cyric-",
        "Kirk-",
        "Church-",  # church
        "Wōden-",  # Woden (deity)
        "Þunor-",
        "Thunder-",  # Thunder (deity)
        "Tīw-",  # Tiw (deity)
        "Ing-",  # tribal/patronymic
    ]

    stems = [
        "tūn",
        "hām",
        "lēah",
        "burg",
        "ford",
        "feld",
        "wīc",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old English toponym into morphological components."""
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

            # Check for -ing- medial (patronymic)
            if stem.lower().endswith("ing") and len(stem) > 3:
                base = stem[:-3]
                if base:
                    results.append(
                        SegmentationResult(
                            component=base,
                            position=0,
                            morph_type="compound_modifier",
                            meaning="personal name / tribe",
                            confidence=0.5,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=stem[-3:],
                        position=1,
                        morph_type="infix",
                        lemma="-ingas",
                        meaning="people of, followers of",
                        confidence=0.6,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=suffix_part,
                        position=2,
                        morph_type="compound_head",
                        lemma=matched_suffix,
                        confidence=0.7,
                    )
                )
            else:
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
                        position=1 if stem else 0,
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
        """Classify whether a name form is likely Old English."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Check suffixes
        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"OE suffix -{suffix}")
                score += 0.4
                break

        # Check prefixes
        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"OE prefix {prefix}-")
                score += 0.3
                break

        # Check for -ing- patronymic pattern
        if "ing" in form_lower and form_lower.endswith(("ham", "ton")):
            evidence.append("-ing- patronymic pattern (e.g., Buckingham, Paddington)")
            score += 0.2

        # Check for OE phonological features
        oe_features = ["æ", "ð", "þ", "ēa", "ċ"]
        for feat in oe_features:
            if feat in form_lower:
                evidence.append(f"OE phonological feature '{feat}'")
                score += 0.1

        # Roman-derived elements indicate post-Roman OE usage
        roman_suffixes = ["chester", "cester", "caster", "street"]
        for rsuf in roman_suffixes:
            if form_lower.endswith(rsuf):
                evidence.append(f"Latin-derived OE element -{rsuf}")
                score += 0.3
                break

        confidence = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="old-english" if confidence > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old English components."""
        candidates: list[EtymologyCandidate] = []

        oe_lexicon = {
            "ham": ("hām", "homestead, village", ["ON heimr", "OHG heim"]),
            "ton": ("tūn", "farmstead, enclosure", ["OHG zūn 'fence'"]),
            "tun": ("tūn", "farmstead, enclosure", ["OHG zūn 'fence'"]),
            "ley": ("lēah", "woodland clearing, meadow", []),
            "leigh": ("lēah", "woodland clearing, meadow", []),
            "lea": ("lēah", "woodland clearing, meadow", []),
            "bury": ("burh/burg", "fortified place", ["ON borg", "OHG burg"]),
            "burgh": ("burh/burg", "fortified place", ["ON borg", "OHG burg"]),
            "borough": ("burh/burg", "fortified place", ["ON borg", "OHG burg"]),
            "wick": ("wīc", "dwelling, dairy farm", ["ON vík", "Lat vicus"]),
            "wich": ("wīc", "dwelling, specialized farm", ["ON vík", "Lat vicus"]),
            "worth": ("worð", "enclosure, homestead", []),
            "worthy": ("worðig", "enclosure", []),
            "field": ("feld", "open land, pasture", ["ON fold", "OHG feld"]),
            "ford": ("ford", "river crossing", ["OHG furt"]),
            "stead": ("stede", "place, site", ["ON staðr", "OHG stat"]),
            "stow": ("stōw", "holy place, meeting place", []),
            "hurst": ("hyrst", "wooded hill, copse", []),
            "den": ("denu", "valley", []),
            "dene": ("denu", "valley", []),
            "well": ("wella", "spring, stream", []),
            "bourne": ("burna", "stream", ["ON brunnr"]),
            "burn": ("burna", "stream", ["ON brunnr"]),
            "chester": ("ceaster", "Roman fort (< Lat castra)", []),
            "cester": ("ceaster", "Roman fort (< Lat castra)", []),
            "caster": ("ceaster", "Roman fort (< Lat castra)", []),
            "minster": ("mynster", "monastery (< Lat monasterium)", []),
            "street": ("strǣt", "paved road (< Lat strata)", []),
            "ey": ("ēg/īeg", "island, dry ground in marsh", ["ON ey"]),
            "ness": ("næss", "headland, promontory", ["ON nes"]),
            "mouth": ("mūða", "river mouth", []),
            "bridge": ("brycg", "bridge", []),
            "church": ("cirice", "church (< Gk kyriakon)", []),
            "holt": ("holt", "small wood", ["ON holt"]),
            "shaw": ("sceaga", "small wood, thicket", []),
            "ing": ("-ingas", "people of, followers of (patronymic)", []),
        }

        for comp in components:
            key = comp.lemma.lower().lstrip("-") if comp.lemma else comp.component.lower()
            if key in oe_lexicon:
                lemma, meaning, cognates = oe_lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=cognates,
                        sources=["Smith, EPNE", "Gelling & Cole 2000"],
                    )
                )

        return candidates
