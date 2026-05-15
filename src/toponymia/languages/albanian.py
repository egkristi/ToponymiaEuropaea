"""Albanian language module for toponymic analysis.

Albanian (Shqip) is one of Europe's most ancient languages, possibly
descended from Illyrian or Thracian:
- Unique branch of Indo-European with no close relatives
- Extensive pre-Slavic, pre-Greek substrate in the Balkans
- Albanian toponyms may preserve very ancient IE elements
- Important for understanding Balkan migrations and substrate layers
- Vikings on the Varangian route passed through Albanian-speaking areas
- Norman/Norse presence in Albania: Normans conquered Durrës 1081

Albanian toponymic patterns:
- Many place-names with unclear etymology may have Illyrian/Albanian roots
- Albanian explains some "dark" Balkan hydronyms
- Interaction with Slavic, Greek, Latin, and Ottoman Turkish layers

Key references:
- Çabej 1976 "Studime etimologjike në fushë të shqipes"
- Demiraj 1999 "Prejardhja e shqiptarëve"
- Topalli 2007 "Fjalor etimologjik i gjuhës shqipe"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AlbanianModule(BaseLanguageModule):
    """Language module for Albanian toponyms."""

    language_code = "sqi"  # ISO 639-3 for Albanian
    language_name = "Albanian"
    family = "Indo-European"
    branch = "Albanian (isolate branch)"
    period = "Attested from 15th century; substrate much older"
    script = "Latn"

    prefixes = [
        "Mal-",  # mountain (Mali i Tomorrit)
        "Fushë-",  # plain (Fushë-Krujë)
        "Kodër-",  # hill (Kodra e Diellit)
        "Liqen-",  # lake (Liqeni i Ohrit)
        "Lum-",  # river (Lumi i Drinit)
        "Rrës-",  # ? (Rrëshen)
        "Kruj-",  # ? spring? (Krujë < IE *kreuH-?)
        "Shkod-",  # ? (Shkodër < Illyrian Scodra)
        "Vlorë-",  # ? (Vlorë/Valona)
        "Butrint-",  # ? (Butrint < Lat. Buthrotum < ?)
    ]

    suffixes = [
        "-ë",  # common Albanian ending (Tiranë, Vlorë)
        "-ës",  # genitive/locative (Elbasan-ës?)
        "-inë",  # place suffix (Sarandë? Korçë?)
        "-at",  # plural/tribal (Berat, Pogradec)
        "-ez",  # ? (Kukës, Lezhë → -ës)
        "-shën",  # saint (< Lat. sanctus; Shëngjin, Shënkoll)
        "-gradec",  # Slavic + Albanian (Pogradec < po + gradec)
        "-ishte",  # collective/place (< Slavic -ište?)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "mal": "mountain (< IE *mol-/*mel-, height)",
        "fushë": "plain, field (< Lat. fossa? or IE)",
        "kodër": "hill, mound",
        "liqen": "lake (< Lat. lacunam?)",
        "lum": "river (< IE *leu-, flow?)",
        "shën": "saint (< Lat. sanctus; Shën Gjin = St. John)",
        "kruj": "spring, fountain (< IE *kreuH-?)",
        "shkod": "ancient city name (< Illyrian Scodra)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Albanian toponym into components."""
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
                    confidence=0.7,
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
        """Classify whether a toponym is likely Albanian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Albanian diagnostic prefixes
        alb_prefixes = ["mal", "fushë", "kodër", "liqen", "shën"]
        for marker in alb_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker):
                evidence.append(f"Albanian element {marker}-")
                score += 0.35
                break

        # Albanian-specific characters
        alb_chars = ["ë", "ç", "gj", "xh", "zh", "sh", "th", "dh", "nj", "rr"]
        for ch in alb_chars:
            if ch in form_lower:
                evidence.append(f"Albanian orthography '{ch}'")
                score += 0.2
                break

        # Albanian definite article postposed (-i, -u, -a, -t for plural)
        # Hard to detect without context, but note -ë ending
        if form_lower.endswith("ë") and len(form_lower) > 3:
            evidence.append("Albanian -ë ending")
            score += 0.1

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Ancient substrate (Illyrian?)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Albanian components."""
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
