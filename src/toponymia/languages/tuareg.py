"""Tuareg/Tamashek language module for toponymic analysis.

Tuareg (Tamashek/Tamasheq) is a Berber language spoken by ~1.2 million people
across the Sahara (Niger, Mali, Algeria, Libya, Burkina Faso). The Tuareg
are notable for preserving the Tifinagh script tradition.

Tuareg toponymy connects to European place-name studies through:
- Trans-Saharan trade routes reaching the Mediterranean
- Saharan geographic features known in classical sources
- Tifinagh script as precursor to Libyco-Berber inscriptions
- Colonial-era mapping (French: Sahara, Hoggar, Tassili)

Characterized by:
- Prefixes: In- (people of), Tin- (feminine of), Tassili- (plateau)
- Suffixes: -n (genitive), -ene (plural)
- Consonantal root system (shared Berber)
- Extensive geographic vocabulary for desert landforms

Key references:
- de Foucauld 1951–52 "Dictionnaire touareg-français"
- Prasse et al. 2003 "Dictionnaire touareg-français"
- Lhote 1955 "Les Touaregs du Hoggar"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class TuaregModule(BaseLanguageModule):
    """Language module for Tuareg/Tamashek toponyms."""

    language_code = "taq"
    language_name = "Tuareg/Tamashek"
    family = "Afro-Asiatic"
    branch = "Berber > Tuareg"
    period = "Antiquity–present"
    script = "Tfng"  # Tifinagh

    prefixes = [
        "In-",  # people of (In Gall, In Salah)
        "Tin-",  # feminine of In- (Tindouf, Tinariwen)
        "Tassili-",  # plateau (Tassili n'Ajjer)
        "Adrar-",  # mountain (Adrar des Ifoghas)
        "Aha-",  # variant of adrar (Ahaggar)
        "Taman-",  # feminine place (Tamanrasset)
        "Agh-",  # variant fort
        "Aza-",  # place, area (Azalai)
        "Ténéré-",  # desert, void (Ténéré)
        "Tidik-",  # palm grove (Tidikelt)
        "Tad-",  # feminine prefix
    ]

    suffixes = [
        "-n",  # genitive marker (Tassili n'Ajjer)
        "-ene",  # plural (Tinariwen = deserts)
        "-et",  # feminine (Tamanrasset)
        "-elt",  # feminine diminutive (Tidikelt)
        "-ak",  # possessive/locative
        "-rar",  # place of (Ahaggar)
        "-wen",  # masculine plural
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "in": "people of, those of (masculine plural)",
        "tin": "those of (feminine plural), place of women",
        "tassili": "plateau, elevated rocky shelf",
        "adrar": "mountain, high ground",
        "aha": "mountain (variant, Ahaggar = mountains)",
        "taman": "place, land (feminine settlement)",
        "ténéré": "desert, empty expanse, void",
        "tidik": "palm grove, oasis with palms",
        "aza": "place, area, route (Azalai = salt route)",
        "tad": "feminine/diminutive prefix",
        "agh": "fortified place",
        "hoggar": "mountains (< Ahaggar, Tuareg tribal name)",
        "ajjer": "cliff, escarpment (Tassili n'Ajjer)",
        "arlit": "depression, low area",
        "tahat": "peak, summit (Mount Tahat)",
        "egharghar": "river, wadi (seasonal)",
        "erg": "sand sea, dune field",
        "reg": "stony desert, gravel plain",
        "tafassasset": "wide valley, open passage",
        "amadror": "mountain range, chain",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Tuareg toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

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

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix and matched_suffix:
            prefix_part = form[: len(matched_prefix)]
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.8,
                )
            )
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=len(results),
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        elif matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]
            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.8,
                )
            )
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="compound_modifier",
                    lemma=remainder.lower(),
                    confidence=0.5,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Tuareg in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        tuareg_prefixes = ["in", "tin", "tassili", "adrar", "aha", "taman", "ténéré"]
        for prefix in tuareg_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Tuareg prefix '{prefix}-'")
                score += 0.45
                break

        tuareg_roots = ["hoggar", "ajjer", "erg", "reg", "arlit", "tahat"]
        for root in tuareg_roots:
            if root in form_lower:
                evidence.append(f"Tuareg root '{root}'")
                score += 0.3
                break

        tuareg_suffixes = ["ene", "elt", "rar"]
        for suffix in tuareg_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Tuareg suffix '-{suffix}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Antiquity–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Tuareg components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get(lemma_key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma_key,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=[],
                        sound_changes=[],
                        sources=["de Foucauld 1951", "Prasse et al. 2003"],
                    )
                )
        return candidates
