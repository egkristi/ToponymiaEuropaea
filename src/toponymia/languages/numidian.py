"""Numidian/Ancient Libyan language module for toponymic analysis.

Numidian (Ancient Libyan) is a pre-Berber language attested in ~1200 inscriptions
from North Africa (3rd c. BCE – 3rd c. CE), written in the Libyco-Berber script
(ancestor of Tifinagh). It represents the substrate beneath modern Berber and
Roman African place-names.

Numidian toponymy connects to European studies through:
- Roman provincial toponymy preserving indigenous names (Africa Proconsularis)
- Latinized Numidian: Cirta (Constantine), Thugga (Dougga), Theveste (Tébessa)
- Substrate in modern Maghrebi Arabic place-names
- Possible connections to pre-Indo-European Mediterranean substrate

Characterized by:
- Root patterns suggesting Berber affinity but distinct phonology
- Names preserved in Latin/Greek sources: -ga, -tha suffixes
- Royal names: Massinissa, Jugurtha, Micipsa (embedded in toponymy)
- Script: Libyco-Berber (eastern and western variants)

Key references:
- Chabot 1940 "Recueil des inscriptions libyques"
- Camps 1961 "Aux origines de la Berbérie"
- Ghaki 2012 "Stèles libyques et néo-puniques de Tunisie"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class NumidianModule(BaseLanguageModule):
    """Language module for Numidian/Ancient Libyan toponyms."""

    language_code = "nxm"
    language_name = "Numidian/Ancient Libyan"
    family = "Afro-Asiatic"
    branch = "Berber (archaic/pre-Berber substrate)"
    period = "3rd c. BCE – 3rd c. CE"
    script = "Lina"  # Libyco-Berber script

    prefixes = [
        "Th-",  # place marker (Thugga, Theveste, Thabarca)
        "Cir-",  # settlement (Cirta = Constantine)
        "Mas-",  # royal/great (Massinissa connection)
        "Tip-",  # elevated (Tipasa)
        "Tha-",  # feminine/place (Thamugadi = Timgad)
        "Sic-",  # border/limit (Sicca Veneria)
        "Zam-",  # place (Zama)
        "Mac-",  # people/place (Mactaris)
        "Hip-",  # harbor? (Hippo Regius = Annaba)
        "Lam-",  # settlement (Lambaesis)
        "Tab-",  # place (Thabraca = Tabarka)
    ]

    suffixes = [
        "-ga",  # place/settlement (Thugga, Zama > Zamga variant)
        "-tha",  # place marker (Lep-tha, variant)
        "-ta",  # settlement/land (Cirta)
        "-sis",  # Latinized place (Lambaesis, Thamugadi)
        "-asa",  # elevated/spring? (Tipasa)
        "-aris",  # Latinized (Mactaris)
        "-gadi",  # fortified? (Thamugadi)
        "-ica",  # place (Utica, Rusucca)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "th": "place, settlement (Libyan prefix, very common)",
        "cir": "settlement, fortified place (Cirta → Constantine)",
        "mas": "great, royal (cf. Massinissa = great leader)",
        "tip": "elevated place, height (Tipasa)",
        "tha": "feminine/place marker (Thamugadi, Thabarca)",
        "sic": "boundary, border region (Sicca)",
        "zam": "olive grove? place (Zama)",
        "mac": "people, tribal area (Mactaris)",
        "hip": "harbor, coastal settlement (Hippo)",
        "lam": "settlement, military post (Lambaesis)",
        "tab": "place, spring area (Thabraca → Tabarka)",
        "ga": "place, settlement (common Libyan suffix)",
        "gadi": "fortified place, stronghold",
        "asa": "spring, water source, height",
        "ugga": "pasture, grazing land (Thugga)",
        "cirta": "city, chief settlement (< *krt)",
        "thugga": "pasture, grazing (Dougga)",
        "theveste": "spring place (Tébessa)",
        "utica": "old settlement (ʿtq = ancient)",
        "hippo": "harbor, river mouth (coastal)",
        "madauros": "settlement of Madores (Madaure)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Numidian toponym into components."""
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.7,
                )
            )
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=middle.lower(),
                        confidence=0.4,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=len(results),
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                    confidence=0.6,
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="compound_modifier",
                    lemma=remainder.lower(),
                    confidence=0.4,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.4,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                    confidence=0.6,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.25,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Numidian in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Known Numidian place-names (strongest signal)
        known_names = [
            "cirta",
            "thugga",
            "theveste",
            "tipasa",
            "utica",
            "hippo",
            "zama",
            "mactaris",
            "lambaesis",
            "thamugadi",
            "madauros",
        ]
        for name in known_names:
            if name in form_lower:
                evidence.append(f"Known Numidian toponym '{name}'")
                score += 0.6
                break

        numidian_prefixes = ["th", "cir", "tip", "tha", "sic", "mac", "hip"]
        for prefix in numidian_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Numidian prefix '{prefix}-'")
                score += 0.25
                break

        numidian_suffixes = ["ga", "gadi", "asa", "aris"]
        for suffix in numidian_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Numidian suffix '-{suffix}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="3rd c. BCE – 3rd c. CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Numidian components."""
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
                        sound_changes=[],
                        sources=["Chabot 1940", "Camps 1961"],
                    )
                )
        return candidates
