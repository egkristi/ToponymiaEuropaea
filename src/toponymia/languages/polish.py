"""Polish (polski) language module for toponymic analysis.

Polish toponymy is one of the richest in Central Europe:
- Possessive suffixes: -ów/-owo, -in/-ino (Kraków, Warszawa)
- Locative suffixes: -ice/-yce (Katowice), -sko (Słupsko)
- Topographic roots: góra (mountain), rzeka (river), las (forest)
- Patronymic settlements: -owice, -ewice (sons of X)
- Germanic substrata in Silesia and Pomerania

Key references:
- Rospond 1984 "Słownik etymologiczny miast i gmin PRL"
- Malec 2003 "Słownik etymologiczny nazw geograficznych Polski"
- Rymut 1996–2009 "Nazwy miejscowe Polski"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PolishModule(BaseLanguageModule):
    """Language module for Polish toponyms."""

    language_code = "pol"
    language_name = "Polish"
    family = "Indo-European"
    branch = "Slavic > West Slavic > Lechitic"
    period = "1000 CE–present"
    script = "Latn"

    prefixes = [
        "Nowo-",  # new (Nowogród)
        "Staro-",  # old (Starogard)
        "Biało-",  # white (Białystok)
        "Czarno-",  # black (Czarnogóra)
        "Czerwono-",  # red
        "Wielko-",  # great (Wielkopolska)
        "Mało-",  # small (Małopolska)
        "Dolno-",  # lower (Dolnośląskie)
        "Górno-",  # upper (Górnośląskie)
        "Między-",  # between (Międzyrzecz)
        "Pod-",  # under (Podlasie)
        "Za-",  # beyond (Zamość)
        "Nad-",  # above (Nadwiślański)
    ]

    suffixes = [
        "-ów",  # possessive masculine (Kraków, Rzeszów)
        "-owo",  # possessive neuter (Inowrocław variant)
        "-ew",  # possessive (Wrocław)
        "-ewo",  # possessive neuter
        "-in",  # possessive feminine (Lublin, Szczecin)
        "-ino",  # possessive neuter
        "-ice",  # place of (Katowice, Gliwice)
        "-yce",  # place of (variant)
        "-owice",  # patronymic (Sosnowiec)
        "-ewice",  # patronymic soft
        "-ów",  # possessive
        "-sk",  # adjectival (Gdańsk, Płońsk)
        "-sko",  # neuter adjectival
        "-gród",  # fortified town (Nowogród, Starogard)
        "-gard",  # fortified town (Stargard)
        "-wola",  # free settlement (from 'wolność')
        "-góra",  # mountain (Zielona Góra, Jelenia Góra)
        "-las",  # forest
        "-pole",  # field (Tarnopol)
        "-most",  # bridge
        "-bór",  # pine forest (Dąbrowa)
        "-stok",  # confluence (Białystok)
        "-rzecz",  # river related (Międzyrzecz)
        "-wice",  # patronymic plural
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "nowo": "new",
        "staro": "old",
        "biało": "white",
        "czarno": "black",
        "czerwono": "red",
        "wielko": "great",
        "mało": "small",
        "dolno": "lower",
        "górno": "upper",
        "między": "between",
        "gród": "fortified town, castle",
        "gard": "fortified town",
        "góra": "mountain, hill",
        "pole": "field",
        "las": "forest",
        "bór": "pine forest",
        "stok": "confluence, slope",
        "rzecz": "river, thing",
        "wola": "free settlement",
        "most": "bridge",
        "morze": "sea",
        "jezioro": "lake",
        "rzeka": "river",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Polish toponym into morphological components."""
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
                    morph_type="prefix",
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
                    morph_type="suffix",
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
                    confidence=0.8,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="prefix",
                    lemma=matched_prefix,
                    confidence=0.7,
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
                    morph_type="simplex",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Polish."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        polish_suffixes = ["ów", "owo", "ice", "yce", "owice", "wice", "gród", "wola"]
        for marker in polish_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Polish suffix -{marker}")
                score += 0.35
                break

        # Polish-specific characters
        polish_chars = ["ł", "ą", "ę", "ó", "ś", "ź", "ć", "ń", "ż"]
        for ch in polish_chars:
            if ch in form_lower:
                evidence.append(f"Polish character '{ch}'")
                score += 0.2
                break

        # Polish consonant clusters
        polish_clusters = ["szcz", "prz", "trz", "chrz"]
        for cluster in polish_clusters:
            if cluster in form_lower:
                evidence.append(f"Polish cluster '{cluster}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1000–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Polish components."""
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
