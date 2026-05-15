"""Kven/Meänkieli language module for toponymic analysis.

Kven (kvensk) and Meänkieli (meänkieli) are Finnic minority languages
spoken in northern Norway (Kven) and northern Sweden (Meänkieli):

Kven (Norway):
- Spoken in Troms and Finnmark (Tromsø, Alta, Hammerfest areas)
- Descended from Finnish immigrants (1500s–1800s)
- Official minority language in Norway since 2005
- Place-names from Kven settlement alongside Norwegian and Sami names

Meänkieli (Sweden):
- Spoken in Torne Valley (Tornedalen), Norrbotten
- Also called "Tornedalsfinska" (Tornedal Finnish)
- Descended from Finnish speakers before the 1809 border
- Official minority language in Sweden since 2000

Toponymic significance:
- Third naming layer in northern Scandinavia (alongside Norse and Sami)
- Many Finnish-type names in areas not traditionally considered Finnish
- Agricultural/fishing vocabulary distinct from Sami pastoral terms
- Some names wrongly attributed to Sami are actually Kven/Meänkieli
- The Finnish element -niemi, -järvi, -joki found in Norwegian territory

Key references:
- Eriksen 2006 "Kvensk stedsnavn i Nord-Troms"
- Julku 1986 "Suomen ja Norjan rajahistoria"
- Kenttä & Weinstock 1985 "Meänkieli"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KvenMeankieliModule(BaseLanguageModule):
    """Language module for Kven and Meänkieli toponyms."""

    language_code = "fkv"  # ISO 639-3 for Kven
    language_name = "Kven/Meänkieli"
    family = "Uralic"
    branch = "Finnic > Kven Finnish / Meänkieli"
    period = "1500s–present (immigration period; some earlier)"
    script = "Latn"

    prefixes = [
        "Iso-",  # big (Finnish iso; Isojärvi)
        "Pikku-",  # small (Finnish pikku)
        "Ylä-",  # upper (Yläjärvi)
        "Ala-",  # lower (Alajärvi)
        "Pitkä-",  # long (Pitkäjärvi)
        "Musta-",  # black (Mustajärvi, Mustajoki)
        "Valke-",  # white (Kven form; cf. Finnish valkea)
        "Uusi-",  # new (Uusijärvi)
        "Vanha-",  # old
        "Kivi-",  # stone (Kivijärvi)
    ]

    suffixes = [
        "-järvi",  # lake (Finnish järvi; widespread in north)
        "-joki",  # river (Finnish joki; Tenojoki, Ivalojoki)
        "-niemi",  # cape, headland (Finnish niemi; Nordkinnniemi?)
        "-lahti",  # bay, inlet (Finnish lahti)
        "-saari",  # island (Finnish saari)
        "-maa",  # land, ground (Finnish maa)
        "-vuono",  # fjord (< Norse, borrowed into Kven)
        "-vaara",  # hill, forested mountain (Kven/Finnish; cf. Sami)
        "-tunturi",  # bare mountain top (Finnish tunturi)
        "-kangas",  # heath, dry pine forest (Finnish kangas)
        "-suo",  # swamp, bog (Finnish suo)
        "-koski",  # rapids (Finnish koski)
        "-selkä",  # ridge, open water (Finnish selkä)
        "-ranta",  # shore, beach (Finnish ranta)
        "-pelto",  # field (Finnish pelto; agricultural naming)
        "-kylä",  # village (Finnish kylä; Tornionkylä)
        "-mäki",  # hill (Finnish mäki)
        "-lampi",  # pond (Finnish lampi)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "järvi": "lake (Finnic *järwi; widespread in Nordic north)",
        "joki": "river (Finnic *joki; cf. Sami johka < same root)",
        "niemi": "cape, headland (Finnic *niemi)",
        "lahti": "bay, inlet (Finnish/Kven)",
        "saari": "island (Finnish/Kven)",
        "maa": "land, earth (Finnic *maa; very old Uralic word)",
        "vaara": "forested hill (Kven/Finnish; borrowed into Norwegian)",
        "tunturi": "treeless mountain top (Finnish; → Norwegian tundra?)",
        "kangas": "dry heath/pine forest (Finnish/Kven)",
        "suo": "swamp, mire (Finnish/Kven; cf. Sami suopmu)",
        "koski": "rapids (Finnish/Kven)",
        "selkä": "ridge; also open lake water (Finnish)",
        "ranta": "shore, beach (Finnish/Kven)",
        "pelto": "cultivated field (Finnish; agricultural layer)",
        "kylä": "village (Finnish/Kven; cf. Sami gilli)",
        "mäki": "hill (Finnish/Kven)",
        "lampi": "pond, small lake (Finnish/Kven)",
        "iso": "big, great (Finnish iso)",
        "pikku": "small, little (Finnish pikku)",
        "musta": "black (Finnish musta)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kven/Meänkieli toponym into components."""
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

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                meaning = self.ELEMENT_MEANINGS.get(suffix, "")
                results.append(
                    SegmentationResult(
                        segments=[stem, suffix],
                        language=self.language_code,
                        confidence=0.65,
                        notes=(f"Kven/Meänkieli: '{stem}' + '-{suffix}' ({meaning})"),
                    )
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                meaning = self.ELEMENT_MEANINGS.get(prefix, "")
                results.append(
                    SegmentationResult(
                        segments=[prefix, remainder],
                        language=self.language_code,
                        confidence=0.6,
                        notes=(f"Kven/Meänkieli prefix '{prefix}' ({meaning}) + '{remainder}'"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Kven/Meänkieli."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Finnish-type suffixes (distinct from Sami equivalents)
        finnic_suffixes = [
            "järvi",
            "joki",
            "niemi",
            "lahti",
            "saari",
            "koski",
            "kangas",
            "pelto",
            "kylä",
            "mäki",
        ]
        for suf in finnic_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Finnic (Kven) suffix '-{suf}'")
                score += 0.6
                break

        # Finnish-type prefixes (color + geographic)
        finnic_prefixes = ["musta", "valke", "iso", "pikku", "pitkä"]
        for pref in finnic_prefixes:
            if form_lower.startswith(pref):
                evidence.append(f"Finnic (Kven) prefix '{pref}-'")
                score += 0.4
                break

        # Finnish vowel harmony (front vowels: ä, ö, y)
        if "ä" in form_lower or "ö" in form_lower:
            evidence.append("Finnish-type front vowels (ä/ö)")
            score += 0.2

        # Kven-specific: vaara (hill) in Norwegian territory
        if "vaara" in form_lower:
            evidence.append("Kven 'vaara' (forested hill; Finnish loanword)")
            score += 0.5

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Kven/Meänkieli etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.55,
                        notes=(
                            f"Kven/Meänkieli (Finnic) element '{element}' "
                            f"in '{form}'. Third naming layer in northern "
                            "Scandinavia alongside Norse and Sami."
                        ),
                    )
                )

        return candidates
