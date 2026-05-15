"""Cuman-Kipchak language module for toponymic analysis.

Cuman-Kipchak (Qıpçaq) was a major Turkic language of the Eurasian steppe
that left extensive toponymic traces across Eastern/Central Europe:
- Cumans dominated the Pontic steppe (11th-13th century)
- Massive Cuman settlement in Hungary after Mongol invasion (Kunság region)
- Cuman/Kipchak substrate in Romania (Wallachia, Moldavia)
- Kipchak elements in Ukrainian, Bulgarian, and Russian place-names
- Connection to Norse studies: Varangians encountered predecessors on the
  same steppe routes; later Norse references to steppe peoples
- Codex Cumanicus (1303) preserves Cuman vocabulary

Cuman toponymic traces in Europe:
- Hungarian Kunság (Kun = Cuman): Kunszentmiklós, Kiskunhalas
- Romanian: many river/settlement names of Turkic origin
- Bulgarian: Cuman personal names in -man, -bey compounds

Key references:
- Németh 1940 "Die Inschriften des Schatzes von Nagyszentmiklós"
- Rasovskij 1927 "Polovcy (Cumans)"
- Golden 1992 "An Introduction to the History of the Turkic Peoples"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CumanKipchakModule(BaseLanguageModule):
    """Language module for Cuman-Kipchak toponyms."""

    language_code = "qwm"  # ISO 639-3 for Cuman
    language_name = "Cuman-Kipchak"
    family = "Turkic"
    branch = "Kipchak > Cuman-Kipchak"
    period = "900–1400 CE (European presence)"
    script = "Latn (Codex Cumanicus) / Arab"

    prefixes = [
        "Kun-",  # Cuman (Hungarian ethnonym; Kunszentmiklós)
        "Kara-",  # black (shared with other Turkic; Karakum)
        "Ak-",  # white (Ak-Kerman)
        "Kyz-",  # red/girl (Kyzyl-)
        "Balyk-",  # fish (Balik → city in Turkic)
        "Kum-",  # sand (Kumanovo? debated)
        "Bay-",  # rich (Bayezid names)
        "Ulu-",  # great (Ulu Mescid)
        "Sary-",  # yellow (Sariyer)
        "Tash-",  # stone (Tashkent area)
    ]

    suffixes = [
        "-man",  # ? (personal name element; Osman, Suleiman)
        "-lyk",  # place/state of (equivalent to -lik; Kipchak area)
        "-suw",  # water (< su; steppe hydronyms)
        "-köl",  # lake (shared Turkic; Issyk-Kul)
        "-tau",  # mountain (Kipchak form; cf. Turkish dağ)
        "-bulaq",  # spring (widespread Turkic)
        "-yurt",  # camp, settlement (Mangyshlak yurts)
        "-ordu",  # camp, headquarters (> English 'horde')
        "-saray",  # palace (< Persian; Saray-Berke, Sarai)
        "-balyk",  # city (Turkic; Balasagun)
        "-kent",  # city (< Sogdian/Persian; via Turkic)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "kun": "Cuman (tribal name; Hungarian form)",
        "kara": "black (widespread Turkic)",
        "ak": "white, pure",
        "kyz": "red; also girl",
        "balyk": "fish; also city (in Turkic)",
        "kum": "sand, sandy ground",
        "bay": "rich, noble",
        "ulu": "great, senior",
        "sary": "yellow, blond",
        "tash": "stone",
        "suw": "water, river (Kipchak form of su)",
        "köl": "lake",
        "tau": "mountain (Kipchak; cf. Turk. dağ)",
        "bulaq": "spring, source",
        "yurt": "camp, dwelling, homeland",
        "ordu": "army camp, headquarters (> horde)",
        "saray": "palace (< Persian sarāy)",
        "kent": "city (< Sogdian/Persian)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Cuman-Kipchak toponym into components."""
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
                    confidence=0.75,
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
                        confidence=0.4,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.75,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.4,
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
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.75,
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
        """Classify whether a toponym is likely Cuman-Kipchak."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Hungarian Kun- (Cuman) marker
        if form_lower.startswith("kun") and len(form_lower) > 4:
            evidence.append("Hungarian Kun- (Cuman ethnic marker)")
            score += 0.45

        # Kipchak-specific suffixes
        kipchak_suffixes = ["tau", "suw", "köl", "bulaq", "yurt", "ordu"]
        for marker in kipchak_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Kipchak suffix -{marker}")
                score += 0.35
                break

        # Generic Turkic prefixes (could be Cuman in European context)
        turkic_prefixes = ["kara", "ak", "sary", "kyz"]
        for marker in turkic_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Turkic/Kipchak prefix {marker}-")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="900–1400 CE (Cuman-Kipchak)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Cuman-Kipchak components."""
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
