"""Estonian (eesti) language module for toponymic analysis.

Estonian toponymy is Finno-Ugric with unique features:
- Genitive-based compounds: Tallinn (talu+linn = estate+city)
- Locative suffixes: -vere (spring), -maa (land), -ste (place of)
- Nature terms: -järv (lake), -jõgi (river), -mägi (mountain)
- Swedish/German administrative overlay in cities
- Close relationship with Finnish place naming

Key references:
- Päll 2020 "Eesti kohanimed"
- Kallasmaa 1996 "Saaremaa kohanimed"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class EstonianModule(BaseLanguageModule):
    """Language module for Estonian toponyms."""

    language_code = "est"
    language_name = "Estonian"
    family = "Uralic"
    branch = "Finnic > South Finnic"
    period = "1200 CE–present"
    script = "Latn"

    prefixes = [
        "Suur-",  # great (Suur-Munamägi)
        "Väike-",  # small (Väike-Maarja)
        "Uue-",  # new
        "Vana-",  # old (Vana-Tallinn)
        "Põhja-",  # north
        "Lõuna-",  # south
        "Ida-",  # east
        "Lääne-",  # west
    ]

    suffixes = [
        "-linn",  # city (Tallinn)
        "-maa",  # land (Saaremaa, Hiiumaa)
        "-vere",  # spring (Rakvere, Jõgevere)
        "-ste",  # place of (Kiviõli variant)
        "-järv",  # lake (Peipsi järv)
        "-jõgi",  # river (Emajõgi)
        "-mägi",  # mountain/hill (Suur-Munamägi)
        "-saare",  # island (Saaremaa)
        "-saar",  # island
        "-ranna",  # shore
        "-metsa",  # forest
        "-mets",  # forest
        "-pea",  # head, end (Haapsalu variant)
        "-küla",  # village
        "-soo",  # swamp, bog
        "-nurme",  # meadow
        "-pere",  # family/household
        "-oja",  # ditch, stream
        "-org",  # valley
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "suur": "great, large",
        "väike": "small",
        "uue": "new",
        "vana": "old",
        "linn": "city, fortress",
        "maa": "land, territory",
        "vere": "spring, water source",
        "järv": "lake",
        "jõgi": "river",
        "mägi": "mountain, hill",
        "saare": "island",
        "saar": "island",
        "ranna": "shore, coast",
        "metsa": "forest",
        "küla": "village",
        "soo": "swamp, bog",
        "nurme": "meadow",
        "oja": "ditch, stream",
        "org": "valley",
        "pea": "head, end, cape",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Estonian toponym into morphological components."""
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

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            if matched_prefix and stem.lower().startswith(matched_prefix):
                results.append(
                    SegmentationResult(
                        component=stem[: len(matched_prefix)],
                        position=0,
                        morph_type="compound_modifier",
                        lemma=matched_prefix,
                        confidence=0.8,
                    )
                )
                mid = stem[len(matched_prefix) :]
                if mid:
                    results.append(
                        SegmentationResult(
                            component=mid,
                            position=1,
                            morph_type="stem",
                            lemma=mid.lower(),
                            confidence=0.5,
                        )
                    )
            else:
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
                    position=len(results),
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
                    confidence=0.7,
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
        """Classify whether a toponym is likely Estonian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        estonian_suffixes = ["linn", "maa", "vere", "järv", "jõgi", "mägi", "saare", "küla", "soo"]
        for marker in estonian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Estonian suffix -{marker}")
                score += 0.4
                break

        # Estonian-specific characters
        estonian_chars = ["õ", "ä", "ö", "ü"]
        for ch in estonian_chars:
            if ch in form_lower:
                evidence.append(f"Estonian character '{ch}'")
                score += 0.2
                break

        # Double vowels (common in Estonian)
        if any(v * 2 in form_lower for v in "aeiouõäöü"):
            evidence.append("Estonian double vowel")
            score += 0.1

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Estonian components."""
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
