"""Gothic language module for toponymic analysis.

Gothic is the earliest attested Germanic language (Wulfila's Bible, 4th c.)
and crucial for understanding early Germanic migrations:
- Goths migrated from Scandinavia (Gotland?) → Black Sea → Italy/Iberia
- Toponymic traces: Gotland (Sweden), Götaland, Gothenburg
- Crimean Gothic persisted until 16th century
- Gothic substrate in Romanian/South Slavic place-names
- Visigothic layer in Iberian toponymy (-riks, -ulf names)
- Ostrogothic layer in Italian toponymy (Goito, Goti-)

Key references:
- Wrede 1891 "Über die Sprache der Ostgoten in Italien"
- Gamillscheg 1934–1936 "Romania Germanica"
- Braune & Heidermanns 2004 "Gotische Grammatik"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class GothicModule(BaseLanguageModule):
    """Language module for Gothic toponyms."""

    language_code = "got"  # ISO 639-3 for Gothic
    language_name = "Gothic"
    family = "Indo-European"
    branch = "Germanic > East Germanic"
    period = "200–600 CE (Crimean Gothic to 1500s)"
    script = "Goth/Latn"

    prefixes = [
        "Gaut-",  # Goth/Geat (Gautland, Götaland)
        "Got-",  # Gothic (Gotland, Gothenburg)
        "Gut-",  # variant (Gutasaga)
        "Aust-",  # east (Austrogoti)
        "Wisi-",  # wise/west? (Visigoth)
        "Greutungi-",  # steppe-dwellers (Greuthungi)
        "Thiuda-",  # people (> Deutsch, Teutonic)
        "Harj-",  # army (< *harjaz; Harzgebirge?)
        "Burg-",  # fortress
        "Amal-",  # royal clan (Amal dynasty)
    ]

    suffixes = [
        "-reiks",  # ruler (> -ric/-rich; Gothic personal names in toponyms)
        "-burg",  # fortress (< baurgs)
        "-haims",  # village, home (< haims)
        "-land",  # land
        "-awi",  # watery meadow (> -au in German)
        "-staths",  # place (< staþs)
        "-wigs",  # way, road
        "-brunna",  # spring (< brunna)
        "-ahwa",  # river, water (< aƕa)
        "-fairguni",  # mountain (< fairguni)
        "-gards",  # enclosure (< gards → garðr)
        "-waurms",  # serpent (in river names)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "gaut": "Goth, Geat (tribal name, < *geutaz 'pourer')",
        "got": "Goth (tribal name)",
        "gut": "Goth (Gutnish variant)",
        "aust": "east (< *austrō)",
        "wisi": "wise/worthy (Visigothic)",
        "thiuda": "people, nation (> Deutsch)",
        "harj": "army, host (< *harjaz)",
        "burg": "fortified town (baurgs)",
        "amal": "laborious, brave (Amal dynasty)",
        "reiks": "ruler, king",
        "haims": "village, home",
        "land": "land, territory",
        "staths": "place, shore",
        "brunna": "spring, well",
        "ahwa": "river, water (cognate ON á)",
        "fairguni": "mountain (cf. Erzgebirge)",
        "gards": "enclosure, yard (cf. ON garðr)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Gothic-origin toponym into components."""
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
                    confidence=0.7,
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
                        confidence=0.4,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.7,
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
                    confidence=0.4,
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
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
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
                    morph_type="simplex",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym may have Gothic origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Gothic tribal markers
        gothic_markers = ["got", "gaut", "gut", "goth", "göt", "geat"]
        for marker in gothic_markers:
            if marker in form_lower:
                evidence.append(f"Gothic tribal element '{marker}'")
                score += 0.4
                break

        # Gothic characteristic phonology
        if "aur" in form_lower or "iu" in form_lower:
            evidence.append("Gothic diphthong")
            score += 0.1

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="200–600 CE (Migration Period)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Gothic components."""
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
