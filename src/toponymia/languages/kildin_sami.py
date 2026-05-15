"""Kildin Sámi language module for toponymic analysis.

Kildin Sámi (кӣллт са̄мь кӣлл / kiillt saam' kiill) is the largest of
the Eastern (Kola) Sámi languages with ~350 speakers on the Kola
Peninsula (Murmansk Oblast, Russia).

The Kola Peninsula has an extremely rich Sámi toponymic layer that predates
Russian settlement (which intensified from the 16th century). Many
"Russian" place-names on the Kola Peninsula are actually Russified
Kildin Sámi names.

Key characteristics:
- Written in Cyrillic script (with additional characters)
- Can also be written in Latin transliteration
- Suprasegmental length distinctions
- Palatalization system similar to Skolt Sámi
- -jāvvr (lake) vs N.Sámi jávri
- -jokk (river) vs N.Sámi johka
- -vārr (mountain) vs N.Sámi várri

Geographic coverage:
- Lovozero/Luujāvv'r area (main settlement area)
- Murmansk coast (Кильдин/Kildin Island — name origin)
- Sámi districts of Kola Peninsula interior
- Formerly: wider area now heavily Russified

Known Russified Kildin Sámi names:
- Мурманск (Murmansk) < ON Murman < ? (debated Norse/Sámi)
- Ловозеро (Lovozero) < Kildin Luujāvv'r 'strong lake'
- Хибины (Khibiny) < Kildin *ūmptek/xibinâ (meaning debated)

Key references:
- Kert 1971 "Саамская топонимия Кольского полуострова"
- Szabó 1987 "Kildin Lappish Dictionary"
- Riesler 2009 "Kildin Saami"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KildinSamiModule(BaseLanguageModule):
    """Language module for Kildin Sámi toponyms."""

    language_code = "sjd"  # ISO 639-3
    language_name = "Kildin Sámi"
    family = "Uralic"
    branch = "Sámi > Eastern Sámi > Kola Sámi > Kildin"
    period = "Continuous; ~350 speakers on Kola Peninsula"
    script = "Cyrl (primary), Latn (transliteration)"

    prefixes = [
        "Šuur-",  # big (Latin transliteration)
        "Ucc-",  # small
        "Paajj-",  # upper
        "Vuâll-",  # lower
        "Kõõskâ-",  # middle
        "Tāvv-",  # north
        "Sajj-",  # south
        "Nuõrtt-",  # east
        "Viestâr-",  # west
        "Kūkk-",  # long
        "Ōđđ-",  # new
        "Vuämm-",  # old
    ]

    suffixes = [
        "-jāvv'r",  # lake (Kildin form)
        "-jokk",  # river
        "-vārr",  # mountain
        "-njārgg",  # headland
        "-suell",  # island
        "-vuõpp",  # forest
        "-vuõnn",  # fjord/bay
        "-luõkk",  # bay
        "-kådd",  # shore
        "-čuõkk",  # peak
        "-tuõddâr",  # tundra
        "-pākk",  # cliff
        "-uāivv",  # head, top
        "-čācc",  # water
        "-ēnn",  # big river
        "-kuõšš",  # rapids
        "-ūmptek",  # flat-topped mountain (unique Kola term)
        "-lūkht",  # bay (variant)
    ]

    stems = [
        "jāvv'r",
        "jokk",
        "vārr",
        "njārgg",
        "suell",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kildin Sámi toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_generics = sorted(
            [s.lstrip("-") for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_generic = None
        for generic in sorted_generics:
            if form_lower.endswith(generic.lower()):
                matched_generic = generic
                break

        if matched_generic:
            specific = form[: len(form) - len(matched_generic)]
            generic_part = form[len(form) - len(matched_generic) :]

            if specific:
                results.append(
                    SegmentationResult(
                        component=specific,
                        position=0,
                        morph_type="compound_modifier",
                        meaning="specific/descriptive element",
                        confidence=0.5,
                    )
                )

            results.append(
                SegmentationResult(
                    component=generic_part,
                    position=1 if specific else 0,
                    morph_type="compound_head",
                    lemma=matched_generic,
                    meaning=self._generic_meaning(matched_generic),
                    confidence=0.7,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.3,
                )
            )

        return results

    def _generic_meaning(self, element: str) -> str:
        """Look up meaning of a generic landscape element."""
        meanings = {
            "jāvv'r": "lake",
            "jokk": "river",
            "vārr": "mountain, fell",
            "njārgg": "headland, peninsula",
            "suell": "island",
            "vuõpp": "forest",
            "vuõnn": "fjord, large bay",
            "luõkk": "bay, inlet",
            "kådd": "shore, bank",
            "čuõkk": "peak, summit",
            "tuõddâr": "tundra plateau",
            "pākk": "cliff",
            "uāivv": "head, mountain top",
            "čācc": "water",
            "ēnn": "large river",
            "kuõšš": "rapids",
            "ūmptek": "flat-topped mountain (Kola-specific)",
            "lūkht": "bay, inlet (variant)",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Kildin Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Kildin Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Kildin Sámi modifier {prefix}-")
                score += 0.3
                break

        # Kildin Sámi: macron vowels (ā, ē, ī, ō, ū) in Latin transliteration
        macron_vowels = ["ā", "ē", "ī", "ō", "ū"]
        for mv in macron_vowels:
            if mv in form_lower:
                evidence.append(f"Kildin Sámi macron vowel '{mv}'")
                score += 0.35
                break

        # Apostrophe in Kildin (palatalization/length mark)
        if "'" in form:
            evidence.append("Kildin Sámi palatalization/length mark (')")
            score += 0.25

        # Kola-specific terms
        if "ūmptek" in form_lower or "umptek" in form_lower:
            evidence.append("Kola Sámi specific term 'ūmptek' (flat mountain)")
            score += 0.5

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="kildin-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Kildin Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "jāvv'r": ("jāvv'r", "lake", ["N.Sámi jávri", "Skolt jäu'rr"]),
            "jokk": ("jokk", "river", ["N.Sámi johka", "Skolt jokk"]),
            "vārr": ("vārr", "mountain", ["N.Sámi várri", "Skolt vä'rr"]),
            "njārgg": ("njārgg", "headland", ["N.Sámi njárga"]),
            "suell": ("suell", "island", ["N.Sámi suolu", "Skolt sue'll"]),
            "vuõpp": ("vuõpp", "forest", ["N.Sámi vuopmi"]),
            "vuõnn": ("vuõnn", "fjord", ["N.Sámi vuotna"]),
            "čācc": ("čācc", "water", ["N.Sámi čáhci", "Skolt čää'cc"]),
            "tuõddâr": ("tuõddâr", "tundra", ["N.Sámi duottar"]),
            "ūmptek": ("ūmptek", "flat-topped mountain", ["Kola-specific; no clear cognate"]),
        }

        for comp in components:
            key = comp.lemma.lower() if comp.lemma else comp.component.lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=cognates,
                        sources=["Kert 1971", "Szabó 1987"],
                    )
                )

        return candidates
