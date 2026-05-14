"""Arabic/Moorish language module for toponymic analysis.

Arabic toponymy in Europe is primarily found in the Iberian Peninsula
(al-Andalus, 711–1492 CE) but also in Sicily and Malta.
Characterized by:
- Definite article al- (with assimilation: ad-, ar-, as-, at-, az-...)
- Topographic roots: wādī (valley/river), jabal (mountain), qal'a (fortress)
- Administrative terms: madīna (city), qaṣr (palace), ḥiṣn (fort)
- Hybrid Romance-Arabic forms after reconquest

Key references:
- Asín Palacios 1944 "Contribución a la toponimia árabe de España"
- Oliver Asín 1974 "En torno a los orígenes de Castilla"
- Terés 1986 "Materiales para el estudio de la toponimia hispanoárabe"
- Ferrando 2001 "Topónimos árabes de la provincia de Castellón"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ArabicMoorishModule(BaseLanguageModule):
    """Language module for Arabic/Moorish toponyms in Europe."""

    language_code = "ar"  # ISO 639-1 for Arabic
    language_name = "Arabic/Moorish"
    family = "Afro-Asiatic"
    branch = "Semitic > Central Semitic > Arabic"
    period = "711–1492 CE (al-Andalus); substrate in Iberia"
    script = "Latn (romanized)"

    # Arabic toponymic prefixes (article + common first elements)
    prefixes = [
        "Al-",  # definite article (Almería, Algeciras, Alhambra)
        "Alca-",  # al-qal'a (the fortress: Alcalá)
        "Alco-",  # variant (Alcoy)
        "Guad-",  # wādī (river/valley: Guadalquivir)
        "Guadal-",  # wādī al- (the river: Guadalajara)
        "Beni-",  # banī (sons of: Benicàssim)
        "Ben-",  # ibn/banī (Benidorm)
        "Medina-",  # madīna (city: Medinaceli)
        "Gibral-",  # jabal (mountain: Gibraltar)
        "Rambla-",  # ramla (sandy area: La Rambla)
        "Tara-",  # ṭarīq (road) or ṭara (edge)
        "Algar-",  # al-ġār (the cave: Algarve)
        "Almu-",  # al-munastīr (the monastery: Almería variant)
    ]

    # Arabic toponymic suffixes/elements
    suffixes = [
        "-quivir",  # kabīr (great: Guadalquivir)
        "-medina",  # madīna (city: Medinaceli)
        "-azar",  # al-sūq (market) or azahr (blossom)
        "-cázar",  # al-qaṣr (palace: Alcázar)
        "-ía",  # territorial suffix (Almería, Andalucía)
        "-ife",  # ḫalīfa (caliph: Tenerife?)
        "-mería",  # al-mariyya (watchtower: Almería)
    ]

    # Element meanings for etymology
    ELEMENT_MEANINGS: dict[str, str] = {
        "al": "the (definite article)",
        "alca": "al-qal'a (the fortress, the castle)",
        "guad": "wādī (river, valley, watercourse)",
        "guadal": "wādī al- (the river of)",
        "beni": "banī (sons of, clan of)",
        "ben": "ibn/banī (son of, sons of)",
        "medina": "madīna (city, fortified town)",
        "gibral": "jabal (mountain, rock)",
        "rambla": "ramla (sandy riverbed, seasonal stream)",
        "tara": "ṭarīq (road, path)",
        "algar": "al-ġār (the cave)",
        "almu": "al-munastīr (the fortress/monastery)",
        "quivir": "kabīr (great, large)",
        "azar": "azahār (blossom) or sūq (market)",
        "cázar": "qaṣr (palace, castle < Lat. castrum)",
        "wadi": "wādī (valley, seasonal river)",
        "jabal": "jabal (mountain, hill)",
        "qala": "qal'a (fortress, citadel)",
        "qasr": "qaṣr (palace, castle)",
        "hisn": "ḥiṣn (fortress, stronghold)",
        "burj": "burj (tower)",
        "suq": "sūq (market, bazaar)",
        "hammam": "ḥammām (bath, hot spring)",
        "rabad": "rabaḍ (suburb, quarter)",
        "sahara": "ṣaḥrā' (desert, open land)",
        "tariq": "ṭarīq (road, path, way)",
        "ras": "ra's (head, cape, promontory)",
        "ain": "'ayn (spring, water source)",
        "bab": "bāb (gate, door)",
        "dar": "dār (house, abode)",
        "kaf": "kahf (cave)",
        "mina": "mīnā' (port, harbour)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Arabic/Moorish toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try prefix matching (Arabic article al- is very common)
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

        # Try suffix matching
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
                    confidence=0.7,
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
                    confidence=0.8,
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
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_head",
                    lemma=stem.lower(),
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="derivational_suffix",
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
        """Classify whether a toponym is likely Arabic/Moorish in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Check for Arabic prefixes (strongest signal)
        arabic_prefixes = [
            "al",
            "guad",
            "guadal",
            "beni",
            "ben",
            "medina",
            "gibral",
            "alca",
            "algar",
        ]
        for prefix in arabic_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Arabic prefix {prefix}-")
                score += 0.4
                break

        # Check for Arabic root patterns in the form
        arabic_roots = [
            "wadi",
            "jabal",
            "qasr",
            "qala",
            "hisn",
            "hammam",
            "rabad",
            "tariq",
            "alcaz",
        ]
        for root in arabic_roots:
            if root in form_lower:
                evidence.append(f"Arabic root '{root}'")
                score += 0.3
                break

        # Check for typical Iberian-Arabic phonology
        arabic_phon = ["kh", "gh", "dj", "zz"]
        for phon in arabic_phon:
            if phon in form_lower:
                evidence.append(f"Arabic phoneme '{phon}'")
                score += 0.1
                break

        score = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="711–1492 CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Arabic/Moorish components."""
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
