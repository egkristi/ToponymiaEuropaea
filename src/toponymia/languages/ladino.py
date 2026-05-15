"""Ladino language module for toponymic analysis.

Ladino (Judeo-Spanish, lad) is a Romance language preserving medieval
Castilian as spoken by Sephardic Jews expelled from Iberia in 1492. Relevant
to toponymy through: Sephardic quarter names (judería, call, mellah), place
names of Jewish communities in the Ottoman Empire and Balkans, and preserved
medieval Iberian forms. Written in Hebrew script (Rashi/Solitreo) or Latin
alphabet. Spoken in Turkey, Greece, Israel, and diaspora communities.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LadinoModule(BaseLanguageModule):
    """Language module for Ladino/Judeo-Spanish toponyms."""

    language_code = "lad"
    language_name = "Ladino"
    family = "Indo-European"
    branch = "Romance > Ibero-Romance"
    period = "Medieval–Modern (1200 CE–present)"
    script = "Latn"

    prefixes = [
        "Djudio-",
        "Nuevo-",
        "Grande-",
        "Chiko-",
    ]

    suffixes = [
        "-ería",
        "-ada",
        "-ika",
        "-iko",
        "-luk",
        "-lik",
        "-dji",
        "-hane",
    ]

    stems = [
        "judería",
        "call",
        "mellah",
        "kal",
        "kortijo",
        "barrio",
        "plaza",
        "fuente",
        "puente",
        "rio",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "djudio": "Jewish",
            "nuevo": "new",
            "grande": "large",
            "chiko": "small",
            "ería": "place of (suffix)",
            "ada": "collective/place suffix",
            "ika": "diminutive (fem.)",
            "iko": "diminutive (masc.)",
            "luk": "place/state (< Turkish -lık)",
            "lik": "place/state (< Turkish)",
            "dji": "agent (< Turkish -ci)",
            "hane": "house (< Turkish/Persian)",
            "judería": "Jewish quarter",
            "call": "Jewish quarter (Catalan)",
            "mellah": "Jewish quarter (N.African)",
            "kal": "synagogue (< Heb. qahal)",
            "kortijo": "courtyard, estate",
            "barrio": "neighbourhood",
            "plaza": "square",
            "fuente": "fountain, spring",
            "puente": "bridge",
            "rio": "river",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Ladino toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.7,
                    )
                )
                form = form[len(prefix) :]
                form_lower = form.lower()
                break

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                pos = len(results)
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=pos,
                        morph_type="stem",
                        confidence=0.5,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=pos + 1,
                        morph_type="suffix",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.65,
                    )
                )
                return results

        # Try matching known stems
        pos = len(results)
        for stem in sorted(self.stems, key=len, reverse=True):
            if form_lower == stem:
                results.append(
                    SegmentationResult(
                        component=form,
                        position=pos,
                        morph_type="stem",
                        lemma=stem,
                        meaning=self._element_meaning(stem),
                        confidence=0.7,
                    )
                )
                return results

        results.append(
            SegmentationResult(
                component=form,
                position=pos,
                morph_type="stem",
                confidence=0.3,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Ladino."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        ladino_terms = ["judería", "call", "mellah", "kal", "kortijo"]
        for term in ladino_terms:
            if term in form_lower:
                evidence.append(f"Sephardic settlement term '{term}'")
                score += 0.4
                break

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Ladino suffix -{suffix}")
                score += 0.25
                break

        ladino_spelling = ["dj", "sh", "iko", "ika"]
        for sp in ladino_spelling:
            if sp in form_lower:
                evidence.append(f"Ladino orthography '{sp}'")
                score += 0.2
                break

        turkish_contact = ["luk", "hane", "dji", "pasha"]
        for tc in turkish_contact:
            if tc in form_lower:
                evidence.append(f"Ottoman contact element '{tc}'")
                score += 0.2
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "judería": ("iudaeariam", "Jewish quarter", ["Sp. judería", "Pt. judiaria"]),
            "call": ("*kahale", "Jewish quarter (< Heb. qahal)", ["Cat. call"]),
            "mellah": ("mallāḥ", "salt/Jewish quarter", ["Ar. mallāḥ"]),
            "kal": ("qahal", "congregation, synagogue", ["Heb. qahal"]),
            "fuente": ("fontem", "fountain, spring", ["Sp. fuente", "It. fonte"]),
            "puente": ("pontem", "bridge", ["Sp. puente", "It. ponte"]),
            "rio": ("rivum", "river", ["Sp. río", "Pt. rio"]),
            "plaza": ("plateam", "square", ["Sp. plaza", "It. piazza"]),
            "barrio": ("*barrī", "neighbourhood (< Ar.)", ["Sp. barrio"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.65,
                        cognates=cognates,
                        sources=["Nehama, Dictionnaire du Judéo-Espagnol"],
                    )
                )
        return candidates
