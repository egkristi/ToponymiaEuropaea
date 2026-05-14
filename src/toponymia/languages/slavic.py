"""Old Slavic (Pan-Slavic) language module for toponymic analysis.

Slavic toponymy spans the vast area from the Elbe to Vladivostok.
Characterized by:
- Possessive suffixes: -ov/-evo, -in/-ino (owner's name + possessive)
- Locative endings: -itz/-ice (place of), -grad/-gorod (fortified town)
- Topographic roots: breg/berg (hill), reka (river), les/laz (forest)
- Shared Proto-Slavic stock across all Slavic languages

Key references:
- Vasmer 1953–1958 "Russisches Etymologisches Wörterbuch"
- Profous 1947–1960 "Místní jména v Čechách"
- Bezlaj 1956–2007 "Etimološki slovar slovenskega jezika"
- Rospond 1984 "Słownik etymologiczny miast i gmin PRL"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldSlavicModule(BaseLanguageModule):
    """Language module for Old/Common Slavic toponyms."""

    language_code = "sla"  # ISO 639-5 for Slavic languages
    language_name = "Old Slavic (Pan-Slavic)"
    family = "Indo-European"
    branch = "Slavic"
    period = "600 CE–present"
    script = "Latn/Cyrl"

    # Common Slavic toponymic prefixes
    prefixes = [
        "Belo-",  # white (Beograd, Białystok)
        "Bielo-",  # white (variant)
        "Biały-",  # white (Polish)
        "Novo-",  # new (Novosibirsk, Nowy Sącz)
        "Staro-",  # old (Stalingrad→Staraya)
        "Veliko-",  # great (Veliky Novgorod)
        "Maly-",  # small
        "Cerno-",  # black (Černigov, Czernowitz)
        "Červeno-",  # red
        "Dolno-",  # lower
        "Gorno-",  # upper
        "Pod-",  # under, below
        "Za-",  # beyond, behind
        "Nad-",  # above
        "Pri-",  # near
        "Meždu-",  # between
    ]

    # Common Slavic toponymic suffixes
    suffixes = [
        "-ov",  # possessive masculine (Petrov, Kharkov)
        "-ovo",  # possessive neuter (Sheremetyevo)
        "-ev",  # possessive (soft stem)
        "-evo",  # possessive neuter (soft stem)
        "-in",  # possessive feminine (Berlin? disputed)
        "-ino",  # possessive neuter feminine
        "-itz",  # place of (German rendering: Chemnitz, Austerlitz)
        "-ice",  # place of (Czech/Slovak: Budějovice)
        "-ica",  # place of (South Slavic: Šibenik→Lješevica)
        "-grad",  # fortified city (Beograd, Leningrad)
        "-gorod",  # fortified city (Novgorod, Uzhgorod)
        "-gard",  # fortified city (Stargard)
        "-sk",  # adjectival (Minsk, Gdańsk, Omsk)
        "-sko",  # adjectival neuter
        "-pole",  # field (Sevastopol, Tarnopol)
        "-pol",  # field (variant)
        "-brod",  # ford (Magdeburg < Slavic?)
        "-most",  # bridge
        "-log",  # meadow, dale
        "-dol",  # valley
        "-gora",  # mountain (Podgorica, Bjelašnica)
        "-les",  # forest
        "-reka",  # river
        "-potok",  # stream
        "-jezero",  # lake
        "-ostrov",  # island
    ]

    # Element meanings for etymology
    ELEMENT_MEANINGS: dict[str, str] = {
        "belo": "white, bright",
        "bielo": "white (variant)",
        "novo": "new",
        "staro": "old",
        "veliko": "great, large",
        "maly": "small",
        "cerno": "black",
        "červeno": "red",
        "dolno": "lower",
        "gorno": "upper",
        "pod": "under, below",
        "za": "beyond, behind",
        "nad": "above",
        "pri": "near, by",
        "grad": "fortified city, castle",
        "gorod": "fortified city (East Slavic)",
        "gard": "fortified city (West Slavic)",
        "pole": "field, open land",
        "brod": "ford, crossing",
        "most": "bridge",
        "gora": "mountain, hill",
        "les": "forest, wood",
        "reka": "river",
        "potok": "stream, brook",
        "jezero": "lake",
        "ostrov": "island",
        "dol": "valley, dale",
        "log": "meadow, clearing",
        "breg": "bank, shore, hill",
        "ov": "possessive (masc.)",
        "ovo": "possessive (neut.)",
        "in": "possessive (fem.)",
        "ino": "possessive (neut. fem.)",
        "itz": "place of (-ice/-itz)",
        "ice": "place of (Czech)",
        "sk": "adjectival suffix",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Slavic toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try suffix matching first (Slavic is heavily suffix-based)
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

        # Also try prefix matching
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

        if matched_prefix and matched_suffix:
            # Both prefix and suffix matched
            prefix_part = form[: len(matched_prefix)]
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
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
                    morph_type="derivational_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_head",
                    lemma=stem.lower(),
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="derivational_suffix",
                    lemma=matched_suffix,
                    confidence=0.8,
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
                    confidence=0.7,
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
        """Classify whether a toponym is likely Slavic in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Check for Slavic suffixes
        slavic_suffix_markers = [
            "ov",
            "ovo",
            "ev",
            "evo",
            "in",
            "ino",
            "itz",
            "ice",
            "ica",
            "grad",
            "gorod",
            "gard",
            "sk",
            "sko",
            "pole",
            "pol",
            "brod",
            "gora",
        ]
        for marker in slavic_suffix_markers:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Slavic suffix -{marker}")
                score += 0.3
                break

        # Check for Slavic prefixes
        slavic_prefix_markers = [
            "belo",
            "bielo",
            "novo",
            "staro",
            "veliko",
            "cerno",
            "červeno",
            "dolno",
            "gorno",
        ]
        for marker in slavic_prefix_markers:
            if form_lower.startswith(marker):
                evidence.append(f"Slavic prefix {marker}-")
                score += 0.3
                break

        # Check for typical Slavic consonant clusters
        slavic_clusters = ["str", "zdr", "šč", "žd", "prz", "brz", "trz"]
        for cluster in slavic_clusters:
            if cluster in form_lower:
                evidence.append(f"Slavic cluster '{cluster}'")
                score += 0.1
                break

        # Check for typical Slavic characters/digraphs
        slavic_chars = ["č", "š", "ž", "ř", "ń", "ł", "ś", "ź", "ć"]
        for ch in slavic_chars:
            if ch in form_lower:
                evidence.append(f"Slavic character '{ch}'")
                score += 0.15
                break

        score = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="600–1500 CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Slavic components."""
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
                    )
                )

        return candidates
