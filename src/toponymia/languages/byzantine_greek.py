"""Byzantine/Medieval Greek language module for toponymic analysis.

Medieval Greek toponymy is relevant for Viking contact through the
Varangian route (Austrvegr) from Scandinavia to Constantinople:
- Varangians served as Byzantine emperor's personal guard (988–1204)
- ON Miklagarðr = Constantinople (Greek Megalē Polis)
- Rune stones reference Grikkland, Serkland via Byzantine trade routes
- Greek influence on Slavic place-naming (e.g., -polis → -pol')
- Norman/Viking principalities in Southern Italy/Sicily (Greek substrata)

Key references:
- Blöndal 1978 "The Varangians of Byzantium"
- Melnikova 2011 "The Eastern World of the Vikings"
- Trapp et al. 2001 "Tabula Imperii Byzantini"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ByzantineGreekModule(BaseLanguageModule):
    """Language module for Byzantine/Medieval Greek toponyms."""

    language_code = "grc"  # ISO 639-3 for Ancient Greek (covers Medieval)
    language_name = "Byzantine Greek"
    family = "Indo-European"
    branch = "Hellenic"
    period = "330–1453 CE"
    script = "Grek"

    prefixes = [
        "Mega-",  # great (Megalopolis)
        "Mikro-",  # small (Mikrolimano)
        "Neo-",  # new (Neapolis→Napoli)
        "Palaio-",  # old (Palaiopolis)
        "Kalo-",  # beautiful (Kalokairi)
        "Leuko-",  # white (Lefkada)
        "Melano-",  # black (Melanoudion)
        "Hierro-",  # holy (Hierapolis)
        "Hagio-",  # saint (Hagios → Agios)
        "Agio-",  # saint (modern form)
        "Chryso-",  # golden (Chrysopolis)
        "Akro-",  # high, cape (Akropolis)
    ]

    suffixes = [
        "-polis",  # city (Constantinople, Adrianople)
        "-oupolis",  # city (Thessaloniki variant)
        "-kastron",  # castle (< Latin castrum)
        "-chorion",  # village
        "-limni",  # lake (< limnē)
        "-potamos",  # river (Mesopotamia)
        "-oros",  # mountain (Olympos)
        "-nesos",  # island (Peloponnesos)
        "-nisos",  # island (modern variant)
        "-limen",  # harbour (Eurymedon)
        "-petra",  # rock (Meteora)
        "-pyrgos",  # tower
        "-stasis",  # station, stopping place
        "-dromos",  # road, course
        "-agora",  # marketplace
        "-therme",  # hot spring (Thessaloniki)
        "-thalassa",  # sea
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "mega": "great, large",
        "mikro": "small",
        "neo": "new",
        "palaio": "old, ancient",
        "kalo": "beautiful, good",
        "leuko": "white",
        "melano": "black, dark",
        "hierro": "holy, sacred",
        "hagio": "saint, holy (hagios)",
        "agio": "saint (modern form)",
        "chryso": "golden",
        "akro": "high point, cape",
        "polis": "city, city-state",
        "kastron": "castle, fortified place (< castrum)",
        "chorion": "village, place",
        "limni": "lake",
        "potamos": "river",
        "oros": "mountain",
        "nesos": "island",
        "limen": "harbour, port",
        "petra": "rock, stone",
        "pyrgos": "tower",
        "agora": "marketplace, assembly",
        "therme": "hot spring, bath",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Byzantine Greek toponym into components."""
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
                    confidence=0.85,
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
                    confidence=0.85,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
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
                    confidence=0.85,
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
        """Classify whether a toponym is likely Byzantine Greek."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        greek_suffixes = ["polis", "oupolis", "kastron", "potamos", "nesos", "nisos", "oros"]
        for marker in greek_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Greek suffix -{marker}")
                score += 0.4
                break

        greek_prefixes = ["mega", "neo", "palaio", "hagio", "agio", "chryso", "akro"]
        for marker in greek_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Greek prefix {marker}-")
                score += 0.3
                break

        # Greek phonetic patterns in transliteration
        greek_patterns = ["th", "ph", "ch", "ps", "ks"]
        for pat in greek_patterns:
            if pat in form_lower:
                evidence.append(f"Greek phonetic '{pat}'")
                score += 0.1
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="330–1453 CE (Byzantine)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Byzantine Greek components."""
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
