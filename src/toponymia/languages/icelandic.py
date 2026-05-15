"""Icelandic language module for toponymic analysis.

Icelandic (íslenska) is uniquely conservative among Nordic languages,
preserving Old Norse morphology and phonology to a remarkable degree.
Settlement naming in Iceland (landnám, 870–930 CE) represents the
purest continuation of Norse naming practices:

Key characteristics:
- Landnám names directly from ON: descriptive landscape terms
- No substrate layer (Iceland was uninhabited; debated Irish monks)
- Highly productive compound system (still active)
- Preserved inflectional system affects name forms (nominative/dative)
- No foreign administrative overlay (unlike Norway, Denmark, Sweden)

Distinctive Icelandic name types:
- Farm names (-staðir, -bólstaðr/-ból, -kot, -sel)
- Geographic features (-jökull, -hraun, -sandur, -vatn)
- Hot spring names (-laug, -hverir, -reykir)
- Volcanic features unique to Iceland (-eldfjall, -gígur)

Case forms in names:
- Nominative: Akureyri (akr 'field' + eyri 'gravel bank')
- Dative: í Reykjavík (locative)
- Genitive: Þingvallavatn (Þingvalla- genitive plural)

Key references:
- Sveinbjarnardóttir 1992 "Farm Abandonment in Medieval Iceland"
- Landnámabók (Book of Settlements, 12th–13th century)
- ÍSLEX (Icelandic place-name lexicon)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class IcelandicModule(BaseLanguageModule):
    """Language module for Icelandic toponyms."""

    language_code = "isl"  # ISO 639-3
    language_name = "Icelandic"
    family = "Indo-European"
    branch = "Germanic > North Germanic > West Scandinavian > Icelandic"
    period = "870 CE–present (landnám naming onwards)"
    script = "Latn"

    prefixes = [
        "Reyk-",  # smoke/steam (Reykjavík, Reykjanes)
        "Ís-",  # ice (Ísafjörður)
        "Vest-",  # west (Vestmannaeyjar, Vestfirðir)
        "Norð-",  # north (Norðurá)
        "Suð-",  # south (Suðurnes)
        "Aust-",  # east (Austfirðir)
        "Eyja-",  # island (Eyjafjallajökull)
        "Hvíta-",  # white (Hvítá, Hvítárvellir)
        "Svart-",  # black (Svartifoss, Svartsengi)
        "Breiða-",  # broad (Breiðafjörður)
        "Langa-",  # long (Langanes)
        "Þing-",  # assembly (Þingvellir, Þingeyjarsýsla)
    ]

    suffixes = [
        # Settlement types
        "-staðir",  # farm/stead (plural; Borgarstaðir)
        "-staður",  # farm/stead (singular; Kirkjustaður)
        "-bólstaður",  # farm (< ON bólstaðr)
        "-ból",  # farm (shortened; Helguból)
        "-kot",  # cottage, small farm (Bæjarkot)
        "-sel",  # mountain hut/shieling (Laugarsel)
        "-bær",  # farm (< ON bœr/býr; Kirkjubæjarklaustur)
        "-hús",  # house (Hólar < *hús)
        # Geographic features
        "-fjörður",  # fjord (Ísafjörður, Hvalfjörður)
        "-jökull",  # glacier (Vatnajökull, Eyjafjallajökull)
        "-vatn",  # lake (Þingvallavatn, Mývatn)
        "-á",  # river (Hvítá, Þjórsá, Ölfusá)
        "-foss",  # waterfall (Gullfoss, Dettifoss)
        "-nes",  # headland (Reykjanes, Langanes)
        "-ey",  # island (Heimaey, Flatey)
        "-eyjar",  # islands (plural; Vestmannaeyjar)
        "-dalur",  # valley (Borgardalur, Öxnadalur)
        "-vík",  # bay (Reykjavík, Húsavík)
        "-hraun",  # lava field (Eldhraun, Hallmundarhraun)
        "-sandur",  # sand plain (Skeiðarársandur)
        "-fell",  # mountain (Esja, Snæfell)
        "-fjall",  # mountain (Eyjafjallajökull)
        "-vellir",  # plains (Þingvellir, Hvítárvellir)
        "-höfn",  # harbour (Höfn, Djúpivogur-höfn)
        # Geothermal (unique to Icelandic naming)
        "-laug",  # hot spring (Laugardalur, Laugarvatn)
        "-hverir",  # hot springs (Hveravellir, Námaskarðshverir)
        "-reykir",  # steam vents (Reykholt, Deildartunguhver)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "reyk": "smoke, steam (< ON reykr; geothermal indicator)",
        "ís": "ice (< ON íss)",
        "eyja": "island (genitive; < ON ey)",
        "hvít": "white (< ON hvítr)",
        "svart": "black (< ON svartr)",
        "breiða": "broad (< ON breiðr)",
        "þing": "assembly, parliament (< ON þing)",
        "staðir": "farm, farmstead (plural; productive type)",
        "ból": "farm, dwelling (< ON bólstaðr)",
        "fjörður": "fjord (< ON fjǫrðr)",
        "jökull": "glacier (< ON jǫkull; uniquely Icelandic in names)",
        "vatn": "lake, water (< ON vatn)",
        "á": "river (< ON á)",
        "foss": "waterfall (< ON fors/foss)",
        "nes": "headland (< ON nes)",
        "ey": "island (< ON ey)",
        "dalur": "valley (< ON dalr)",
        "vík": "bay, inlet (< ON vík)",
        "hraun": "lava field (specifically Icelandic landscape)",
        "sandur": "outwash sand plain (glacial; Icelandic geographic)",
        "fell": "mountain (< ON fjall; Icelandic form)",
        "vellir": "plains, fields (< ON vǫllr plural)",
        "laug": "hot spring, bath (< ON laug; geothermal)",
        "hverir": "hot springs (< ON hverr 'hot spring')",
        "reykir": "steam, smoke (plural; geothermal)",
        "höfn": "harbour (< ON hǫfn)",
        "holt": "stony hill, copse (< ON holt)",
        "borg": "fortress, cliff (< ON borg)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Icelandic toponym into components."""
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
                self.ELEMENT_MEANINGS.get(suffix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=stem,
                            position=0,
                            morph_type="compound_modifier",
                            confidence=0.75,
                        ),
                        SegmentationResult(
                            component=suffix,
                            position=1,
                            morph_type="compound_head",
                            confidence=0.75,
                        ),
                    ]
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                self.ELEMENT_MEANINGS.get(prefix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.7
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.7
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Icelandic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Uniquely Icelandic elements (geothermal, glacial)
        icelandic_unique = ["jökull", "hraun", "hverir", "laug", "reykir"]
        for elem in icelandic_unique:
            if elem in form_lower:
                evidence.append(f"Uniquely Icelandic element '{elem}'")
                score += 0.7
                break

        # Icelandic preserved ON morphology (þ, ð retained)
        if "þ" in form_lower or "ð" in form_lower:
            evidence.append("Preserved ON consonants (þ/ð) — Icelandic")
            score += 0.4

        # Icelandic compound suffixes
        isl_suffixes = ["fjörður", "staðir", "dalur", "vellir", "eyjar"]
        for suf in isl_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Icelandic suffix '-{suf}'")
                score += 0.5
                break

        # Icelandic genitive compounds (common pattern)
        if "ar" in form_lower and len(form_lower) > 8:
            # Genitive -ar- linking element is very Icelandic
            evidence.append("Possible genitive linking -ar- (Icelandic)")
            score += 0.1

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Icelandic etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form = components[0].component if components else ""
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        lemma=f"*{element}",
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.65,
                    )
                )

        return candidates
