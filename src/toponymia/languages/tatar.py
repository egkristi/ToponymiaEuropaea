"""Tatar language module for toponymic analysis.

The Tatar language (primarily Kazan Tatar / Volga Tatar) is a Kipchak
Turkic language that became the dominant language of the Golden Horde
and its successor khanates (1240s–1783):

- Golden Horde (Ulus of Jochi): controlled Russia, Ukraine, Siberia
- Kazan Khanate (1438–1552): Volga-Ural region
- Crimean Khanate (1441–1783): Crimea, southern Ukraine
- Siberian Khanate (1468–1598): Western Siberia
- Astrakhan Khanate (1466–1556): Lower Volga

Toponymic impact on Europe:
- Hundreds of settlement names across Russia (Kazan, Saratov, Astrakhan)
- Crimean names (Bakhchisaray, Aqmescit/Simferopol, Qırım)
- River/geographic names (Irtysh, Ishim, Tobol)
- Administrative terms preserved as names (yurt, orda, bazar)
- Indirect influence via Russian/Ukrainian on Nordic awareness
  (Norwegian King Håkon IV exchanged envoys with Mongol khans 1240s)

Key references:
- Baskakov 1979 "Tyurkskaya leksika v russkom"
- Jankowski 1997 "Historical-Etymological Dictionary of Pre-Russian
  Habitation Names of the Crimea"
- Golden 1992 "An Introduction to the History of the Turkic Peoples"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class TatarModule(BaseLanguageModule):
    """Language module for Tatar (Golden Horde / Volga-Crimean) toponyms."""

    language_code = "tat"  # ISO 639-3
    language_name = "Tatar"
    family = "Turkic"
    branch = "Kipchak > Kipchak-Bulgar (Volga Tatar)"
    period = "1240–present (Golden Horde through successor khanates)"
    script = "Arab (historical) / Cyrl / Latn"

    prefixes = [
        "Kara-",  # black (Karabash, Karadeniz)
        "Ak-",  # white (Aqmescit, Ak-Saray)
        "Qyzyl-",  # red (Qyzyl-Yar)
        "Yash-",  # green/young (Yashel Üzän)
        "Sar-",  # yellow (Saratov < Sary Tau?)
        "Tash-",  # stone (Tashkent influence)
        "Bash-",  # head, upper (Bashkortostan)
        "Ulu-",  # great (Ulu Orda)
        "Yañ-",  # new (Yañalif)
        "Kük-",  # blue/sky (Kük Orda = Blue Horde)
    ]

    suffixes = [
        "-saray",  # palace (Bakhchisaray, Saray-Berke)
        "-bazar",  # market (from Persian)
        "-balyk",  # city (Turkic)
        "-yurt",  # settlement, camp
        "-tau",  # mountain (Saratov < Sary-tau)
        "-küle",  # lake (Tatar form; cf. Turkish göl)
        "-su",  # water, river
        "-elga",  # river (Tatar; cf. Volga tributaries)
        "-bulay",  # spring
        "-üzän",  # valley, river (Tatar)
        "-abad",  # settlement (from Persian)
        "-stan",  # land/place (from Persian)
        "-orda",  # horde, headquarters
        "-qala",  # fortress (from Arabic)
        "-mescit",  # mosque (from Arabic masjid)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "kara": "black, dark (Turkic color prefix)",
        "ak": "white, pure, western",
        "qyzyl": "red (Tatar form of kızıl)",
        "yash": "green, young, fresh",
        "sar": "yellow, pale",
        "tash": "stone, rock",
        "bash": "head, chief, upper",
        "ulu": "great, grand, senior",
        "yan": "new, fresh",
        "kük": "blue, sky (celestial)",
        "saray": "palace (< Persian sarāy)",
        "bazar": "market (< Persian bāzār)",
        "balyk": "fish; city (Turkic)",
        "yurt": "homeland, settlement, camp",
        "tau": "mountain (Kipchak form)",
        "küle": "lake (Tatar form)",
        "su": "water, river",
        "elga": "river (Tatar)",
        "bulay": "spring, source",
        "üzän": "valley, lowland, river",
        "orda": "army camp, headquarters, horde",
        "qala": "fortress, citadel (< Arabic)",
        "mescit": "mosque (< Arabic masjid)",
        "khan": "ruler, sovereign",
        "bek": "lord, chief",
        "ata": "father, ancestor",
        "ana": "mother",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Tatar toponym into components."""
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

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix):
                remainder = form[len(prefix) :]
                meaning = self.ELEMENT_MEANINGS.get(prefix, "")
                results.append(
                    SegmentationResult(
                        segments=[prefix, remainder],
                        language=self.language_code,
                        confidence=0.6,
                        notes=f"Tatar prefix '{prefix}' ({meaning}) + '{remainder}'",
                    )
                )
                break

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                meaning = self.ELEMENT_MEANINGS.get(suffix, "")
                results.append(
                    SegmentationResult(
                        segments=[stem, suffix],
                        language=self.language_code,
                        confidence=0.6,
                        notes=f"Tatar: '{stem}' + suffix '-{suffix}' ({meaning})",
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Tatar."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Known Tatar place-name elements
        tatar_markers = [
            "saray",
            "kazan",
            "astrakhan",
            "bazar",
            "qala",
            "yurt",
            "orda",
            "khan",
            "bek",
            "tau",
        ]
        for marker in tatar_markers:
            if marker in form_lower:
                evidence.append(f"Contains Tatar element '{marker}'")
                score += 0.4
                break

        # Color+geographic compound pattern (very Turkic)
        color_prefixes = ["kara", "ak", "qyzyl", "sar", "kük", "yash"]
        for color in color_prefixes:
            if form_lower.startswith(color):
                evidence.append(f"Turkic color prefix '{color}-'")
                score += 0.35
                break

        # Tatar-specific suffixes
        tatar_suffixes = ["saray", "elga", "küle", "üzän", "mescit", "qala"]
        for suf in tatar_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Tatar-specific suffix '-{suf}'")
                score += 0.4
                break

        # Back vowel harmony (a, o, u dominant = Turkic indicator)
        vowels = [c for c in form_lower if c in "aeiouäöüəıy"]
        back_vowels = [c for c in vowels if c in "aouıy"]
        if len(vowels) >= 3 and len(back_vowels) / len(vowels) > 0.7:
            evidence.append("Back vowel harmony (Turkic typology)")
            score += 0.1

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Tatar etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.5,
                        notes=f"Tatar element '{element}' in '{form}'",
                    )
                )

        return candidates
