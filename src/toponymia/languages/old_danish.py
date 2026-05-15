"""Old Danish language module for toponymic analysis.

Old Danish (gammel dansk, c. 800–1500 CE) created the distinctive
Danish place-name stratigraphy that reveals settlement chronology:

Oldest layer (pre-Viking / early Viking):
- -inge names (tribal/group association: Helsinge, Roskilde < Hroars Kilde)
- -løse names (meadow/clearing: Kirkeløse, Slagelse < *Slagheløse)
- -lev names (inheritance/estate: Herlev, Ølstykke < -lev)

Viking Age layer:
- -by (settlement: Roskildeby → Roskilde)
- -torp (outlying farm: Brøndby Østertorp)
- -toft (homestead plot: Maglekildtoft)

Medieval layer:
- -rup (< þorp: Glostrup, Ishøj → -rup)
- -strup (< staðr+þorp: Ålstrup)
- -drup

Sound changes from Old Norse to Old Danish:
- ON ey > Dan. ø (Hovedøya → Hovedø)
- ON steinn > Dan. sten
- ON þ > Dan. t (early) then lost
- Stød development (glottal stop) doesn't appear in writing

Key references:
- Hald 1965 "Vore Stednavne" (authoritative Danish name history)
- Jørgensen 2008 "Stednavneordbog" (place-name dictionary)
- Kousgård Sørensen 1958 "Danske bebyggelsesnavne på -sted"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldDanishModule(BaseLanguageModule):
    """Language module for Old Danish toponyms."""

    language_code = "odk"  # No standard ISO; using conventional
    language_name = "Old Danish"
    family = "Indo-European"
    branch = "Germanic > North Germanic > East Scandinavian > Old Danish"
    period = "800–1500 CE"
    script = "Latn (runic in earliest period)"

    prefixes = [
        "Stor-",  # great (Storebælt)
        "Lille-",  # small (Lillebælt)
        "Vester-",  # west (Vestervig)
        "Øster-",  # east (Østerbro)
        "Nørre-",  # north (Nørrebro, Nørresundby)
        "Sønder-",  # south (Sønderjylland)
        "Gammel-",  # old (Gammelstrup)
        "Ny-",  # new (Nyborg, Nykøbing)
    ]

    suffixes = [
        # Oldest stratum (pre-Viking)
        "-inge",  # group/people (Helsinge, Ølstykke < *-inge)
        "-løse",  # meadow, clearing (Kirkeløse, Slagelse)
        "-lev",  # inheritance, estate (Herlev, Tårnby < *-lev?)
        # Viking Age
        "-by",  # settlement (Roskilde-by, Helsingby > Helsingør)
        "-torp",  # outlying farm (Brøndby Østertorp)
        "-toft",  # homestead site (Maglekildtoft)
        # Medieval developments
        "-rup",  # < þorp (Glostrup, Ishøj-rup)
        "-strup",  # < staðr+þorp (Ålstrup)
        "-drup",  # variant of -trup/-þorp
        "-sted",  # place (< ON staðr; Hillerød < *-sted?)
        "-ager",  # field (< ON akr; Holbæksager)
        "-bæk",  # stream (< ON bekkr; Holbæk)
        "-borg",  # fortification (< ON borg; Nyborg)
        "-bro",  # bridge (Nørrebro, Østerbro)
        "-gård",  # farm (< ON garðr; Helsingørgård)
        "-havn",  # harbour (< ON hǫfn; København)
        "-holm",  # islet (< ON holmr; Bornholm)
        "-høj",  # mound (< ON haugr; Ishøj)
        "-kilde",  # spring (< ON kelda; Roskilde)
        "-købing",  # market town (< ON kaupangr; Nykøbing)
        "-lund",  # grove (< ON lundr; Brøndbylund)
        "-mark",  # field, borderland (< ON mǫrk; Danmark)
        "-skov",  # forest (< ON skógr; Gribskov)
        "-sø",  # lake (< ON sær; Tissø)
        "-ø",  # island (< ON ey; Falsterø > Falster)
        "-å",  # river (< ON á; Gudenå)
        "-vig",  # bay (< ON vík; Kolding-vig)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "inge": "group, people (oldest Danish name type; tribal)",
        "løse": "meadow, pig-pasture (Pre-Viking; very archaic)",
        "lev": "inheritance, estate (Pre-Viking personal+lev compounds)",
        "by": "settlement, village (Viking Age; most productive type)",
        "torp": "outlying farm, secondary settlement (Viking Age)",
        "toft": "homestead plot, building site (Viking Age)",
        "rup": "village (< þorp; reduced medieval form)",
        "strup": "place-farm (< staðr+þorp compound)",
        "sted": "place, site (< ON staðr)",
        "bæk": "stream, brook (< ON bekkr)",
        "borg": "fortification, castle (< ON borg)",
        "havn": "harbour, port (< ON hǫfn)",
        "holm": "islet, small island (< ON holmr)",
        "høj": "mound, burial mound (< ON haugr)",
        "kilde": "spring, well (< ON kelda)",
        "købing": "market town (< ON kaupangr 'trading place')",
        "lund": "sacred grove (< ON lundr)",
        "mark": "field, borderland (< ON mǫrk; cf. Dan-mark)",
        "skov": "forest (< ON skógr)",
        "sø": "lake (< ON sær)",
        "å": "river (< ON á)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Danish toponym into components."""
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
                            confidence=0.7,
                        ),
                        SegmentationResult(
                            component=suffix, position=1, morph_type="compound_head", confidence=0.7
                        ),
                    ]
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.6
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.6
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Old Danish."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Distinctly Danish archaic suffixes (chronological markers)
        archaic = {"inge": 0.6, "løse": 0.7, "lev": 0.65}
        for suf, weight in archaic.items():
            if form_lower.endswith(suf):
                evidence.append(f"Archaic Old Danish suffix '-{suf}' (pre-Viking)")
                score += weight
                break

        # Danish-specific medieval reductions
        danish_reductions = ["rup", "strup", "drup"]
        for suf in danish_reductions:
            if form_lower.endswith(suf):
                evidence.append(f"Danish -þorp reduction '-{suf}' (medieval)")
                score += 0.55
                break

        # Danish orthographic markers (ø, å, æ without Norwegian context)
        if "ø" in form_lower or "å" in form_lower:
            evidence.append("Scandinavian orthography (ø/å)")
            score += 0.1

        # Danish-specific elements
        danish_elements = ["købing", "kilde", "høj", "skov", "havn"]
        for elem in danish_elements:
            if elem in form_lower:
                evidence.append(f"Danish element '{elem}'")
                score += 0.4
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Old Danish etymologies for a toponym."""
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
                        confidence=0.6,
                    )
                )

        return candidates
