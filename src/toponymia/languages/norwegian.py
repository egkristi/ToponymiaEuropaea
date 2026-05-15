"""Norwegian language module for toponymic analysis.

Norwegian (Bokmål/Nynorsk) represents the modern continuation of Old Norse
in Norway, with distinctive phonological developments that affect
place-name forms. Important to distinguish from Danish (administrative
overlay 1380–1814) and Swedish (union 1814–1905).

Key Norwegian phonological changes from Old Norse:
- ON -staðir > Norw. -stad/-ster/-ste (Ullensvang < Ullarstaðir)
- ON -heimr > Norw. -heim/-hem/-um/-im (Solheim, Bærum < Beruheimr)
- ON -vin (meadow) > Norw. -vin/-ven/-ven (Sandven, Bjørgvin > Bergen)
- ON -bólstaðr > Norw. -bøl/-bol/-bøle (Tynsbøl)
- ON -setr > Norw. -seter/-sæter/-set (Haugseter)
- ON þ > t, ð > d (Þórr > Tor-)

Bokmål vs Nynorsk form differences:
- Bm. -gård vs Nn. -gard
- Bm. -elv vs Nn. -elv (both from ON elfr)
- Bm. -fjell vs Nn. -fjell (from ON fjall)

Norwegian-specific compounding patterns for place-names differ from
Swedish/Danish in vowel quality, consonant assimilation, and suffix
reduction patterns.

Key references:
- Rygh 1898 "Norske Gaardnavne" (authoritative farm-name corpus)
- Sandnes & Stemshaug 1976 "Norsk Stadnamnleksikon"
- Hovda 1966 "Norske fiskeméd"
- NSL (Norsk Stadnamnleksikon) 1997
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class NorwegianModule(BaseLanguageModule):
    """Language module for Norwegian (Bokmål/Nynorsk) toponyms."""

    language_code = "nor"  # ISO 639-2/3
    language_name = "Norwegian"
    family = "Indo-European"
    branch = "Germanic > North Germanic > West Scandinavian > Norwegian"
    period = "1350 CE–present (post-Old Norse)"
    script = "Latn"

    prefixes = [
        "Stor-",  # great, big (Storfjord, Storskog)
        "Lille-",  # little (Lillehammer, Lillestrøm)
        "Nord-",  # north (Nordfjord, Nordkapp)
        "Sør-",  # south (Sørreisa, Sørlandet)
        "Øst-",  # east (Østfold, Østerdalen)
        "Vest-",  # west (Vestfold, Vestland)
        "Ny-",  # new (Nyborg, Nydalen)
        "Gamle-",  # old (Gamlebyen)
        "Ytre-",  # outer (Ytre Arna)
        "Indre-",  # inner (Indre Troms)
        "Øvre-",  # upper (Øvre Eiker)
        "Nedre-",  # lower (Nedre Eiker)
    ]

    suffixes = [
        "-heim",  # home, settlement (< ON heimr; Solheim, Trondheim)
        "-hem",  # reduced form of -heim (Bærum < *Beruheimr)
        "-stad",  # place, stead (< ON staðr; Hallingstad)
        "-ster",  # contracted -staðir (Ullenster)
        "-rud",  # clearing (< ON ruð; Smedsrud, Norderud)
        "-rud",  # Østlandet variant
        "-rød",  # clearing (< ON ruð; Vestfold/Østfold form: Sanderød)
        "-set",  # dwelling, seat (< ON setr; Hovset)
        "-seter",  # mountain farm (< ON setr; Haugseter)
        "-bøl",  # farm (< ON bólstaðr; Tynsbøl)
        "-vik",  # bay, inlet (< ON vík; Narvik, Sandvika)
        "-vika",  # definite form of vik
        "-fjord",  # fjord (Sognefjord, Hardangerfjord)
        "-nes",  # headland, cape (< ON nes; Dramnes, Bygdøynes)
        "-øy",  # island (< ON ey; Nøtterøy, Kvaløy)
        "-ø",  # island variant (Askø)
        "-dal",  # valley (< ON dalr; Hallingdal, Gudbrandsdal)
        "-dalen",  # definite form
        "-berg",  # mountain (< ON berg; Tønsberg)
        "-ås",  # ridge (< ON áss; Haslås, Frognerås)
        "-voll",  # field (< ON vǫllr; Tryvannsvollen)
        "-land",  # land, farm (< ON land; Rogaland, Nordland)
        "-gård",  # farm (< ON garðr; Bakgård, Åsgård)
        "-gard",  # Nynorsk form
        "-by",  # town/settlement (Grimsby, Granby)
        "-elv",  # river (< ON elfr; Glomma = Glåma)
        "-bekk",  # stream (< ON bekkr; Sandbekk)
        "-tjern",  # tarn, small lake (Maridaltjern)
        "-vann",  # lake, water (< ON vatn; Mjøsa is exceptional)
        "-vatn",  # Nynorsk lake form
        "-foss",  # waterfall (< ON fors; Rjukanfossen)
        "-mo",  # sandy plain (< ON mór; Mosjøen, Brumunddal)
        "-vin",  # meadow (< ON vin; archaic: Bjørgvin > Bergen)
        "-ven",  # reduced form of -vin (Sandven)
        "-hov",  # temple, mound (< ON hof; Gildeskålhov)
        "-tun",  # farmyard (< ON tún; Barkåstun)
        "-aker",  # field (< ON akr; Ullensaker)
        "-ås",  # hill, ridge
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "heim": "home, settlement (< ON heimr)",
        "stad": "place, farmstead (< ON staðr)",
        "rud": "clearing (< ON ruð; very common in Østlandet)",
        "rød": "clearing (< ON ruð; Vestfold/southern form)",
        "set": "seat, dwelling (< ON setr)",
        "seter": "mountain pasture farm (< ON setr/sætr)",
        "bøl": "farm, settlement (< ON bólstaðr)",
        "vik": "bay, inlet (< ON vík)",
        "fjord": "fjord, long inlet (< ON fjǫrðr)",
        "nes": "headland, promontory (< ON nes)",
        "øy": "island (< ON ey)",
        "dal": "valley (< ON dalr)",
        "berg": "mountain, rock (< ON berg)",
        "ås": "ridge, hill (< ON áss)",
        "voll": "field, meadow (< ON vǫllr)",
        "land": "land, large estate (< ON land)",
        "gård": "farm, enclosure (< ON garðr)",
        "by": "town, settlement (< ON býr/bœr)",
        "elv": "river (< ON elfr)",
        "bekk": "stream, brook (< ON bekkr)",
        "vann": "lake, water (< ON vatn)",
        "foss": "waterfall (< ON fors/foss)",
        "mo": "sandy heath (< ON mór)",
        "vin": "meadow (< ON vin; pre-Viking stratum)",
        "hov": "pagan temple (< ON hof)",
        "tun": "farmyard, enclosed area (< ON tún)",
        "aker": "cultivated field (< ON akr)",
        "stor": "great, big (< ON stórr)",
        "lille": "little, small (< ON lítill)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Norwegian toponym into components."""
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
                        confidence=0.7,
                        notes=(f"Norwegian: '{stem}' + '-{suffix}' ({meaning})"),
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
                        confidence=0.65,
                        notes=(f"Norwegian prefix '{prefix}' ({meaning}) + '{remainder}'"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Norwegian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Distinctly Norwegian suffixes
        norw_suffixes = [
            "heim",
            "rud",
            "rød",
            "seter",
            "bøl",
            "fjord",
            "foss",
            "bekk",
            "tjern",
            "vann",
            "vatn",
        ]
        for suf in norw_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Norwegian suffix '-{suf}'")
                score += 0.5
                break

        # Norwegian-specific orthography (ø, å)
        if "ø" in form_lower or "å" in form_lower:
            evidence.append("Norwegian orthography (ø/å)")
            score += 0.2

        # Definiteness suffix (common in Norwegian place-names)
        if form_lower.endswith(("en", "et", "a")):
            # Check for definite article suffix pattern
            for base in ["dalen", "vika", "berget", "fjellet", "elva"]:
                if form_lower.endswith(base):
                    evidence.append(f"Norwegian definite form '-{base}'")
                    score += 0.3
                    break

        # Common Norwegian generic elements
        generics = ["gård", "gard", "ås", "dal", "nes", "vik"]
        for gen in generics:
            if gen in form_lower:
                evidence.append(f"Norwegian generic element '{gen}'")
                score += 0.3
                break

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Norwegian etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.6,
                        notes=(f"Norwegian element '{element}' in '{form}'"),
                    )
                )

        return candidates
