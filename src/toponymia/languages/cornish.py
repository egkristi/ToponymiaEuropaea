"""Cornish language module for toponymic analysis.

Cornish (Kernewek) is a Brittonic Celtic language of Cornwall, revived in the
20th century after declining from the 18th century. Cornish toponymy is
famous for its distinctive prefixes: Tre- (homestead), Pen- (head/end),
Pol- (pool/cove), Lan- (enclosure/church site). "By Tre, Pol and Pen /
Shall ye know Cornishmen." Many thousands of Cornish place names survive
in Cornwall despite the language's near-extinction.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CornishModule(BaseLanguageModule):
    """Language module for Cornish toponyms."""

    language_code = "cor"
    language_name = "Cornish"
    family = "Indo-European"
    branch = "Celtic > Brittonic"
    period = "Medieval–Modern (800 CE–present, revived 1904)"
    script = "Latn"

    prefixes = [
        "Tre-",
        "Pen-",
        "Pol-",
        "Lan-",
        "Ros-",
        "Car-",
        "Nan-",
        "Bod-",
        "Bal-",
        "Men-",
        "Porth-",
        "Cam-",
    ]

    suffixes = [
        "-ek",
        "-an",
        "-ow",
        "-ys",
        "-ack",
        "-aze",
        "-idden",
        "-ney",
        "-ence",
    ]

    stems = [
        "tre",
        "pen",
        "pol",
        "lan",
        "ros",
        "car",
        "men",
        "dour",
        "mor",
        "ker",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "tre": "homestead, settlement",
            "pen": "head, end, promontory",
            "pol": "pool, cove",
            "lan": "enclosure, church site",
            "ros": "heath, moor, promontory",
            "car": "fort, rock",
            "nan": "valley",
            "bod": "dwelling",
            "bal": "mine working, place",
            "men": "stone",
            "porth": "harbour, cove",
            "cam": "crooked",
            "dour": "water",
            "mor": "sea",
            "ker": "fort (variant of car)",
            "ek": "adjectival suffix",
            "an": "diminutive",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Cornish toponym into morphological components."""
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
                        confidence=0.8,
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
                        confidence=0.6,
                    )
                )
                return results

        pos = len(results)
        results.append(
            SegmentationResult(
                component=form,
                position=pos,
                morph_type="stem",
                confidence=0.4,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Cornish."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Cornish prefix {prefix}-")
                score += 0.4
                break

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Cornish suffix -{suffix}")
                score += 0.2
                break

        cornish_elements = ["tre", "pen", "pol", "lan", "ros", "porth", "car"]
        for elem in cornish_elements:
            if elem in form_lower and elem not in [
                p.rstrip("-").lower()
                for p in self.prefixes
                if form_lower.startswith(p.rstrip("-").lower())
            ]:
                evidence.append(f"Cornish element '{elem}'")
                score += 0.2
                break

        if not evidence and any(c in form_lower for c in ["dh", "gh", "wh"]):
            evidence.append("Brittonic consonant cluster")
            score += 0.15

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "tre": ("*treb-", "homestead", ["W. tref", "Br. trev"]),
            "pen": ("*pennos", "head, end", ["W. pen", "Br. penn"]),
            "pol": ("*pull-", "pool, pit", ["W. pwll", "Br. poull"]),
            "lan": ("*landā", "enclosure, sacred place", ["W. llan", "Br. lann"]),
            "ros": ("*rosso-", "promontory, heath", ["W. rhos", "Br. roz"]),
            "car": ("*karito-", "fort", ["W. caer", "Br. kêr"]),
            "men": ("*maen-", "stone", ["W. maen", "Br. maen"]),
            "porth": ("*portu-", "harbour", ["W. porth", "Lat. portus"]),
            "dour": ("*dubron", "water", ["W. dŵr", "Br. dour"]),
            "mor": ("*mori-", "sea", ["W. môr", "Lat. mare"]),
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
                        confidence=0.75,
                        cognates=cognates,
                        sources=["Padel, Cornish Place-Name Elements"],
                    )
                )
        return candidates
