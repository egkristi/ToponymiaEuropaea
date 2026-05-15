"""Romanian language module for toponymic analysis.

Romanian toponymy is uniquely layered, reflecting the crossroads position:
- Dacian/Thracian substrate (pre-Roman, many hydronyms)
- Latin stratum (Roman Dacia, 106-271 CE)
- Slavic superstrate (massive 6th-10th c. influence)
- Hungarian/Turkic elements (medieval Transylvania)
- Relevant for Norse studies: Varangian route passed through
  Romanian territories (Dnieper → Black Sea); rune stones
  reference travel through these lands (Blakumen = Vlachs/Romanians)

Key references:
- Iordan 1963 "Toponimia românească"
- Moldovanu 2010 "Toponimia românească"
- Brezeanu 1999 "Toponymie et onomastique de la Roumanie"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class RomanianModule(BaseLanguageModule):
    """Language module for Romanian toponyms."""

    language_code = "ron"  # ISO 639-3 for Romanian
    language_name = "Romanian"
    family = "Indo-European"
    branch = "Romance > Eastern Romance"
    period = "8th century CE – present"
    script = "Latn"

    prefixes = [
        "Piatra-",  # stone (Piatra Neamț)
        "Valea-",  # valley (Valea lui Mihai)
        "Turnu-",  # tower (Turnu Severin, Turnu Măgurele)
        "Câmpu-",  # field (Câmpulung)
        "Baia-",  # mine (Baia Mare, Baia Sprie)
        "Târgu-",  # market (Târgu Mureș, Târgu Jiu)
        "Gura-",  # mouth (Gura Humorului)
        "Alba-",  # white (Alba Iulia)
        "Satu-",  # village (Satu Mare)
        "Drobeta-",  # Dacian substrate name
    ]

    suffixes = [
        "-ești",  # settlement of (patronymic: București, Pitești)
        "-eni",  # inhabitants (Botoșeni→Botoșani)
        "-ani",  # inhabitants (Argeșani)
        "-oara",  # diminutive (Timișoara < Timiș + -oara)
        "-oaia",  # augmentative/place
        "-ava",  # Slavic river suffix (Moldova < *moldava)
        "-ița",  # diminutive (Ialomița, Dâmbovița)
        "-ova",  # Slavic possessive (Craiova < Cr. Krajova)
        "-ești",  # patronymic plural
        "-lung",  # long (Câmpulung)
        "-mare",  # great (Baia Mare, Satu Mare)
        "-mic",  # small
        "-nou",  # new (Codlea Nou)
        "-vechi",  # old
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "piatra": "stone, rock (< Lat. petra)",
        "valea": "valley (< Lat. vallis)",
        "turnu": "tower (< Lat. turris)",
        "câmpu": "field, plain (< Lat. campus)",
        "baia": "mine, bath (< Lat. *balnea or Slavic banja)",
        "târgu": "market, town (< Slavic trŭgŭ)",
        "gura": "mouth, entrance (< Lat. gula)",
        "alba": "white (< Lat. alba)",
        "satu": "village (< Lat. fossatum)",
        "ești": "patronymic settlement suffix (-ești)",
        "eni": "inhabitants of",
        "oara": "diminutive place suffix",
        "ava": "river (Slavic substrate)",
        "ița": "diminutive (river/place)",
        "ova": "possessive (Slavic origin)",
        "lung": "long (< Lat. longus)",
        "mare": "great, large (< Lat. mare/magnus)",
        "mic": "small (< Lat. *miccus)",
        "nou": "new (< Lat. novus)",
        "vechi": "old (< Lat. vetulus→veclu)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Romanian toponym into components."""
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

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix and matched_suffix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="stem",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_modifier",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.5,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="simplex",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Romanian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Romanian patronymic suffix -ești (very diagnostic)
        if form_lower.endswith(("ești", "esti")):
            evidence.append("Romanian patronymic -ești")
            score += 0.45

        rom_suffixes = ["oara", "ița", "ova", "eni", "ani"]
        for marker in rom_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 2:
                evidence.append(f"Romanian suffix -{marker}")
                score += 0.25
                break

        rom_prefixes = ["târgu", "baia", "piatra", "turnu", "câmpu"]
        for marker in rom_prefixes:
            if form_lower.startswith(marker):
                evidence.append(f"Romanian prefix {marker}-")
                score += 0.3
                break

        # Romanian diacritics
        rom_chars = ["ș", "ț", "ă", "â", "î"]
        for ch in rom_chars:
            if ch in form_lower:
                evidence.append(f"Romanian diacritic '{ch}'")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="8th century – present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Romanian components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            meaning = self.ELEMENT_MEANINGS.get(comp.lemma.lower().rstrip("-"))
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp.lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                    )
                )
        return candidates
