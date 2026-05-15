"""Hebrew language module for toponymic analysis.

Hebrew toponymy spans from Biblical antiquity (c. 1200 BCE) through
Mishnaic and Medieval periods to Modern Hebrew (revived 1880s).
Characterized by:
- Construct-state compounds (smichut): Beit-Lehem (house of bread)
- Topographic prefixes: Ein/En- (spring), Tel- (mound), Be'er- (well)
- Settlement prefixes: Kfar- (village), Beit/Beth- (house)
- Plural markers: -im (masc.), -ot (fem.), -ayim (dual)
- Root-and-pattern morphology (triliteral roots)

Key references:
- Rainey 2006 "The Sacred Bridge"
- Demsky 2004 "These Are the Names: Studies in Jewish Onomastics"
- Zadok 1988 "The Pre-Hellenistic Israelite Anthroponymy and Prosopography"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class HebrewModule(BaseLanguageModule):
    """Language module for Hebrew toponyms."""

    language_code = "heb"
    language_name = "Hebrew"
    family = "Afro-Asiatic"
    branch = "Semitic > Central Semitic > Northwest Semitic > Canaanite"
    period = "c. 1200 BCE – present (Biblical, Mishnaic, Modern)"
    script = "Hebr"

    prefixes = [
        "Tel-",  # mound, archaeological site (Tel Aviv)
        "Be'er-",  # well (Be'er Sheva)
        "Ein-",  # spring ('Ein Gedi)
        "En-",  # spring variant (En Dor)
        "Kfar-",  # village (Kfar Saba)
        "Beit-",  # house (Beit She'an)
        "Beth-",  # house, anglicized (Bethlehem)
        "Givat-",  # hill (Giv'at Shmuel)
        "Ramat-",  # heights (Ramat Gan)
        "Nahal-",  # stream/wadi (Nahal Sorek)
        "Har-",  # mountain (Har Sinai)
        "Yam-",  # sea (Yam Kinneret)
        "Neve-",  # oasis/pasture (Neve Tzedek)
    ]

    suffixes = [
        "-im",  # masculine plural (Yerushalayim)
        "-ot",  # feminine plural (Nazareth < Natzr-at)
        "-ayim",  # dual (Yerushal-ayim, Mitzr-ayim)
        "-on",  # diminutive (Hevron, Ashkelon)
        "-it",  # feminine adjective (Bereshit)
        "-el",  # God (Yizre'el, Beit-El)
        "-yah",  # YHWH theophoric (Eliyyahu > Elijah)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "tel": "tell/mound (archaeological hill)",
        "beer": "be'er (well, water source)",
        "ein": "'ayin (spring, water source)",
        "en": "'ayin (spring, water source)",
        "kfar": "kfar (village, hamlet)",
        "beit": "bayit (house, temple)",
        "beth": "bayit (house, temple)",
        "givat": "giv'ah (hill)",
        "ramat": "ramah (heights, elevated place)",
        "nahal": "naḥal (stream, wadi)",
        "har": "har (mountain)",
        "yam": "yam (sea, lake)",
        "neve": "neveh (oasis, pasture)",
        "im": "masculine plural marker",
        "ot": "feminine plural marker",
        "ayim": "dual marker (pair)",
        "on": "diminutive/place suffix",
        "el": "'el (God)",
        "yah": "YHWH (theophoric element)",
        "shalom": "shālōm (peace, wholeness)",
        "tzion": "ṣiyyōn (Zion, landmark)",
        "ir": "'ir (city)",
        "migdal": "migdāl (tower)",
        "maayan": "ma'ayan (spring, fountain)",
        "emek": "'ēmeq (valley)",
        "gat": "gat (winepress)",
        "kerem": "kerem (vineyard)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Hebrew toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower().replace("'", "")

        sorted_prefixes = sorted(
            [p.rstrip("-").lower().replace("'", "") for p in self.prefixes],
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

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]
            if remainder.startswith(("-", " ")):
                remainder = remainder[1:]
                prefix_part = form[: len(matched_prefix) + 1]

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

            if matched_suffix and remainder.lower().endswith(matched_suffix):
                stem = remainder[: len(remainder) - len(matched_suffix)]
                if stem:
                    results.append(
                        SegmentationResult(
                            component=stem,
                            position=1,
                            morph_type="stem",
                            lemma=stem.lower(),
                            confidence=0.5,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=len(results),
                        morph_type="suffix",
                        lemma=matched_suffix,
                        meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                        confidence=0.7,
                    )
                )
            else:
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
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
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
        """Classify whether a toponym is likely Hebrew in origin."""
        form_lower = form.lower().replace("'", "")
        score = 0.0
        evidence: list[str] = []

        hebrew_prefixes = [
            "tel",
            "beer",
            "ein",
            "en",
            "kfar",
            "beit",
            "beth",
            "givat",
            "ramat",
            "nahal",
            "har",
            "neve",
        ]
        for prefix in hebrew_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                evidence.append(f"Hebrew prefix {prefix}-")
                score += 0.4
                break

        hebrew_suffixes = ["ayim", "im", "ot", "on", "el", "yah"]
        for suffix in hebrew_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Hebrew suffix -{suffix}")
                score += 0.3
                break

        hebrew_elements = ["shalom", "tzion", "migdal", "gat", "kerem", "emek"]
        for elem in hebrew_elements:
            if elem in form_lower:
                evidence.append(f"Hebrew element '{elem}'")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Biblical/Iron Age" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Hebrew components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().replace("'", "").rstrip("-")
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
                        sources=["Rainey 2006", "Demsky 2004"],
                    )
                )
        return candidates
