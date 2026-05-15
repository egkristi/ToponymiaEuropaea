"""Faroese language module for toponymic analysis.

Faroese (føroyskt) developed from Old Norse settlers (c. 800 CE) on the
Faroe Islands. It shows distinctive phonological developments that
differentiate Faroese place-names from Icelandic and Norwegian forms:

Key sound changes:
- ON á > Faroese ó (ON stað-r > Far. staður but á > ó in names)
- ON au > Faroese ey (ON haugr > Far. heyggjur/heyggur)
- Skerping (vowel breaking): e > ea, o > oa before certain consonants
- ON þ retained (as in Icelandic)
- Glide insertion: ON dalr > Far. dalur (as Icelandic)

Faroese-specific name patterns:
- Farm names (býlingur): -bøur (< ON bœr), -garður, -staður
- Coastal features: -vík, -vágur (< ON vágr 'bay'), -nes
- Bird-cliff names (unique ecological naming)
- -oyggj (island; < ON ey with Faroese development)

The 18 islands have names from original settlement:
- Streymoy (< ON Straumøy 'current-island')
- Eysturoy (< ON Eystrey 'eastern island')
- Vágar (< ON Vágøyar 'bay islands')
- Borðoy (< ON Borðey 'edge island')

Key references:
- Matras 1932 "Stednavne paa de Færøske Øer"
- Jacobsen & Matras 1961 "Føroysk-donsk orðabók"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class FaroeseModule(BaseLanguageModule):
    """Language module for Faroese toponyms."""

    language_code = "fao"  # ISO 639-3
    language_name = "Faroese"
    family = "Indo-European"
    branch = "Germanic > North Germanic > West Scandinavian > Faroese"
    period = "800 CE–present (Norse settlement of Faroes)"
    script = "Latn"

    prefixes = [
        "Nor-",  # north (Norðoyar = northern islands)
        "Su-",  # south (Suðuroy = southern island)
        "Ey-",  # island (Eysturoy = eastern island)
        "Stór-",  # great, big (Stóra Dímun)
        "Lítla-",  # little (Lítla Dímun)
        "Mykla-",  # great (Mykines < ON mikill)
        "Sand-",  # sand (Sandoy, Sandavágur)
        "Hvít-",  # white (Hvítanes)
        "Svart-",  # black (Svartifossur)
    ]

    suffixes = [
        # Island/coastal
        "-oyggj",  # island (< ON ey; Faroese development)
        "-oy",  # island (older spelling; Streymoy)
        "-vágur",  # bay (< ON vágr; Sandavágur, Miðvágur)
        "-vík",  # bay, inlet (< ON vík; Fuglavík)
        "-nes",  # headland (< ON nes; Hvítanes)
        "-fjørður",  # fjord (< ON fjǫrðr; Trongisvágsfjørður)
        "-hólmur",  # islet (< ON holmr; Nólsoy < *hólmur)
        # Settlement
        "-bøur",  # farm (< ON bœr; Hvalba < *Hvalbøur)
        "-garður",  # enclosure (< ON garðr; Miðgarður)
        "-staður",  # place (< ON staðr; Fuglastaður)
        "-bólstaður",  # farm (< ON bólstaðr)
        "-býlingur",  # settlement group
        # Landscape
        "-dalur",  # valley (< ON dalr; Kvívíksdalur)
        "-fell",  # mountain (< ON fjall; Slættaratindur)
        "-fossur",  # waterfall (< ON fors; Bøsdalafossur)
        "-vatn",  # lake (< ON vatn; Sørvágsvatn)
        "-á",  # river (< ON á; Stórá)
        "-heyggjur",  # mound (< ON haugr; Faroese form)
        "-sandur",  # sand, beach (Sandur)
        "-gjógv",  # gorge, cleft (Gjógv; Faroese-specific)
        # Bird/ecological (unique to Faroe Islands naming)
        "-fugl-",  # bird (Fuglafjørður, Fuglavík)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "oyggj": "island (< ON ey; Faroese -oyggj/-oy)",
        "vágur": "bay, inlet (< ON vágr; more common than -vík)",
        "vík": "bay, inlet (< ON vík)",
        "nes": "headland, cape (< ON nes)",
        "fjørður": "fjord (< ON fjǫrðr)",
        "bøur": "farm, settlement (< ON bœr)",
        "garður": "enclosure, farm (< ON garðr)",
        "staður": "place (< ON staðr)",
        "dalur": "valley (< ON dalr)",
        "fell": "mountain (< ON fjall)",
        "fossur": "waterfall (< ON fors)",
        "vatn": "lake (< ON vatn)",
        "á": "river (< ON á)",
        "heyggjur": "mound, cairn (< ON haugr; Faroese skerping)",
        "sandur": "sand, sandy beach",
        "gjógv": "gorge, narrow cleft (Faroese-specific term)",
        "streym": "current, stream (< ON straumr; Streymoy)",
        "stór": "great, big (< ON stórr)",
        "lítla": "little, small (< ON lítill; Faroese form)",
        "fugl": "bird (< ON fugl; bird-cliff naming)",
        "nólsoy": "Nólsoy island (meaning debated)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Faroese toponym into components."""
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
                self.ELEMENT_MEANINGS.get(prefix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.65
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.65
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Faroese."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Distinctly Faroese elements
        faroese_unique = ["vágur", "gjógv", "oyggj", "heyggjur", "bøur"]
        for elem in faroese_unique:
            if elem in form_lower:
                evidence.append(f"Distinctly Faroese element '{elem}'")
                score += 0.7
                break

        # Faroese phonology: ð retained, oy- patterns
        if "ð" in form_lower:
            evidence.append("Retained ð (West Scandinavian; Faroese/Icelandic)")
            score += 0.2

        # Faroese suffixes
        far_suffixes = ["fjørður", "dalur", "fossur", "staður"]
        for suf in far_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Faroese/Icelandic suffix '-{suf}'")
                score += 0.4
                break

        # Faroese skerping (vowel breaking): ea, oa patterns
        if "ea" in form_lower or "oa" in form_lower:
            evidence.append("Faroese skerping (vowel breaking: ea/oa)")
            score += 0.25

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Faroese etymologies for a toponym."""
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
