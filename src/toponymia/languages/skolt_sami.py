"""Skolt Sámi language module for toponymic analysis.

Skolt Sámi (sää'mǩiõll) is an Eastern Sámi language spoken in the
Sevettijärvi area of Utsjoki (Finland) and formerly in the Pechenga/
Petsamo area (now Russia). ~300 speakers remain.

History:
- Originally spoken across the Pechenga (Petsamo) area
- After WWII (1944), Finland ceded Petsamo to USSR
- Skolt Sámi speakers were relocated to Sevettijärvi/Nellim (Finland)
- Russian Skolts remained in Murmansk Oblast (very few speakers)

Key differences from other Sámi languages:
- Palatalization system (ǩ, ǧ, ǥ, etc.)
- Suprasegmental features (vowel length, palatalization)
- Different vocabulary from both N.Sámi and Inari Sámi
- -jäu'rr (lake) vs N.Sámi jávri, Inari jävri
- -jokk (river) vs N.Sámi johka
- -vä'rr (mountain) vs N.Sámi várri

Geographic coverage (traditional territory):
- Suõ'nn'jel/Suonikylä (now in Russia)
- Peäccam/Pechenga/Petsamo area (Russia, formerly Finland)
- Njauddâm/Neiden (Norway)
- Čevetjäu'rr/Sevettijärvi (Finland — current main location)
- Njeä'llem/Nellim (Finland)

Key references:
- Sammallahti & Mosnikoff 1991 "Suomi-koltansaame sanakirja"
- Feist 2010 "A Grammar of Skolt Saami"
- Mosnikoff & Sammallahti 1988 "U'cc sää'm-lää'dd sää'nnǩeä'rjj"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SkoltSamiModule(BaseLanguageModule):
    """Language module for Skolt Sámi toponyms."""

    language_code = "sms"  # ISO 639-3
    language_name = "Skolt Sámi"
    family = "Uralic"
    branch = "Sámi > Eastern Sámi > Skolt Sámi"
    period = "Continuous; ~300 speakers (relocated 1944)"
    script = "Latn"

    prefixes = [
        "Šuu'r-",  # big
        "Ucc-",  # small
        "Pââ'jj-",  # upper
        "Vuâlla-",  # lower
        "Kõõsk-",  # middle
        "Tâ'vv-",  # north
        "Saujj-",  # south
        "Nuõrtt-",  # east
        "Viõstâr-",  # west
        "Kuu'ǩǩ-",  # long
        "Õđ-",  # new
        "Vuä'mm-",  # old
        "Čää'pp-",  # black
        "Vii'lǧǧ-",  # white
    ]

    suffixes = [
        "-jäu'rr",  # lake (Skolt form; cf. N.Sámi jávri)
        "-jokk",  # river (cf. N.Sámi johka)
        "-vä'rr",  # mountain (cf. N.Sámi várri)
        "-njä'rǧǧ",  # headland (cf. N.Sámi njárga)
        "-sue'll",  # island (cf. N.Sámi suolu)
        "-vuõ'pp",  # forest (cf. N.Sámi vuopmi)
        "-vuõnn",  # fjord (cf. N.Sámi vuotna)
        "-luõ'kk",  # bay (cf. N.Sámi luokta)
        "-kå'dd",  # shore (cf. N.Sámi gáddi)
        "-čuõ'kk",  # peak (cf. N.Sámi čohkka)
        "-tuõddâr",  # tundra (cf. N.Sámi duottar)
        "-pää'kk",  # cliff (cf. N.Sámi bákti)
        "-uä'iv",  # head, top (cf. N.Sámi oaivi)
        "-čää'cc",  # water (cf. N.Sámi čáhci)
        "-ee'nn",  # big river (cf. N.Sámi eatnu)
        "-kue'šš",  # rapids
        "-lää'dd",  # flatland
    ]

    stems = [
        "jäu'rr",
        "jokk",
        "vä'rr",
        "njä'rǧǧ",
        "sue'll",
        "vuõ'pp",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Skolt Sámi toponym into morphological components."""
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
                        confidence=0.55,
                    )
                )

            results.append(
                SegmentationResult(
                    component=generic_part,
                    position=1 if specific else 0,
                    morph_type="compound_head",
                    lemma=matched_generic,
                    meaning=self._generic_meaning(matched_generic),
                    confidence=0.75,
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
            "jäu'rr": "lake",
            "jokk": "river",
            "vä'rr": "mountain, fell",
            "njä'rǧǧ": "headland, peninsula",
            "sue'll": "island",
            "vuõ'pp": "forest",
            "vuõnn": "fjord",
            "luõ'kk": "bay, inlet",
            "kå'dd": "shore, bank",
            "čuõ'kk": "peak, summit",
            "tuõddâr": "tundra plateau",
            "pää'kk": "cliff",
            "uä'iv": "head, mountain top",
            "čää'cc": "water",
            "ee'nn": "large river",
            "kue'šš": "rapids",
            "lää'dd": "flat area, plain",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Skolt Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Skolt Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Skolt Sámi modifier {prefix}-")
                score += 0.3
                break

        # Skolt Sámi highly diagnostic: palatalization marks (ǩ, ǧ, ǥ)
        skolt_chars = ["ǩ", "ǧ", "ǥ", "ʹ", "õ"]
        for char in skolt_chars:
            if char in form_lower:
                evidence.append(f"Skolt Sámi palatalization/softening mark '{char}'")
                score += 0.4
                break

        # Skolt Sámi: apostrophe-marked consonants (geminate softening)
        if "'" in form:
            evidence.append("Skolt Sámi softening apostrophe (ʹ)")
            score += 0.3

        # Double vowels with special Skolt patterns
        skolt_vowels = ["õõ", "ää", "uu", "õ"]
        for sv in skolt_vowels:
            if sv in form_lower:
                evidence.append(f"Skolt Sámi vowel pattern '{sv}'")
                score += 0.15
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="skolt-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Skolt Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "jäu'rr": ("jäu'rr", "lake", ["N.Sámi jávri", "Inari jävri", "Kildin jāvvr"]),
            "jokk": ("jokk", "river", ["N.Sámi johka", "Kildin jokk"]),
            "vä'rr": ("vä'rr", "mountain", ["N.Sámi várri", "Kildin vārr"]),
            "njä'rǧǧ": ("njä'rǧǧ", "headland", ["N.Sámi njárga"]),
            "sue'll": ("sue'll", "island", ["N.Sámi suolu"]),
            "vuõ'pp": ("vuõ'pp", "forest", ["N.Sámi vuopmi"]),
            "vuõnn": ("vuõnn", "fjord", ["N.Sámi vuotna"]),
            "luõ'kk": ("luõ'kk", "bay", ["N.Sámi luokta"]),
            "čää'cc": ("čää'cc", "water", ["N.Sámi čáhci", "Inari čääci"]),
            "tuõddâr": ("tuõddâr", "tundra", ["N.Sámi duottar"]),
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
                        confidence=0.65,
                        cognates=cognates,
                        sources=[
                            "Sammallahti & Mosnikoff 1991",
                            "Feist 2010",
                        ],
                    )
                )

        return candidates
