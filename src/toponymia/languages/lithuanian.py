"""Lithuanian (lietuvių) language module for toponymic analysis.

Lithuanian toponymy preserves extremely archaic Indo-European forms:
- Hydronyms among oldest in Europe: Nemunas, Neris, Dubysa
- Settlement suffixes: -iškės (place of), -ėnai (people of)
- Baltic roots shared with Latvian/Old Prussian
- Slavic overlay in southeastern dialects
- Very conservative phonology preserving PIE vowel system

Key references:
- Vanagas 1981 "Lietuvių hidronimų etimologinis žodynas"
- Zinkevičius 2005 "Lietuvių tautos kilmė"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LithuanianModule(BaseLanguageModule):
    """Language module for Lithuanian toponyms."""

    language_code = "lit"
    language_name = "Lithuanian"
    family = "Indo-European"
    branch = "Baltic > East Baltic"
    period = "1200 CE–present"
    script = "Latn"

    prefixes = [
        "Didži-",  # great (Didžioji)
        "Maž-",  # small (Mažeikiai)
        "Nauj-",  # new (Naujoji)
        "Sen-",  # old (Senoji)
        "Aukšt-",  # upper/high (Aukštaitija)
        "Žem-",  # lower (Žemaitija)
        "Šiaul-",  # north (Šiauliai region)
    ]

    suffixes = [
        "-iškės",  # place of (Pabradė→Pabiržiškės)
        "-iškis",  # place (Anykščiai variant)
        "-ėnai",  # people of (Klaipėda→Memelėnai)
        "-ynė",  # place of plants (Alksnynė)
        "-upė",  # river (Šventupė)
        "-upis",  # river (masculine)
        "-ežeris",  # lake
        "-ežeras",  # lake variant
        "-kalnas",  # mountain
        "-giria",  # forest
        "-miškas",  # forest
        "-laukis",  # field
        "-pieva",  # meadow
        "-sala",  # island
        "-tiltas",  # bridge
        "-pilė",  # castle (Gedimino pilė)
        "-pilis",  # castle
        "-iai",  # plural settlement (Šiauliai, Panevėžiai)
        "-ai",  # plural (Trakai, Biržai)
        "-ės",  # feminine plural
        "-ava",  # river/place (Suvalkija→Suvalkai variant)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "didži": "great, large",
        "maž": "small",
        "nauj": "new",
        "sen": "old",
        "aukšt": "upper, high",
        "žem": "lower, land (cf. žemė = earth)",
        "upė": "river",
        "upis": "river (masculine)",
        "ežeris": "lake",
        "ežeras": "lake",
        "kalnas": "mountain, hill",
        "giria": "forest (dense)",
        "miškas": "forest",
        "laukis": "field",
        "pieva": "meadow",
        "sala": "island",
        "tiltas": "bridge",
        "pilė": "castle, fortress",
        "pilis": "castle",
        "iškės": "place of (locative)",
        "ėnai": "people of, inhabitants",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Lithuanian toponym into morphological components."""
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
        """Classify whether a toponym is likely Lithuanian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        lithuanian_suffixes = ["iškės", "iškis", "ėnai", "iai", "upė", "kalnas", "giria", "pilis"]
        for marker in lithuanian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Lithuanian suffix -{marker}")
                score += 0.4
                break

        # Lithuanian-specific characters
        lithuanian_chars = ["ą", "č", "ę", "ė", "į", "š", "ų", "ū", "ž"]
        for ch in lithuanian_chars:
            if ch in form_lower:
                evidence.append(f"Lithuanian character '{ch}'")
                score += 0.2
                break

        # Lithuanian word-final patterns
        if form_lower.endswith(("as", "is", "us", "ys", "ė")):
            evidence.append("Lithuanian nominal ending")
            score += 0.1

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Lithuanian components."""
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
