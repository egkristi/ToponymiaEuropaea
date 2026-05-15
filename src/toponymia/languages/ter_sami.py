"""Ter Sámi language module for toponymic analysis.

Ter Sámi (sää'mekiill / тэрь саамь кӣлл) is the easternmost Sámi
language, spoken on the eastern Kola Peninsula (Russia). It is nearly
extinct with fewer than 10 speakers (all elderly, in Lovozero area).

Despite being nearly extinct as a spoken language, Ter Sámi place-names
survive across the eastern Kola coast (from Iokanga/Yokanga to the
Ponoy/Ponoj river area and the Terskiy Coast).

Historical territory:
- The Terskiy/Терский Coast of the White Sea (name origin: "Ter")
- Iokanga (Jokânga < Ter Sámi *jokk-eŋŋe 'river mouth')
- Ponoy/Ponoj area (< Ter Sámi *Pōnuj 'dog river'?)
- Lumbovka area
- Kanevka/Kānnj area

Ter Sámi is the most divergent Sámi language, classified as its own
sub-branch within Eastern Sámi. Its toponomy preserves features of the
oldest Sámi settlement layer on the White Sea coast.

Key linguistic features:
- Extreme reduction of unstressed vowels
- Unique consonant clusters not found in other Sámi
- jāvvr/javr (lake), jokk (river), vārr (mountain)
- Some forms show convergence with Russian due to long contact

Key references:
- Itkonen 1958 "Koltan- ja kuolanlappalainen sanakirja"
- Terëškin 2002 "Саамско-русский и русско-саамский словарь"
- Saam' killt (Ter Sámi documentation project, 2010s)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class TerSamiModule(BaseLanguageModule):
    """Language module for Ter Sámi toponyms."""

    language_code = "sjt"  # ISO 639-3
    language_name = "Ter Sámi"
    family = "Uralic"
    branch = "Sámi > Eastern Sámi > Kola Sámi > Ter"
    period = "Continuous; nearly extinct (<10 speakers)"
    script = "Cyrl (primary), Latn (transliteration)"

    prefixes = [
        "Šurr-",  # big
        "Ucc-",  # small
        "Paajj-",  # upper
        "Vuâll-",  # lower
        "Kõškâ-",  # middle
        "Tāvv-",  # north
        "Sajj-",  # south
        "Nuõrt-",  # east
        "Viestâr-",  # west
        "Kūkk-",  # long
    ]

    suffixes = [
        "-javr",  # lake (Ter form, most reduced)
        "-jokk",  # river
        "-vārr",  # mountain
        "-njārgg",  # headland
        "-suell",  # island
        "-vuõpp",  # forest
        "-luõkk",  # bay
        "-kådd",  # shore
        "-čokk",  # peak
        "-tuõddâr",  # tundra
        "-pākk",  # cliff
        "-čācc",  # water
        "-eŋŋe",  # river mouth (Ter-specific; cf. Iokanga)
        "-kurr",  # gorge, narrow valley
        "-ūmptek",  # flat-topped mountain
        "-lūkht",  # bay, lagoon
    ]

    stems = [
        "javr",
        "jokk",
        "vārr",
        "njārgg",
        "eŋŋe",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Ter Sámi toponym into morphological components."""
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
            "javr": "lake",
            "jokk": "river",
            "vārr": "mountain, fell",
            "njārgg": "headland, peninsula",
            "suell": "island",
            "vuõpp": "forest",
            "luõkk": "bay, inlet",
            "kådd": "shore, bank",
            "čokk": "peak, summit",
            "tuõddâr": "tundra plateau",
            "pākk": "cliff",
            "čācc": "water",
            "eŋŋe": "river mouth (Ter Sámi specific)",
            "kurr": "gorge, narrow valley",
            "ūmptek": "flat-topped mountain (Kola-specific)",
            "lūkht": "bay, coastal lagoon",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Ter Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Ter Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Ter Sámi modifier {prefix}-")
                score += 0.3
                break

        # Ter Sámi specific: eŋŋe (river mouth) — highly diagnostic
        if "eŋŋe" in form_lower or "enge" in form_lower:
            evidence.append("Ter Sámi 'eŋŋe' (river mouth)")
            score += 0.6

        # Macron vowels in transliteration
        macron_vowels = ["ā", "ē", "ī", "ō", "ū"]
        for mv in macron_vowels:
            if mv in form_lower:
                evidence.append(f"Kola Sámi macron vowel '{mv}'")
                score += 0.2
                break

        # ŋ character (used in Ter Sámi eŋŋe, but also in N.Sámi)
        if "ŋ" in form_lower:
            evidence.append("Sámi ŋ character")
            score += 0.1

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="ter-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Ter Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "javr": ("javr", "lake", ["N.Sámi jávri", "Kildin jāvv'r", "Skolt jäu'rr"]),
            "jokk": ("jokk", "river", ["N.Sámi johka", "Kildin jokk"]),
            "vārr": ("vārr", "mountain", ["N.Sámi várri", "Kildin vārr"]),
            "njārgg": ("njārgg", "headland", ["N.Sámi njárga"]),
            "suell": ("suell", "island", ["N.Sámi suolu", "Kildin suell"]),
            "čācc": ("čācc", "water", ["N.Sámi čáhci", "Kildin čācc"]),
            "tuõddâr": ("tuõddâr", "tundra", ["N.Sámi duottar"]),
            "eŋŋe": (
                "eŋŋe",
                "river mouth",
                ["Specific to Ter Sámi; cf. Iokanga < *jokk-eŋŋe"],
            ),
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
                        confidence=0.55,
                        cognates=cognates,
                        sources=["Itkonen 1958", "Terëškin 2002"],
                    )
                )

        return candidates
