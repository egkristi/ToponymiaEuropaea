"""Mongolian language module for toponymic analysis.

Mongolian (Khalkha and historical Middle Mongol) left toponymic traces
across Eurasia through the Mongol Empire (1206–1368) and its successor
states. While the Mongol administrative language was often Turkic or
Persian, Mongolian proper contributed to place-naming:

- Mongol Empire administrative centers (Karakorum, Sarai, Almaliq)
- Titles/ranks preserved as place-names (khan, noyon, daruga)
- Geographic terms from Mongolian military/pastoral tradition
- Indirect path to Scandinavia: Mongol threat was known to Norwegian
  court (King Håkon IV, 1240s); Matthew Paris mapped "Tartars"
- Via Golden Horde: Mongol terminology entered Russian, then spread
  to neighboring languages including Old Norse late vocabulary

Key phonological features for identification:
- Vowel harmony (front/back)
- Initial consonant clusters rare
- Final -n, -r, -l common
- Long vowels significant

Key references:
- Clauson 1972 "An Etymological Dictionary of Pre-13th Century Turkish"
- Lessing 1960 "Mongolian-English Dictionary"
- Ratchnevsky 1991 "Genghis Khan: His Life and Legacy"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MongolianModule(BaseLanguageModule):
    """Language module for Mongolian toponyms."""

    language_code = "mon"  # ISO 639-3 Mongolian (Khalkha)
    language_name = "Mongolian"
    family = "Mongolic"
    branch = "Central Mongolic"
    period = "1200–present (Empire era naming most relevant)"
    script = "Mong (traditional) / Cyrl (modern)"

    prefixes = [
        "Khara-",  # black (Karakorum < Mongol. qara qorum)
        "Tsagaan-",  # white (Tsagaan Nuur)
        "Ulaan-",  # red (Ulaanbaatar)
        "Khökh-",  # blue (Khökh Nuur = Blue Lake)
        "Ikh-",  # great (Ikh Khüree)
        "Baga-",  # small, little
        "Öndör-",  # high (Öndörkhaan)
        "Dalan-",  # seventy (Dalan Balgas)
        "Nar-",  # sun (Naran)
    ]

    suffixes = [
        "-baatar",  # hero (Ulaanbaatar)
        "-gol",  # river (Mongol, from which 'Mongol' itself?)
        "-nuur",  # lake (Khövsgöl Nuur, Baikal < Mongol?)
        "-khot",  # city (Altan-khot)
        "-bulaq",  # spring (shared with Turkic)
        "-khan",  # ruler (Öndörkhaan)
        "-orda",  # camp, palace (Altan Orda = Golden Horde)
        "-tal",  # steppe, plain (Mongol Tal)
        "-uul",  # mountain (Bogd Uul)
        "-khüree",  # encampment, monastery (Ikh Khüree)
        "-tolgoi",  # hill, mound
        "-khoshuu",  # banner, administrative division
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "khara": "black (Mongol.; cf. Turkic kara)",
        "tsagaan": "white, pure",
        "ulaan": "red",
        "khökh": "blue, blue-green",
        "ikh": "great, large",
        "baga": "small, lesser",
        "öndör": "high, tall",
        "dalan": "seventy (numeral in names)",
        "nar": "sun",
        "baatar": "hero, warrior (> Russian bogatyr?)",
        "gol": "river, stream",
        "nuur": "lake",
        "khot": "city, settlement",
        "bulaq": "spring, source",
        "khan": "ruler, sovereign (Chinggis Khan)",
        "orda": "palace, camp, horde (> English 'horde')",
        "tal": "steppe, open plain",
        "uul": "mountain",
        "khüree": "monastery encampment, circle",
        "tolgoi": "hill, head, mound",
        "khoshuu": "banner (administrative unit)",
        "noyon": "prince, lord (administrative title)",
        "daruga": "governor (Mongol administrator > Russian daroga)",
        "yam": "postal station (> Russian yam > Yamskaya)",
        "tümen": "ten thousand (administrative unit > Tyumen)",
        "balgasun": "ruined city, fortress",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Mongolian toponym into components."""
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

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix):
                remainder = form[len(prefix) :]
                meaning = self.ELEMENT_MEANINGS.get(prefix, "")
                results.append(
                    SegmentationResult(
                        segments=[prefix, remainder],
                        language=self.language_code,
                        confidence=0.55,
                        notes=(f"Mongolian prefix '{prefix}' ({meaning}) + '{remainder}'"),
                    )
                )
                break

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                meaning = self.ELEMENT_MEANINGS.get(suffix, "")
                results.append(
                    SegmentationResult(
                        segments=[stem, suffix],
                        language=self.language_code,
                        confidence=0.55,
                        notes=(f"Mongolian: '{stem}' + suffix '-{suffix}' ({meaning})"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Mongolian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Known Mongolian administrative/geographic terms
        mongol_markers = [
            "baatar",
            "khaan",
            "khan",
            "orda",
            "nuur",
            "gol",
            "khot",
            "khüree",
            "tümen",
            "noyon",
            "yam",
        ]
        for marker in mongol_markers:
            if marker in form_lower:
                evidence.append(f"Contains Mongolian element '{marker}'")
                score += 0.45
                break

        # Mongolian color prefixes (distinct from Turkic by form)
        mongol_colors = ["ulaan", "tsagaan", "khökh", "khara"]
        for color in mongol_colors:
            if form_lower.startswith(color):
                evidence.append(f"Mongolian color prefix '{color}-'")
                score += 0.4
                break

        # Mongolian phonotactics: kh- initial
        if form_lower.startswith("kh"):
            evidence.append("Initial kh- cluster (Mongolian phonotactics)")
            score += 0.15

        # Long vowels written as doubled (aa, uu, öö)
        doubled_vowels = ["aa", "uu", "öö", "ee", "ii"]
        for dv in doubled_vowels:
            if dv in form_lower:
                evidence.append(f"Doubled vowel '{dv}' (Mongolian long vowel)")
                score += 0.15
                break

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Mongolian etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.45,
                        notes=f"Mongolian element '{element}' in '{form}'",
                    )
                )

        return candidates
