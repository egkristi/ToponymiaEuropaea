"""Old Swedish language module for toponymic analysis.

Old Swedish (fornsvenska, c. 800–1526 CE) created distinctive
Swedish place-name strata that reveal settlement history:

Key chronological layers:
- Pre-Viking: -tuna names (central/cult places: Sigtuna, Eskilstuna)
- Viking Age: -by, -sta (< staðir), -böle (< bólstaðr)
- Medieval: -ås (ridge), -skog (forest), -ö (island)

Old Swedish-specific developments:
- ON ey > OSw. ö (> Sw. ö: Björkö, Vaxö > Växjö)
- ON steinn > OSw. sten (Steninge)
- ON haugr > OSw. hög (Hög, Kungshögen)
- ON vík > OSw. vik (Bergsvik)
- Apocope: final -r drops (ON staðir > OSw. sta: Bromma < *-sta)

Distinctive Swedish name types:
- -tuna: ancient central places (only in Sweden; Sigtuna, Eskilstuna)
- -sala: hall, large estate (Uppsala < *Upp-sala 'upper hall')
- -inge: group association (Kungsängen < -inge, Enköping)
- -åker: cultivated field (Linköping < -aker)
- -ön: the island (definite form)

Key references:
- Hellquist 1903-06 "Studier öfver de svenska sjönamnen"
- SOL (Svenskt Ortnamnslexikon) 2003
- Andersson 1965 "Bebyggelsenamnen"
- Stahre 1986 "Ortnamn i Stockholms län"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldSwedishModule(BaseLanguageModule):
    """Language module for Old Swedish toponyms."""

    language_code = "osw"  # Conventional code
    language_name = "Old Swedish"
    family = "Indo-European"
    branch = "Germanic > North Germanic > East Scandinavian > Old Swedish"
    period = "800–1526 CE"
    script = "Latn (runic in earliest period)"

    prefixes = [
        "Stor-",  # great (Storvreta, Storsjön)
        "Lill-",  # small (Lillån)
        "Norr-",  # north (Norrköping, Norrtälje)
        "Söder-",  # south (Söderköping, Södertälje)
        "Öster-",  # east (Östermalm, Östersund)
        "Väster-",  # west (Västerås, Västerbotten)
        "Ny-",  # new (Nyköping)
        "Gamla-",  # old (Gamla Uppsala)
        "Kungs-",  # king's (Kungälv, Kungsör)
    ]

    suffixes = [
        # Oldest stratum (pre-Viking, unique to Sweden)
        "-tuna",  # central place/cult site (Sigtuna, Eskilstuna)
        "-sala",  # hall, estate (Uppsala, Vaksala)
        "-inge",  # group/people (Enköping < *Enikoping + -inge)
        # Viking Age
        "-by",  # settlement (Visby, Norrtäljeby)
        "-sta",  # place (< ON staðir; Bromma < *Brunnsta)
        "-böle",  # farm (< ON bólstaðr; Bollnäs < Böle-näs)
        "-torp",  # outlying farm (Biskopstorp)
        "-bo",  # dwelling (< ON bú; Dalby < Dalabo)
        # Common elements
        "-köping",  # market town (< ON kaupangr; Nyköping, Linköping)
        "-borg",  # fortification (Göteborg, Mariefred-borg)
        "-holm",  # islet (Stockholm, Katrineholm)
        "-ö",  # island (< ON ey; Björkö, Värmdö)
        "-ön",  # the island (definite; Lidingön)
        "-ås",  # ridge (< ON áss; Västerås)
        "-äng",  # meadow (< ON eng; Kungsängen)
        "-skog",  # forest (< ON skógr; Rättvik < -skog)
        "-sjö",  # lake (< ON sær/sjór; Storsjön)
        "-å",  # river (< ON á; Ljusnan < *ljós-á)
        "-berg",  # mountain (Malmberget)
        "-bro",  # bridge (Örebro, Lindesberg)
        "-dal",  # valley (< ON dalr; Bohusdal)
        "-fors",  # rapids (Luleå < *Lule-fors?)
        "-hamn",  # harbour (< ON hǫfn; Stockholms hamn)
        "-hult",  # copse, wood (Halmstad < -hult area)
        "-löv",  # inheritance (< ON -leif; Eslöv, Dalslöv)
        "-näs",  # headland (< ON nes; Bollnäs, Sigtunäs)
        "-vik",  # bay (< ON vík; Bergsvik)
        "-åker",  # field (< ON akr; Linderåker)
        "-hed",  # heath (Stockshed)
        "-hög",  # mound (< ON haugr; Kungshögen)
        "-lund",  # grove (< ON lundr; Helgelund)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "tuna": "central place, cult site (UNIQUE to Sweden; high status)",
        "sala": "hall, great house (< ON salr; Uppsala = 'upper hall')",
        "inge": "group, people (tribal association; very archaic)",
        "by": "settlement, village (< ON býr/bœr)",
        "sta": "place (< ON staðir; reduced Swedish form)",
        "böle": "farm, dwelling (< ON bólstaðr; Norrland form)",
        "torp": "outlying farm, secondary settlement",
        "köping": "market town (< ON kaupangr 'trading place')",
        "borg": "fortification, castle (< ON borg)",
        "holm": "islet, small island (< ON holmr)",
        "ö": "island (< ON ey)",
        "ås": "ridge, esker (< ON áss; Västerås = 'western ridge')",
        "äng": "meadow, water-meadow (< ON eng)",
        "skog": "forest (< ON skógr)",
        "sjö": "lake (< ON sær; Swedish-specific form)",
        "å": "river (< ON á)",
        "berg": "mountain, rock (< ON berg)",
        "dal": "valley (< ON dalr)",
        "fors": "rapids, waterfall (< ON fors)",
        "näs": "headland, cape (< ON nes; Swedish form with -ä-)",
        "vik": "bay, inlet (< ON vík)",
        "åker": "cultivated field (< ON akr)",
        "hög": "mound, burial mound (< ON haugr)",
        "lund": "sacred grove (< ON lundr)",
        "löv": "inheritance (< ON -leif; South Swedish)",
        "hult": "copse, small wood (West Swedish)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Swedish toponym into components."""
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
                        notes=(f"Old Swedish: '{stem}' + '-{suffix}' ({meaning})"),
                    )
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                results.append(
                    SegmentationResult(
                        segments=[prefix, remainder],
                        language=self.language_code,
                        confidence=0.6,
                        notes=(f"Old Swedish prefix '{prefix}' + '{remainder}'"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Old Swedish."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Uniquely Swedish archaic types
        if form_lower.endswith("tuna"):
            evidence.append("Swedish -tuna suffix (unique pre-Viking central place type)")
            score += 0.8

        if form_lower.endswith("sala"):
            evidence.append("Swedish -sala suffix (hall/estate; cf. Uppsala)")
            score += 0.7

        # Swedish-specific suffixes
        swedish_suffixes = ["köping", "sjö", "näs", "böle", "löv", "hult"]
        for suf in swedish_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Swedish suffix '-{suf}'")
                score += 0.5
                break

        # Swedish orthographic markers (ö, ä, å)
        if "ö" in form_lower or "ä" in form_lower:
            evidence.append("Swedish orthography (ö/ä)")
            score += 0.15

        # Reduced -sta form (Swedish apocope of -staðir)
        if form_lower.endswith("sta") and len(form_lower) >= 5:
            evidence.append("Swedish reduced -sta (< ON staðir; apocope)")
            score += 0.4

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Old Swedish etymologies for a toponym."""
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
                        notes=(f"Old Swedish element '{element}' in '{form}'"),
                    )
                )

        return candidates
