"""Breton language module for toponymic analysis.

Breton (Brezhoneg) is a Brythonic Celtic language of Brittany (Armorica):
- Brought from Britain by Celtic migrants (5th-6th century CE)
- Viking contact: Brittany was heavily raided/settled by Norse (9th-10th c.)
  - Norse duchy existed in Nantes region
  - Many coastal names show ON influence
  - Île de Bréhat, Île de Batz — potential Norse adaptations
- Sister language to Welsh and Cornish
- Distinctive Plou-/Lan-/Tre- naming system (ecclesiastical parishes)
- Pre-Norse Celtic substrate for understanding Norse naming in Britain

Breton parish-name system:
- Plou- (< Lat. plebs, parish): Plougastel, Ploumanac'h
- Lan- (< *landa, sacred enclosure): Lannion, Landerneau
- Tre-/Tré- (< *treb, settlement): Trégastel, Tréguier

Key references:
- Fleuriot 1980 "Les origines de la Bretagne"
- Tanguy 1990 "Dictionnaire des noms de communes, trèves et paroisses"
- Falc'hun 1963 "Les noms de lieux celtiques"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class BretonModule(BaseLanguageModule):
    """Language module for Breton toponyms."""

    language_code = "bre"  # ISO 639-3 for Breton
    language_name = "Breton"
    family = "Indo-European"
    branch = "Celtic > Brythonic"
    period = "5th century CE – present"
    script = "Latn"

    prefixes = [
        "Plou-",  # parish (< Lat. plebs; Plougastel)
        "Plo-",  # variant (Ploërmel)
        "Plu-",  # variant (Pluguffan)
        "Lan-",  # sacred enclosure (Lannion, Landerneau)
        "Lam-",  # variant before labial
        "Tre-",  # settlement, homestead (Trégastel, Tréguier)
        "Tré-",  # variant
        "Ker-",  # fortified place/village (Kervignac, Kerlaz)
        "Pen-",  # head, end (Penmarc'h, Penmarch)
        "Loc-",  # holy place (Locmariaquer, Locronan)
        "Guil-",  # ? (Guilvinec, Guilers)
        "Coat-",  # wood, forest (Coat-Méal, Coataudon)
        "Brest-",  # ? hill (Brest < *briga?)
        "Ros-",  # hillock, promontory (Roscoff, Rosporden)
        "Pont-",  # bridge (Pont-Aven, Pontivy)
    ]

    suffixes = [
        "-ec",  # place of (Guérec, Questembert area)
        "-ac",  # Gallo-Roman estate (-acum; shared with French)
        "-enez",  # island (< enez; Ouessant = Enez Eusa)
        "-ster",  # ? (Quimper < *con-fluentia? via Lat.)
        "-oc'h",  # Breton superlative/place
        "-an",  # diminutive
        "-enn",  # collective suffix
        "-aven",  # river (Pont-Aven; < aven, river)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "plou": "parish (< Lat. plebs/plou)",
        "plo": "parish (variant)",
        "plu": "parish (variant)",
        "lan": "sacred enclosure, monastery site",
        "tre": "settlement, homestead (< *treb)",
        "ker": "fortified village, homestead (< *caer)",
        "pen": "head, end, promontory (< *penn)",
        "loc": "holy place, monastery (< Lat. locus)",
        "coat": "wood, forest (< *coit)",
        "ros": "hillock, promontory (< *ross)",
        "pont": "bridge (< Lat. pons)",
        "enez": "island",
        "aven": "river (< *abona)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Breton toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )
        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
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

        if matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.85,
                )
            )
            remainder = form[len(matched_prefix) :]
            if matched_suffix and remainder.lower().endswith(matched_suffix):
                mid = remainder[: len(remainder) - len(matched_suffix)]
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
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=len(results),
                        morph_type="compound_head",
                        lemma=matched_suffix,
                        confidence=0.7,
                    )
                )
            else:
                results.append(
                    SegmentationResult(
                        component=remainder,
                        position=1,
                        morph_type="compound_head",
                        lemma=remainder.lower(),
                        confidence=0.5,
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
        """Classify whether a toponym is likely Breton."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Diagnostic Breton parish prefixes
        breton_parish = ["plou", "plo", "plu", "lan", "tre", "tré"]
        for marker in breton_parish:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Breton parish prefix {marker}-")
                score += 0.45
                break

        # Other Breton prefixes
        breton_other = ["ker", "pen", "loc", "coat", "ros"]
        for marker in breton_other:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Breton prefix {marker}-")
                score += 0.3
                break

        # Breton orthography (c'h, zh, ñ)
        if "c'h" in form_lower or "c'h" in form:
            evidence.append("Breton c'h digraph")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="5th century – present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Breton components."""
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
