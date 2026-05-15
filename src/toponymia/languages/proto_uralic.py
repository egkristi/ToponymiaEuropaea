"""Proto-Uralic substrate module for toponymic analysis.

A pre-Sami, pre-Finnic Uralic substrate layer exists in Scandinavian
place-names, particularly hydronyms (river/lake names). This represents
some of the OLDEST recoverable naming layers in Northern Europe:

Evidence for Proto-Uralic substrate in Scandinavia:
- River names that resist Indo-European (Germanic/Celtic) etymology
- Hydronyms with parallels in Uralic languages across northern Eurasia
- Distribution matches areas of known pre-Germanic habitation
- Some -jokk/-jakk river names in non-Sami areas may be older
  than Sami expansion (or represent early Uralic settlement)

Norwegian/Swedish substrate examples (debated):
- Names with unexplained -ma, -va, -ja endings
- Lake names that match Finno-Ugric patterns but aren't clearly Sami
- Some älv/elv river names may have pre-Germanic Uralic substrate
- Connection to "Arctic" or "Paleo-European" naming layers

This is relevant for the Mongolian connection:
- Uralic languages are part of a broader Northern Eurasian language
  zone with possible deep-time connections to Altaic/Mongolic
  (controversial "Ural-Altaic" hypothesis, now mostly rejected but
  substrate contacts are real)
- The Sami and their linguistic ancestors came from the east
- Some "unexplained" Scandinavian names may trace to very early
  Uralic-speaking populations

Key references:
- Aikio 2004 "An essay on substrate studies and the origin of Saami"
- Saarikivi 2004 "Is there Palaeo-European substratum interference
  in western branches of Uralic?"
- Koivulehto 1991 "Uralische Evidenz für die Laryngaltheorie"
- Sammallahti 1998 "The Saami Languages: An Introduction"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ProtoUralicModule(BaseLanguageModule):
    """Language module for Proto-Uralic substrate toponyms in Europe."""

    language_code = "urj"  # ISO 639-5 Uralic (family code)
    language_name = "Proto-Uralic substrate"
    family = "Uralic"
    branch = "Pre-Sami / Proto-Uralic (substrate layer)"
    period = "~3000 BCE – 500 CE (pre-Germanic substrate in Scandinavia)"
    script = "None (reconstructed from comparative linguistics)"

    prefixes = [
        "Jokk-",  # river (Uralic *jokka; > Sami johka, Finnish joki)
        "Jäv-",  # lake (Uralic *jäwrä; > Finnish järvi, Sami jávri)
        "Num-",  # sky, god (Uralic *numa; > Nenets Num)
        "Kol-",  # fish (Uralic *kala; > Finnish kala)
        "Vu-",  # water (Uralic *wete; > Finnish vesi, Komi va)
        "Sar-",  # stream? (possible Uralic substrate)
        "Suo-",  # swamp (Finnish suo; > substrate in Sweden)
    ]

    suffixes = [
        "-jokk",  # river (widespread in northern Scandinavia)
        "-jávri",  # lake (Sami form; older substrate has variants)
        "-järvi",  # lake (Finnish form)
        "-ma",  # land, earth (Uralic *maa; > Finnish maa, Sami meahcci)
        "-va",  # water (Uralic substrate; cf. Komi va 'water')
        "-ja",  # river (pre-Sami substrate in Scandinavia)
        "-njarga",  # cape, headland (Sami form; widespread)
        "-vuotna",  # fjord (Sami; used in names across northern Norway)
        "-luokta",  # bay (Sami; substrate in coastal names)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "jokk": "river (Uralic *jokka; Sami johka; Finnish joki)",
        "jávri": "lake (Sami form of Uralic *jäwrä)",
        "järvi": "lake (Finnish form of Uralic *jäwrä)",
        "maa": "land, earth (Uralic *maa; very widespread)",
        "vesi": "water (Uralic *wete; Finnish vesi > ve-/va- in names)",
        "kala": "fish (Uralic *kala; Finnish kala)",
        "suo": "swamp, bog (Finnish; widespread in Swedish substrate)",
        "numa": "sky, heaven, god (Uralic *numa; > Nenets Num)",
        "njarga": "cape, headland (Sami; < Proto-Uralic *ńarki?)",
        "vuotna": "fjord (Sami; cf. Norwegian -fjord replacements)",
        "luokta": "bay, inlet (Sami; < *lukta)",
        "suolo": "island (Sami; < Uralic *sala 'branch/island')",
        "oaivi": "head, mountain top (Sami; < Uralic *ojwa)",
        "čáhci": "water (Sami; older substrate form)",
        "ála": "upper? (pre-Sami substrate in Ål-, Al- names?)",
        "sar": "stream, flow (possible substrate; cf. Finnish sara 'sedge')",
    }

    # Known substrate hydronym patterns in Scandinavia
    SUBSTRATE_PATTERNS: dict[str, str] = {
        "älv": "river (Sw.; from ON elfr, but some may replace Uralic substrate)",
        "träsk": "lake (Sw. northern; possibly calque of Uralic substrate)",
        "tjärn": "tarn, small lake (Sw./No.; cf. Sami čearru?)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment potential Proto-Uralic substrate toponyms."""
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
                        confidence=0.5,
                        notes=(f"Uralic substrate: '{stem}' + '-{suffix}' ({meaning})"),
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
                        confidence=0.45,
                        notes=(f"Proto-Uralic prefix '{prefix}' ({meaning}) + '{remainder}'"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form may have Proto-Uralic substrate origins."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Sami-type elements (indicating Uralic layer)
        sami_elements = [
            "jokk",
            "jávri",
            "njarga",
            "vuotna",
            "luokta",
            "suolo",
            "oaivi",
            "čáhci",
        ]
        for elem in sami_elements:
            if elem in form_lower:
                evidence.append(f"Sami/Uralic geographic element '{elem}'")
                score += 0.6
                break

        # Finnish-type elements in Scandinavian context
        finnish_elements = ["järvi", "joki", "maa", "suo", "kala"]
        for elem in finnish_elements:
            if elem in form_lower:
                evidence.append(f"Finnic element '{elem}' (possible substrate)")
                score += 0.4
                break

        # Unexplained -va, -ma, -ja endings (possible substrate markers)
        substrate_endings = ("va", "ma", "ja")
        if (
            form_lower.endswith(substrate_endings)
            and len(form_lower) >= 4
            and not any(form_lower.endswith(germ) for germ in ["heim", "stad", "land", "vik"])
        ):
            evidence.append(f"Ending '-{form_lower[-2:]}' (possible Uralic substrate marker)")
            score += 0.2

        # Names starting with typical Uralic phonology
        # (lacking initial consonant clusters, open syllables)
        if form_lower.startswith(("ala", "yla", "oulu", "iva", "ova")):
            evidence.append("Open-syllable initial (Uralic phonotactics)")
            score += 0.15

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Proto-Uralic substrate etymologies."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.4,
                        notes=(
                            f"Proto-Uralic substrate element '{element}' "
                            f"in '{form}'. This represents a pre-Germanic/"
                            "pre-Sami naming layer in Northern Europe."
                        ),
                    )
                )

        return candidates
