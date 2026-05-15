"""Latvian (latviešu) language module for toponymic analysis.

Latvian toponymy is Baltic with Finno-Ugric substrata (Livonian):
- River names: Daugava, Gauja (archaic hydronyms)
- Settlement suffixes: -ciems (village), -pils (castle)
- Nature elements: -ezers (lake), -kalns (mountain), -mežs (forest)
- Livonian (Finnic) substrata in Vidzeme/Kurzeme
- German overlay from Teutonic Order/Hanseatic period

Key references:
- Balode & Bušs 2015 "No Abavas līdz Zilupei"
- Endzelīns 1961 "Latvijas PSR vietvārdi"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LatvianModule(BaseLanguageModule):
    """Language module for Latvian toponyms."""

    language_code = "lav"
    language_name = "Latvian"
    family = "Indo-European"
    branch = "Baltic > East Baltic"
    period = "1200 CE–present"
    script = "Latn"

    prefixes = [
        "Liel-",  # great (Lielvārde)
        "Maz-",  # small (Mazirbe)
        "Jaun-",  # new (Jaunjelgava)
        "Vec-",  # old (Vecpiebalga)
        "Aug-",  # upper (Augšdaugava)
        "Lej-",  # lower (Lejasciems)
        "Ziem-",  # north (Ziemeļkurzeme)
        "Dien-",  # south (Dienvidlatgale)
    ]

    suffixes = [
        "-pils",  # castle (Daugavpils, Jēkabpils)
        "-ciems",  # village (Lejasciems)
        "-muiža",  # manor, estate (Turaida muiža)
        "-ezers",  # lake
        "-kalns",  # mountain, hill
        "-mežs",  # forest
        "-upe",  # river
        "-sala",  # island
        "-krasts",  # shore
        "-grīva",  # river mouth (Daugavgrīva)
        "-gals",  # end, edge
        "-sils",  # pine forest
        "-purvs",  # swamp
        "-lauks",  # field
        "-dārzs",  # garden
        "-tilts",  # bridge
        "-ava",  # archaic river suffix (Daugava, Gauja variant)
        "-aine",  # place of abundance
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "liel": "great, large",
        "maz": "small",
        "jaun": "new, young",
        "vec": "old",
        "aug": "upper, high",
        "lej": "lower",
        "pils": "castle, fortress",
        "ciems": "village",
        "muiža": "manor, estate",
        "ezers": "lake",
        "kalns": "mountain, hill",
        "mežs": "forest",
        "upe": "river",
        "sala": "island",
        "krasts": "shore, bank",
        "grīva": "river mouth",
        "sils": "pine forest",
        "purvs": "swamp, bog",
        "lauks": "field",
        "daugava": "great river (< daudz + ava)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Latvian toponym into morphological components."""
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
                    confidence=0.8,
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
        """Classify whether a toponym is likely Latvian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        latvian_suffixes = ["pils", "ciems", "ezers", "kalns", "grīva", "upe", "muiža"]
        for marker in latvian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Latvian suffix -{marker}")
                score += 0.4
                break

        # Latvian-specific characters
        latvian_chars = ["ā", "č", "ē", "ģ", "ī", "ķ", "ļ", "ņ", "š", "ū", "ž"]
        for ch in latvian_chars:
            if ch in form_lower:
                evidence.append(f"Latvian character '{ch}'")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Latvian components."""
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
