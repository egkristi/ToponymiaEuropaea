"""Kabyle language module for toponymic analysis.

Kabyle (Taqbaylit) is the largest Berber/Amazigh language (~5 million speakers),
spoken primarily in the Kabylia region of northern Algeria. It belongs to the
Northern Berber branch of the Afroasiatic family.

Kabyle toponymy is critical for understanding:
- Pre-Roman substrate in North African place-names
- Roman Africa toponymy often preserves Berber names (Latinized forms)
- Mediterranean connections and shared Berber-European contact toponymy
- French colonial transcriptions of Kabyle place-names

Characterized by:
- Prefixes: Ait-/Ath- (sons of), Tizi- (mountain pass/col), Igh- (fort)
- Suffixes: -en (plural/genitive), -ath (collective), -ith (feminine)
- Feminine marker t-...-t (circumfix)
- State alternation: free state vs. construct state

Key references:
- Haddadou 2012 "Dictionnaire toponymique et historique de l'Algérie"
- Pellegrin 1949 "Essai sur les noms de lieux d'Algérie et de Tunisie"
- Dallet 1982 "Dictionnaire kabyle-français"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KabyleModule(BaseLanguageModule):
    """Language module for Kabyle/Amazigh toponyms."""

    language_code = "kab"
    language_name = "Kabyle"
    family = "Afro-Asiatic"
    branch = "Berber > Northern Berber > Kabyle"
    period = "Antiquity–present (continuous habitation)"
    script = "Latn"

    prefixes = [
        "Ait-",  # sons of, clan of (Ait Menguellet)
        "Ath-",  # variant of Ait (Ath Yenni)
        "Tizi-",  # mountain pass, col (Tizi Ouzou)
        "Igh-",  # fort, fortified place (Ighil)
        "Ighil-",  # hill, ridge (Ighil Ali)
        "Tala-",  # spring, fountain (Tala Hamza)
        "Aïn-",  # spring (< Arabic borrowing, common)
        "Bou-",  # father of / place of (Bouira)
        "Tham-",  # feminine place marker
        "Azrou-",  # rock (Azrou)
        "Agouni-",  # hillside, slope (Agouni Gueghrane)
        "Thar-",  # feminine of agr- (field)
    ]

    suffixes = [
        "-en",  # plural/genitive marker (Imazighen)
        "-ath",  # collective (Ath, variant of Ait)
        "-ith",  # feminine singular
        "-an",  # adjectival/locative
        "-ou",  # adjectival (Tizi Ouzou = col of genets)
        "-iw",  # possessive
        "-ene",  # plural variant
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ait": "sons of, clan of (tribal prefix)",
        "ath": "sons of, clan of (variant of Ait)",
        "tizi": "mountain pass, col, saddle",
        "igh": "fortified place, fort",
        "ighil": "hill, ridge, promontory",
        "tala": "spring, fountain, water source",
        "azrou": "rock, boulder, rocky place",
        "agouni": "hillside, slope, terrace",
        "bou": "father of, possessor of (place with)",
        "tham": "feminine place (circumfix t-...-t)",
        "ain": "spring, water source (< Arabic ʿayn)",
        "thar": "field, cultivated land (feminine)",
        "ou": "of (genitive particle)",
        "akbou": "hill, knoll",
        "adrar": "mountain",
        "aseqif": "arch, vault, covered passage",
        "amalu": "shaded slope (north-facing)",
        "asif": "river, watercourse",
        "taourirt": "small hill, knoll (fem.)",
        "thamurth": "land, country, homeland",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kabyle toponym into components."""
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
        """Classify whether a toponym is likely Kabyle/Berber in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        kabyle_prefixes = ["ait", "ath", "tizi", "igh", "ighil", "tala", "azrou", "agouni"]
        for prefix in kabyle_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Kabyle prefix '{prefix}-'")
                score += 0.45
                break

        kabyle_roots = ["adrar", "asif", "taourirt", "thamurth", "amalu"]
        for root in kabyle_roots:
            if root in form_lower:
                evidence.append(f"Kabyle root '{root}'")
                score += 0.3
                break

        kabyle_suffixes = ["ath", "ith", "ene"]
        for suffix in kabyle_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Kabyle suffix '-{suffix}'")
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
        """Generate etymology candidates for Kabyle components."""
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
                        sources=["Haddadou 2012", "Dallet 1982"],
                    )
                )
        return candidates
