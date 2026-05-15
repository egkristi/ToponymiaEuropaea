"""Proto-Indo-Iranian language module for toponymic analysis.

Proto-Indo-Iranian (PII) is the reconstructed ancestor of all Indo-Iranian
languages (Indo-Aryan + Iranian + Nuristani), spoken approximately during
the 3rd–2nd millennium BCE. It represents the deepest recoverable layer of
Central Asian and steppe toponymy.

Proto-Indo-Iranian toponymic features:
- Reconstructed forms for water/river: *saras-vatī (flowing water > Sarasvatī/Harahvaitī)
- River names: *sindhu (river > Indus; cf. Avestan hindu-)
- Steppe/pastoral vocabulary in place names
- Connected to Andronovo/Sintashta archaeological cultures
- Key for Europe-Asia early IE dispersal path

Key references:
- Lubotsky 2001 "Indo-Iranian Substratum"
- Witzel 2003 "Linguistic Evidence for Cultural Exchange in Prehistoric Western Central Asia"
- Mallory & Adams 2006 "Oxford Introduction to Proto-Indo-European"
- Parpola 2015 "The Roots of Hinduism: Early Aryans and the Indus Civilization"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ProtoIndoIranianModule(BaseLanguageModule):
    """Language module for Proto-Indo-Iranian reconstructed toponyms."""

    language_code = "iir"
    language_name = "Proto-Indo-Iranian"
    family = "Indo-European"
    branch = "Indo-Iranian (ancestral; RECONSTRUCTED)"
    period = "Proto-Indo-Iranian (3rd–2nd millennium BCE); RECONSTRUCTED"
    script = ""  # No script (reconstructed)

    prefixes = [
        "*su-",  # good (> Skt su-, Av hu-)
        "*dus-",  # bad (> Skt dus-, Av duš-)
        "*vi-",  # apart (> Skt vi-, Av vī-)
        "*upa-",  # near (> Skt upa-, Av upa-)
        "*pra-",  # forth (> Skt pra-, Av fra-)
    ]

    suffixes = [
        "*-vatī",  # possessing, having (fem.; > Skt -vatī, Av -vaitī)
        "*-vant",  # possessing (masc.; > Skt -vant, Av -vant)
        "*-stháana",  # place (> Skt sthāna, Av stāna, Pers -stan)
        "*-dhāna",  # holding place (> Skt -dhāna)
        "*-āpas",  # water (plural; > Skt āpas, Av āpō)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "*saras": "flowing water, lake (> Skt saras, Av harah-; RUKI: s > h)",
        "*sindhu": "river, stream (> Skt sindhu = Indus, Av hindu-)",
        "*ap": "water (> Skt āp-, Av āp-, Pers āb)",
        "*vāri": "water (> Skt vāri)",
        "*giri": "mountain (> Skt giri, Av gairi)",
        "*stháana": "place, standing (> -stan; < PIE *steh₂-)",
        "*arya": "noble, own people (> Skt ārya, Av airya- > Iran)",
        "*dāsa": "enemy, stranger (substrate word?)",
        "*ráthas": "chariot (> Skt ratha; Sintashta culture)",
        "*áśvas": "horse (> Skt aśva, Av aspa; key cultural term)",
        "*sū́ryas": "sun (> Skt sūrya; theophoric names)",
        "*mítras": "contract, friend (> Skt mitra, Av miθra)",
        "*vr̥ka": "wolf (> Skt vṛka, Av vəhrka; Hyrcania)",
        "*dhánu": "bow; dry land, shore",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Proto-Indo-Iranian reconstructed toponym."""
        results: list[SegmentationResult] = []
        form_lower = form.lower().lstrip("*")

        # PII forms are typically reconstructed with asterisk
        pii_suffixes = ["vati", "vatī", "vant", "sthaana", "sthana", "stan", "dhana"]
        pii_suffixes_sorted = sorted(pii_suffixes, key=len, reverse=True)

        pii_prefixes = ["su", "dus", "vi", "upa", "pra"]
        pii_prefixes_sorted = sorted(pii_prefixes, key=len, reverse=True)

        matched_prefix = None
        for prefix in pii_prefixes_sorted:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                matched_prefix = prefix
                break

        matched_suffix = None
        for suffix in pii_suffixes_sorted:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix and matched_suffix:
            results.append(
                SegmentationResult(
                    component="*" + form_lower[: len(matched_prefix)],
                    position=0,
                    morph_type="prefix",
                    lemma="*" + matched_prefix,
                    confidence=0.6,
                )
            )
            middle = form_lower[len(matched_prefix) : len(form_lower) - len(matched_suffix)]
            if middle:
                results.append(
                    SegmentationResult(
                        component="*" + middle,
                        position=1,
                        morph_type="stem",
                        lemma="*" + middle,
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component="*" + matched_suffix,
                    position=len(results),
                    morph_type="suffix",
                    lemma="*" + matched_suffix,
                    confidence=0.6,
                )
            )
        elif matched_suffix:
            stem = form_lower[: len(form_lower) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component="*" + stem,
                    position=0,
                    morph_type="stem",
                    lemma="*" + stem,
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component="*" + matched_suffix,
                    position=1,
                    morph_type="suffix",
                    lemma="*" + matched_suffix,
                    confidence=0.6,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component="*" + matched_prefix,
                    position=0,
                    morph_type="prefix",
                    lemma="*" + matched_prefix,
                    confidence=0.55,
                )
            )
            rest = form_lower[len(matched_prefix) :]
            results.append(
                SegmentationResult(
                    component="*" + rest,
                    position=1,
                    morph_type="stem",
                    lemma="*" + rest,
                    confidence=0.4,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component="*" + form_lower,
                    position=0,
                    morph_type="stem",
                    lemma="*" + form_lower,
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym may reflect Proto-Indo-Iranian."""
        form_lower = form.lower().lstrip("*")
        score = 0.0
        evidence: list[str] = []

        # Reconstructed PII hydronyms
        pii_hydro = {
            "saras": "*saras- (flowing water; > Sarasvatī/Harahvaitī)",
            "sindhu": "*sindhu- (river; > Indus, Hindu)",
            "rasa": "*rasā- (moisture; > Av Raŋhā, Skt Rasā)",
        }
        for root, note in pii_hydro.items():
            if root in form_lower:
                evidence.append(f"Proto-Indo-Iranian hydronym: {note}")
                score += 0.5
                break

        # PII possessive suffixes (> -vatī/-vant)
        if form_lower.endswith(("vati", "vatī")):
            evidence.append("PII possessive suffix *-vatī")
            score += 0.3

        # Steppe cultural vocabulary
        steppe_terms = ["asva", "aspa", "ratha", "arya"]
        for term in steppe_terms:
            if term in form_lower:
                evidence.append(f"PII cultural term *{term}")
                score += 0.25
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Proto-Indo-Iranian (3rd–2nd millennium BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for PII components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            key = comp.lemma.lower().lstrip("*").rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get("*" + key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp.lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=["Sanskrit", "Avestan", "Old Persian"],
                        sound_changes=[
                            "PII *s > Av h (RUKI context)",
                            "PII *ć > Skt ś, Av s",
                        ],
                        sources=["Lubotsky 2001", "Mallory & Adams 2006"],
                    )
                )
        return candidates
