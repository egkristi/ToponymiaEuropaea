"""Punic language module for toponymic analysis.

Punic is the Western Phoenician (Canaanite/Semitic) language of the Carthaginian
colonies in the Western Mediterranean (814 BCE – 7th c. CE). It is CRITICAL for
Western Mediterranean toponymy, leaving deep traces in Iberia, Sicily, Sardinia,
and Malta.

Major European toponymic impact:
- Carthage (qart-ḥadašt = new city)
- Cadiz (gadir = wall, enclosure)
- Cartagena (qart-ḥadašt, "New Carthage")
- Ibiza (ʾybšm = island of Bes)
- Malta (mlt = refuge, shelter)
- Sardinian and Sicilian coastal names

Characterized by:
- qart- (city): Carthage, Cartagena, Cirta
- gadir (wall/enclosure): Cadiz, Agadir
- -im (masculine plural): Motya (mtw'ym)
- Theophoric: Baal, Melqart, Tanit, Eshmun

Key references:
- Krahmalkov 2000 "Phoenician-Punic Dictionary"
- Lipiński 2004 "Itineraria Phoenicia"
- Benz 1972 "Personal Names in the Phoenician and Punic Inscriptions"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PunicModule(BaseLanguageModule):
    """Language module for Punic/Western Phoenician toponyms."""

    language_code = "xpu"
    language_name = "Punic"
    family = "Afro-Asiatic"
    branch = "Semitic > Northwest Semitic > Canaanite > Phoenician"
    period = "814 BCE – 7th c. CE"
    script = "Phnx"  # Phoenician

    prefixes = [
        "Qart-",  # qrt (city: Carthage, Cartagena)
        "Cart-",  # Latinized qrt (Cartagena)
        "Gad-",  # gdr (wall, enclosure: Cadiz)
        "Rus-",  # rʾš (head, cape: Rusaddir)
        "Maha-",  # mḥnt (camp, settlement)
        "Mel-",  # mlk/mlqrt (king/Melqart: Melilla?)
        "Esh-",  # ʾšmn (Eshmun deity)
        "Baal-",  # bʿl (lord: Baalbek transmission)
        "Mago-",  # mgn (shield, personal name)
        "Sul-",  # sl (rock: Sulcis, Sardinia)
        "Tha-",  # tʾ (place marker)
    ]

    suffixes = [
        "-im",  # masculine plural (place of many)
        "-ot",  # feminine plural
        "-it",  # feminine singular/gentilic
        "-an",  # locative/adjectival
        "-hadash",  # ḥdš (new: qart-hadash)
        "-gadir",  # gdr (enclosure: suffix form)
        "-tanit",  # tnt (Tanit deity: theophoric)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "qart": "qrt (city, urban settlement)",
        "cart": "qrt (city, Latinized form)",
        "gad": "gdr (wall, enclosure, fortified area)",
        "gadir": "gdr (wall, enclosure → Cadiz)",
        "rus": "rʾš (head, cape, promontory)",
        "maha": "mḥnt (camp, military settlement)",
        "mel": "mlqrt (Melqart, king of the city)",
        "esh": "ʾšmn (Eshmun, healing deity)",
        "baal": "bʿl (lord, master, deity)",
        "sul": "sl (rock, cliff → Sulcis)",
        "hadash": "ḥdš (new, recent)",
        "im": "-im (masculine plural marker)",
        "ot": "-ot (feminine plural)",
        "tanit": "tnt (Tanit, chief goddess of Carthage)",
        "mago": "mgn (shield, protector)",
        "malaka": "mlk (king/factory → Malaga)",
        "abdera": "ʿbd-rʾ (servant of the sun → Adra)",
        "ibes": "ʾybšm (island of Bes → Ibiza)",
        "motya": "mtw (landing place, Mozia/Sicily)",
        "tharros": "trš (Tharros, Sardinia)",
        "leptis": "lpqy (Leptis Magna, Libya)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Punic toponym into components."""
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
                    confidence=0.85,
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                    confidence=0.75,
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
                    confidence=0.85,
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                    confidence=0.75,
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
        """Classify whether a toponym is likely Punic in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        punic_prefixes = ["qart", "cart", "gad", "rus", "mel", "baal", "sul"]
        for prefix in punic_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                evidence.append(f"Punic prefix '{prefix}-'")
                score += 0.5
                break

        punic_roots = ["gadir", "hadash", "malaka", "motya", "tharros", "leptis"]
        for root in punic_roots:
            if root in form_lower:
                evidence.append(f"Punic root '{root}'")
                score += 0.35
                break

        punic_theophoric = ["baal", "tanit", "melqart", "eshmun"]
        for deity in punic_theophoric:
            if deity in form_lower:
                evidence.append(f"Punic theophoric element '{deity}'")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="814 BCE – 7th c. CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Punic components."""
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
                        sources=["Krahmalkov 2000", "Lipiński 2004"],
                    )
                )
        return candidates
