"""Turkmen language module for toponymic analysis.

Turkmen (Türkmençe) is an Oghuz Turkic language spoken in Turkmenistan and
northwestern Iran. It connects to the Seljuk > Ottoman chain and shares
features with both Turkish and Azerbaijani.

Turkmen toponymic features:
- Oghuz Turkic structure with Iranian substrate
- Suffixes: -abad, -gala (fortress), -depe (hill), -suw (water)
- Notable names: Mary (ancient Merv), Aşgabat (Ashgabat, < *ešq-ābād = love-city?),
  Türkmenbaşy, Daşoguz, Balkanabat
- Caspian coast and Karakum desert terminology
- Connection to Seljuk migrations into Anatolia (11th century)

Key references:
- Ataev 1970 "Turkmen Toponymy" (in Russian)
- Clark 1998 "Turkmen Reference Grammar"
- Bosworth 1968 "The History of the Seljuq Turks"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class TurkmenModule(BaseLanguageModule):
    """Language module for Turkmen-origin toponyms."""

    language_code = "tuk"
    language_name = "Turkmen"
    family = "Turkic"
    branch = "Oghuz"
    period = "Proto-Oghuz 8th c.; Turkmen distinct 15th c.–"
    script = "Latn (since 1993); Cyrl (Soviet); Arab (historical)"

    prefixes = [
        "Ak-",  # white (Akdepe)
        "Gara-",  # black (Garabogaz)
        "Gyzyl-",  # red (Gyzylarbat)
        "Täze-",  # new (Täze Yol)
        "Köne-",  # old
        "Uly-",  # great
        "Daş-",  # stone, outer (Daşoguz)
    ]

    suffixes = [
        "-abad",  # settlement (Gyzylarbat, Balkanabat)
        "-gala",  # fortress (Merw gala)
        "-depe",  # hill, mound (Akdepe)
        "-suw",  # water (Garasuw)
        "-dag",  # mountain
        "-göl",  # lake
        "-çeşme",  # spring (< Persian čašma)
        "-guýy",  # well
        "-ýol",  # road
        "-bazar",  # market (< Persian)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ak": "white",
        "gara": "black, large",
        "gyzyl": "red, gold",
        "täze": "new",
        "köne": "old",
        "daş": "stone, outer",
        "depe": "hill, mound (archaeological tell)",
        "gala": "fortress (< Arabic qalʿa)",
        "suw": "water",
        "dag": "mountain",
        "göl": "lake",
        "çeşme": "spring (< Persian čašma)",
        "guýy": "well",
        "ýol": "road, path",
        "bazar": "market (< Persian bāzār)",
        "oguz": "Oghuz tribal name",
        "merw": "ancient city (Margiana; < Old Persian Margu)",
        "ešq": "love (Aşgabat < ešq-ābād?)",
        "balkan": "mountain range (< Turkic balq = mud?)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Turkmen-origin toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes], key=len, reverse=True
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes], key=len, reverse=True
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
                    confidence=0.8,
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
                        confidence=0.5,
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
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
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
                    position=1,
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
                    confidence=0.75,
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
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym has Turkmen origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        tkm_suffixes = ["depe", "gala", "suw", "guýy"]
        for marker in tkm_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Turkmen suffix -{marker}")
                score += 0.4
                break

        tkm_prefixes = ["gara", "gyzyl", "täze", "köne"]
        for marker in tkm_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Turkmen prefix {marker}-")
                score += 0.3
                break

        # Turkmen-specific: ý, ä, ň, ž
        if "ý" in form_lower or "ä" in form_lower:
            evidence.append("Turkmen-specific graphemes (ý, ä)")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Turkmen/Oghuz period" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Turkmen components."""
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
                        cognates=["Turkish " + comp.lemma, "Azerbaijani " + comp.lemma],
                    )
                )
        return candidates
