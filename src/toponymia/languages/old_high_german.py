"""Old High German / Continental Germanic language module for toponymic analysis.

Continental Germanic toponymy dominates central Europe (Germany, Austria,
Switzerland, parts of Netherlands and Belgium). Characterized by:
- Habitative suffixes: -heim (home), -burg (fort), -dorf (village)
- Topographic elements: -wald (forest), -berg (mountain), -feld (field)
- Personal name + possessive patterns (Ludwigsburg, Karlsruhe)
- Palatalization and vowel shifts from OHG to modern dialects

Key references:
- Bach 1952–1956 "Deutsche Namenkunde" (3 vols)
- Förstemann 1856–1859 "Altdeutsches Namenbuch"
- Debus & Seibicke 2012 "Namenkunde" (HSK vol. 11)
- Niemeyer 2012 "Deutsches Ortsnamenbuch"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldHighGermanModule(BaseLanguageModule):
    """Language module for Old High German / Continental Germanic toponyms."""

    language_code = "goh"  # ISO 639-3 for Old High German
    language_name = "Old High German (Continental Germanic)"
    family = "Indo-European"
    branch = "Germanic > West Germanic > High German"
    period = "750–1050 CE (OHG); continues as MHG/NHG"
    script = "Latn"

    # Common Germanic/OHG toponymic prefixes
    prefixes = [
        "Alt-",  # old (Altstadt, Altdorf)
        "Neu-",  # new (Neustadt, Neuburg)
        "Ober-",  # upper (Oberhausen, Oberdorf)
        "Unter-",  # lower (Unterhaching)
        "Nieder-",  # lower (Niedersachsen)
        "Hohen-",  # high (Hohenzollern)
        "Klein-",  # small (Kleinmachnow)
        "Gross-",  # large (Grossbeeren)
        "Schön-",  # beautiful (Schönbrunn)
        "Langen-",  # long (Langenberg)
        "Schwarzen-",  # black (Schwarzenberg)
        "Weissen-",  # white (Weissenburg)
    ]

    # Common Germanic/OHG toponymic suffixes
    suffixes = [
        "-heim",  # home, settlement (Mannheim, Hildesheim)
        "-ham",  # home (English cognate)
        "-burg",  # fortified place, castle (Hamburg, Salzburg)
        "-berg",  # mountain, hill (Heidelberg, Nürnberg)
        "-dorf",  # village (Düsseldorf, Oberdorf)
        "-wald",  # forest (Schwarzwald, Grünwald)
        "-feld",  # field, open land (Bielefeld, Saarfeld)
        "-bach",  # stream, brook (Ansbach, Gladbach)
        "-brunn",  # spring, well (Schönbrunn, Heilbronn)
        "-bronn",  # spring (variant: Heilbronn)
        "-born",  # spring (Low German: Paderborn)
        "-hausen",  # houses, settlement (Oberhausen, Mühlhausen)
        "-hofen",  # courts, farms (Ludwigshafen)
        "-stadt",  # city, place (Darmstadt, Neustadt)
        "-statt",  # place (variant: Ingolstadt)
        "-stedt",  # place (Low German: Helmstedt)
        "-furt",  # ford (Frankfurt, Erfurt)
        "-brück",  # bridge (Osnabrück, Innsbruck)
        "-kirch",  # church (Feldkirch, Neukirchen)
        "-kirchen",  # churches (Gelsenkirchen)
        "-au",  # meadow, water-meadow (Passau, Lindau)
        "-aue",  # meadow (variant)
        "-ach",  # water, river (Biberach)
        "-ingen",  # people of (Tübingen, Göttingen)
        "-ungen",  # people of (Meiningen)
        "-weil",  # settlement (< Lat. villa: Rottenweil)
        "-weiler",  # hamlet (< Lat. villare: Badenweiler)
        "-rode",  # clearing (Wernigerode)
        "-rath",  # clearing (Benrath)
        "-reuth",  # clearing (Bayreuth)
        "-ried",  # marsh clearing (Riedlingen)
    ]

    # Element meanings for etymology
    ELEMENT_MEANINGS: dict[str, str] = {
        "alt": "old",
        "neu": "new",
        "ober": "upper",
        "unter": "lower",
        "nieder": "lower, nether",
        "hohen": "high, elevated",
        "klein": "small, little",
        "gross": "large, great",
        "schön": "beautiful, fair",
        "langen": "long",
        "schwarzen": "black",
        "weissen": "white",
        "heim": "home, settlement (OHG *haim)",
        "ham": "home (cognate of -heim)",
        "burg": "fortified place, castle (OHG burg)",
        "berg": "mountain, hill (OHG berg)",
        "dorf": "village (OHG dorf < *þurp)",
        "wald": "forest (OHG wald)",
        "feld": "field, open land (OHG feld)",
        "bach": "stream, brook (OHG bah)",
        "brunn": "spring, well (OHG brunno)",
        "bronn": "spring (variant of brunn)",
        "born": "spring (Low German)",
        "hausen": "houses, settlement (OHG hūs)",
        "hofen": "courts, farms (OHG hof)",
        "stadt": "city, place (OHG stat)",
        "statt": "place (variant)",
        "stedt": "place (Low German)",
        "furt": "ford, crossing (OHG furt)",
        "brück": "bridge (OHG brucca)",
        "kirch": "church (OHG kirihha < Gk kyriakon)",
        "kirchen": "churches (plural)",
        "au": "water-meadow, island (OHG ouwa)",
        "aue": "meadow (variant)",
        "ach": "water, river (OHG aha)",
        "ingen": "people of, descendants (patronymic)",
        "ungen": "people of (variant)",
        "weil": "settlement (< Latin villa)",
        "weiler": "hamlet (< Latin villare)",
        "rode": "clearing, assart (OHG riod)",
        "rath": "clearing (rhineland variant)",
        "reuth": "clearing (Bavarian variant)",
        "ried": "marsh, reed clearing",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Germanic toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try suffix matching first (Germanic is suffix-heavy for place-names)
        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        # Also try prefix matching
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

        if matched_prefix and matched_suffix:
            prefix_part = form[: len(matched_prefix)]
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=len(results),
                    morph_type="derivational_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_head",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="derivational_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_prefix:
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
                    lemma=remainder.lower(),
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
        """Classify whether a toponym is likely Continental Germanic."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Check for Germanic suffixes
        germanic_suffixes = [
            "heim",
            "burg",
            "berg",
            "dorf",
            "wald",
            "feld",
            "bach",
            "brunn",
            "born",
            "hausen",
            "hofen",
            "stadt",
            "furt",
            "brück",
            "kirch",
            "ingen",
            "weiler",
            "rode",
            "rath",
            "reuth",
        ]
        for suffix in germanic_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                evidence.append(f"Germanic suffix -{suffix}")
                score += 0.35
                break

        # Check for Germanic prefixes
        germanic_prefixes = [
            "alt",
            "neu",
            "ober",
            "unter",
            "nieder",
            "hohen",
            "klein",
            "gross",
            "schön",
        ]
        for prefix in germanic_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                evidence.append(f"Germanic prefix {prefix}-")
                score += 0.25
                break

        # Check for typical German orthography
        german_ortho = ["sch", "ü", "ö", "ä", "ss", "ck", "pf", "tz"]
        for ortho in german_ortho:
            if ortho in form_lower:
                evidence.append(f"German orthography '{ortho}'")
                score += 0.1
                break

        score = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="750–1500 CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Germanic components."""
        candidates: list[EtymologyCandidate] = []

        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get(lemma_key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma_key,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=[],
                    )
                )

        return candidates
