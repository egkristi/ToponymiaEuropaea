"""Parthian language module for toponymic analysis.

Parthian was a Northwestern Iranian language spoken in the Arsacid Empire
(3rd century BCE – 3rd century CE), centered in northeastern Iran/Turkmenistan.
The Parthian Empire was Rome's great eastern rival, and many Parthian place
names are known through Greek and Latin sources.

Parthian toponymic features:
- Northwestern Iranian phonology (distinct from Persian)
- Capital: Nisa (near modern Ashgabat), Hecatompylos (Greek name)
- Arsacid dynasty names transmitted to Armenia (Arshakuni)
- Many names known via Greek historians (Strabo, Isidore of Charax)
- Key names: Nisa, Merv (Margiana), Hecatompylos, Rhagae

Key references:
- Ghilain 1939 "Essai sur la langue parthe"
- Boyce 1983 "Parthian Writings and Literature"
- Isidore of Charax "Parthian Stations" (1st c. CE)
- Bivar 1983 "The Political History of Iran under the Arsacids"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ParthianModule(BaseLanguageModule):
    """Language module for Parthian-origin toponyms."""

    language_code = "xpr"
    language_name = "Parthian"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Northwestern Iranian"
    period = "Parthian (3rd c. BCE – 3rd c. CE); DEAD"
    script = "Prti (Parthian script, from Aramaic)"

    prefixes = [
        "Mihr-",  # Mithra, sun (Mihrdātkirt)
        "Vahr-",  # glory, fortune (Vahrām)
        "Arš-",  # Arsacid (Aršak > Arsaces)
        "Vind-",  # finding? (Vindafarnā)
    ]

    suffixes = [
        "-kirt",  # made, built (Mihrdātkirt = built by Mithridates)
        "-gird",  # variant of -kirt (Dārābgird)
        "-šahr",  # realm, city (shared with Middle Persian)
        "-stān",  # land (shared with Persian)
        "-ān",  # place/plural (Tūrān, Kirmān?)
        "-āwand",  # possessing, having (Dēwāwand > Damavand?)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "mihr": "Mithra, sun (< *Miθra-; widespread in theophoric names)",
        "vahr": "glory, divine fortune (< *vṛθra-gna- > Bahrām)",
        "arš": "Arsaces (dynasty founder; < *ṛšan- = male, hero?)",
        "kirt": "made, built (< *kṛta-; cf. Persian kard)",
        "gird": "made (variant; cf. Dārābgird)",
        "šahr": "realm, kingdom, city (< *xšaθra-)",
        "nisa": "capital (etymology uncertain; Nēsā?)",
        "marg": "meadow (Margiana = Merv region; < *margu-)",
        "asp": "horse (< *aspa-; Aspadānā > Isfahan?)",
        "dāt": "given (< *dāta-; Mihrdāt = given by Mithra)",
        "wind": "finding (< *vinda-; cf. Vindafarnā)",
        "bagā": "god (< *baga-)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Parthian-origin toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes], key=len, reverse=True
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes], key=len, reverse=True
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
                    confidence=0.7,
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
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="prefix",
                    lemma=matched_prefix,
                    confidence=0.65,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="stem",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.5,
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
        """Classify whether a toponym has Parthian origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Known Parthian toponyms (via Greek/Latin sources)
        known = {
            "nisa": "Parthian capital (Nēsā)",
            "hecatomp": "Hecatompylos (Greek name for Parthian city)",
            "merv": "Margiana (Merv; Parthian province)",
            "rhagae": "Parthian city (modern Ray/Tehran)",
        }
        for name, note in known.items():
            if name in form_lower:
                evidence.append(f"Known Parthian toponym: {note}")
                score += 0.5
                break

        # Parthian compound suffixes
        parthian_suffixes = ["kirt", "gird", "āwand"]
        for marker in parthian_suffixes:
            if form_lower.endswith(marker):
                evidence.append(f"Parthian suffix -{marker}")
                score += 0.35
                break

        # Parthian theophoric prefix
        if form_lower.startswith(("mihr", "vahr")):
            evidence.append("Parthian theophoric prefix")
            score += 0.25

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Parthian/Arsacid period (3rd c. BCE – 3rd c. CE)"
            if score > 0.3
            else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Parthian components."""
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
                        cognates=["Middle Persian " + comp.lemma, "Avestan"],
                        sources=["Ghilain 1939", "Isidore of Charax"],
                    )
                )
        return candidates
