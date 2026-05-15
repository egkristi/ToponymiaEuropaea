"""Middle Low German (Mittelniederdeutsch) language module for toponymic analysis.

Middle Low German (MLG) was the lingua franca of the Hanseatic League
(1200–1600) and massively influenced Nordic place-names:
- Bergen (Norway), Stockholm, Visby all had German-speaking populations
- Scandinavian cities adopted German administrative terminology
- Norwegian/Swedish borrowed -gate (street), -stræde, -torv (market)
- German merchants named quarters: Bryggen, Tyske Brygge (German Wharf)
- Danish absorbed hundreds of Low German place-name elements

Key references:
- Laur 1992 "Historisches Ortsnamenlexikon von Schleswig-Holstein"
- Brattegard 1945 "Die mittelniederdeutsche Geschäftssprache des Hansekontors zu Bergen"
- Nynäs 2001 "Tyska lånord i svenska ortnamn"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MiddleLowGermanModule(BaseLanguageModule):
    """Language module for Middle Low German (Hanseatic) toponyms."""

    language_code = "gml"  # ISO 639-3 for Middle Low German
    language_name = "Middle Low German"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Low German"
    period = "1200–1600 CE"
    script = "Latn"

    prefixes = [
        "Nien-",  # new (Nienstedten)
        "Olden-",  # old (Oldenburg)
        "Groten-",  # great (Grotendeich)
        "Lütten-",  # small (Lütten Klein)
        "Oster-",  # east (Osterode)
        "Wester-",  # west (Westerstede)
        "Norder-",  # north (Norderney)
        "Süder-",  # south (Süderbrarup)
        "Hoge-",  # high
        "Neder-",  # lower (Niederdeutsch)
        "Schön-",  # beautiful (Schönberg)
        "Swarte-",  # black (Schwartau)
        "Witte-",  # white (Wittenberge)
    ]

    suffixes = [
        "-borg",  # castle, fortress (Hamburg, Flensburg)
        "-burg",  # variant
        "-büttel",  # settlement (Wolfenbüttel, Wandsbek)
        "-stedt",  # place (Helmstedt, Nienstedten)
        "-stede",  # variant
        "-hagen",  # enclosure (Kopenhagen, Hagen)
        "-haven",  # harbour (Bremerhaven, Cuxhaven)
        "-husen",  # houses (Nordhausen, Mühlhausen)
        "-dorp",  # village (< þorp; Ahrensdorf)
        "-torp",  # variant
        "-beke",  # stream (Lübeck, Reinbek)
        "-fleet",  # channel, tidal creek (Neustadt/Fleet)
        "-werder",  # island, elevated land (Werder)
        "-damm",  # dam (Amsterdam, Potsdam)
        "-brügge",  # bridge (Brügge/Bruges)
        "-markt",  # market
        "-strate",  # street (> Scandinavian -stræde)
        "-gat",  # street, passage (> Scand. -gate)
        "-torf",  # village (variant of -dorp)
        "-holm",  # islet (shared with ON, but MLG transmission)
        "-sund",  # strait (Stralsund)
        "-wik",  # bay, trading place (Schleswig, Brunswick)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "nien": "new",
        "olden": "old",
        "groten": "great, large",
        "lütten": "small, little",
        "borg": "castle, fortified town",
        "burg": "castle, fortified town",
        "büttel": "settlement, estate",
        "stedt": "place, site (< stede)",
        "hagen": "enclosure, hedged field",
        "haven": "harbour, port",
        "husen": "houses, settlement",
        "dorp": "village",
        "torp": "village (< þorp)",
        "beke": "stream, brook",
        "fleet": "tidal channel, creek",
        "werder": "river island, elevated land",
        "damm": "dam, embankment",
        "brügge": "bridge",
        "markt": "market, market place",
        "strate": "street, paved road",
        "gat": "street, passage, opening",
        "holm": "small island",
        "sund": "strait, sound",
        "wik": "bay, trading settlement",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Middle Low German toponym into morphological components."""
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
                        confidence=0.8,
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
                            confidence=0.5,
                        )
                    )
            else:
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
                    position=len(results),
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
                    confidence=0.7,
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
        """Classify whether a toponym is likely Middle Low German."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        mlg_suffixes = [
            "borg",
            "burg",
            "büttel",
            "stedt",
            "stede",
            "hagen",
            "haven",
            "husen",
            "beke",
            "fleet",
            "werder",
            "damm",
            "wik",
        ]
        for marker in mlg_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"MLG suffix -{marker}")
                score += 0.35
                break

        mlg_prefixes = ["nien", "olden", "groten", "lütten"]
        for marker in mlg_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"MLG prefix {marker}-")
                score += 0.25
                break

        # Low German umlaut ü (distinct from High German in distribution)
        if "ü" in form_lower and ("büttel" in form_lower or "lüt" in form_lower):
            evidence.append("MLG characteristic ü")
            score += 0.15

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–1600 CE (Hanseatic)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for MLG components."""
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
