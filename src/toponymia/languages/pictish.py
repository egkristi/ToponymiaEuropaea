"""Pictish language module for toponymic analysis.

Pictish is the extinct pre-Gaelic language of northern/eastern Scotland
(~300–900 CE). It left a distinctive toponymic substrate:
- The Pit- names (< Pictish *pett, 'piece of land') are diagnostic
  - Over 300 Pit- names in eastern Scotland: Pitlochry, Pittenweem, Pitmedden
- Pictish was likely P-Celtic (Brythonic branch), related to Welsh/Cumbric
- Norse settlers in Scotland encountered Pictish substrate names
- Gaelic later overlaid Pictish, but the substrate persists
- Aber- names may be Pictish (vs. Gaelic Inver-)

Pictish elements preserved in place-names:
- Pit-/Pet- (< *pett, portion of land) — DIAGNOSTIC
- Aber- (river mouth) — shared with Welsh/Cumbric
- Carden-/Cardden- (thicket)
- Laner-/Lanark- (clear space)
- Pevr-/Per- (< *per, bright; Perth)

Key references:
- Watson 1926 "The History of the Celtic Place-Names of Scotland"
- Nicolaisen 1976/2001 "Scottish Place-Names"
- Taylor 2011 "Pictish place-names revisited" in Pictish Progress
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PictishModule(BaseLanguageModule):
    """Language module for Pictish toponyms."""

    language_code = "xpi"  # ISO 639-3 for Pictish (x = extinct)
    language_name = "Pictish"
    family = "Indo-European"
    branch = "Celtic > Brythonic (probable)"
    period = "300–900 CE"
    script = "Ogam/Latn"

    prefixes = [
        "Pit-",  # portion of land (< *pett; Pitlochry, Pittenweem)
        "Pet-",  # variant (Petty, Peterculter?)
        "Pett-",  # variant (Pittenweem)
        "Aber-",  # river mouth (< *aber; Aberdeen, Abernethy)
        "Carden-",  # thicket, copse (Cardenden)
        "Laner-",  # clear space (Lanark)
        "Per-",  # bright? (Perth < *per)
        "Pert-",  # bush, copse (cf. Welsh perth)
        "Mor-",  # sea/great (Moray < *mori)
        "Fother-",  # slope? (Fortingall, Forteviot)
    ]

    suffixes = [
        "-lochry",  # ? (Pitlochry; possibly lake + ry)
        "-weem",  # cave (< Gaelic uaimh, via Pictish territory)
        "-medden",  # middle (Pitmedden)
        "-nethy",  # ? (Abernethy — possibly sacred/pure)
        "-deen",  # ? (Aberdeen — possibly *don, water)
        "-four",  # pasture (Pitfour < *four)
        "-cassie",  # path, way (Pitcassie)
        "-gober",  # confluence? goat? (Pittengober)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "pit": "piece of land, estate (< *pett)",
        "pet": "piece of land (variant of *pett)",
        "pett": "piece of land, estate",
        "aber": "river mouth, confluence (cf. Welsh aber)",
        "carden": "thicket, wooded area",
        "laner": "open space, clearing",
        "per": "bright, beautiful (cf. Perth)",
        "pert": "bush, copse (cf. Welsh perth)",
        "mor": "sea, or great (cf. Moray)",
        "fother": "terraced slope (Forteviot)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Pictish toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

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

        if matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.85 if matched_prefix in ("pit", "pet", "pett") else 0.7,
                )
            )
            remainder = form[len(matched_prefix) :]
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="compound_head",
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
        """Classify whether a toponym is likely Pictish."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Pit-/Pet- is THE diagnostic Pictish marker
        if form_lower.startswith(("pit", "pet", "pett")) and len(form_lower) > 4:
            evidence.append("Pictish *pett element (highly diagnostic)")
            score += 0.6

        # Aber- could be Pictish or Cumbric
        elif form_lower.startswith("aber") and len(form_lower) > 5:
            evidence.append("Aber- (Pictish/Brythonic river-mouth)")
            score += 0.3

        # Carden- element
        elif form_lower.startswith("carden") and len(form_lower) > 7:
            evidence.append("Pictish carden- (thicket)")
            score += 0.4

        # Geographic constraint: Pictish names cluster in E/NE Scotland
        # (can't check geography here, but note it)

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="300–900 CE (Pictish)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Pictish components."""
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
