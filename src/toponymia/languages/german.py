"""German (Deutsch) language module for toponymic analysis.

German toponymy spans from the North Sea to the Alps and historically
into Central/Eastern Europe through Ostsiedlung:
- Compound structure: determinans + grundwort (Schönburg = schön + Burg)
- Settlement suffixes: -burg, -dorf, -stadt, -heim, -hausen, -feld
- Topographic: -berg, -tal, -bach, -wald, -au, -stein
- Historical layers: Celtic, Roman, Slavic substrata

Key references:
- Bach 1953–1954 "Deutsche Namenkunde"
- Niemeyer 2012 "Deutsches Ortsnamenbuch"
- Berger 1999 "Geographische Namen in Deutschland"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class GermanModule(BaseLanguageModule):
    """Language module for German toponyms."""

    language_code = "deu"
    language_name = "German"
    family = "Indo-European"
    branch = "Germanic > West Germanic > High German"
    period = "750 CE–present"
    script = "Latn"

    prefixes = [
        "Alt-",  # old (Altenburg)
        "Neu-",  # new (Neubrandenburg)
        "Groß-",  # great (Großbritannien)
        "Klein-",  # small (Kleinmachnow)
        "Ober-",  # upper (Oberhausen)
        "Unter-",  # lower (Unterföhring)
        "Nieder-",  # lower (Niedersachsen)
        "Hoch-",  # high (Hochschwarzwald)
        "Schön-",  # beautiful (Schönbrunn)
        "Schwarze-",  # black (Schwarzenberg)
        "Weiß-",  # white (Weißenburg)
        "Rot-",  # red (Rothenburg)
        "Langen-",  # long (Langenberg)
        "Kirch-",  # church (Kirchheim)
        "Stein-",  # stone (Steinbach)
    ]

    suffixes = [
        "-burg",  # fortification, castle (Hamburg, Salzburg)
        "-berg",  # mountain, hill (Heidelberg, Nürnberg)
        "-dorf",  # village (Düsseldorf)
        "-stadt",  # city (Darmstadt)
        "-heim",  # home (Mannheim, Hildesheim)
        "-hausen",  # houses (Mühlhausen)
        "-feld",  # field (Bielefeld)
        "-bach",  # stream (Gladbach, Ansbach)
        "-tal",  # valley (Wuppertal)
        "-wald",  # forest (Greifswald)
        "-au",  # water meadow (Braunau, Passau)
        "-stein",  # stone (Frankenstein)
        "-furt",  # ford (Frankfurt, Erfurt)
        "-brück",  # bridge (Osnabrück, Saarbrücken)
        "-brunn",  # spring, well (Heilbronn)
        "-born",  # spring (Paderborn)
        "-see",  # lake (Bodensee)
        "-hafen",  # harbour (Wilhelmshaven)
        "-münster",  # monastery (Münster)
        "-kirchen",  # church (Gelsenkirchen)
        "-walde",  # forest (variant)
        "-werder",  # island, elevated land
        "-leben",  # inheritance/estate (Eisleben)
        "-ingen",  # people of (Tübingen, Göttingen)
        "-lingen",  # people of (Reutlingen)
        "-ach",  # water (variant of -bach)
        "-land",  # land, territory
        "-mark",  # border territory (Dänemark)
        "-reuth",  # clearing (Bayreuth)
        "-rode",  # clearing (Wernigerode)
        "-rath",  # clearing (Benrath)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "alt": "old",
        "neu": "new",
        "groß": "great, large",
        "klein": "small",
        "ober": "upper",
        "unter": "lower, under",
        "nieder": "lower",
        "hoch": "high",
        "schön": "beautiful",
        "burg": "fortification, castle",
        "berg": "mountain, hill",
        "dorf": "village",
        "stadt": "city, place",
        "heim": "home, settlement",
        "hausen": "houses, settlement",
        "feld": "field, open land",
        "bach": "stream, brook",
        "tal": "valley",
        "wald": "forest",
        "au": "water meadow, island",
        "stein": "stone, rock",
        "furt": "ford, river crossing",
        "brück": "bridge",
        "brunn": "spring, well",
        "born": "spring, well",
        "see": "lake",
        "hafen": "harbour",
        "münster": "monastery, cathedral",
        "kirchen": "church",
        "ingen": "people of, place of",
        "land": "land, territory",
        "mark": "border, march",
        "reuth": "clearing, cleared land",
        "rode": "clearing (from roden)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a German toponym into morphological components."""
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
            # Check if the stem itself starts with a known prefix
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
                            morph_type="compound_head",
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
        """Classify whether a toponym is likely German."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        german_suffixes = [
            "burg",
            "berg",
            "dorf",
            "stadt",
            "heim",
            "hausen",
            "feld",
            "bach",
            "tal",
            "wald",
            "stein",
            "furt",
            "brück",
            "ingen",
            "leben",
            "born",
            "reuth",
            "rode",
            "rath",
        ]
        for marker in german_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"German suffix -{marker}")
                score += 0.4
                break

        german_prefixes = ["alt", "neu", "groß", "klein", "ober", "unter", "nieder", "schön"]
        for marker in german_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"German prefix {marker}-")
                score += 0.25
                break

        # German-specific characters
        if "ü" in form_lower or "ö" in form_lower or "ä" in form_lower or "ß" in form_lower:
            evidence.append("German umlaut/eszett")
            score += 0.15

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="750–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented German components."""
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
                        cognates=[],
                    )
                )
        return candidates
