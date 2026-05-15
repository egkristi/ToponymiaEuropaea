"""Ukrainian (українська) language module for toponymic analysis.

Ukrainian toponymy shares the East Slavic layer with Russian but has
distinctive features:
- Possessive suffixes: -ів/-їв (Kyiv, Kharkiv, Dnipro)
- Locative suffixes: -ці/-ці, -ськ (Zaporizhzhia, Lutsk)
- Unique phonology: і for ě/o, г→h, ї (yi)
- Cossack-era naming patterns (Sich, Zaporizhzhia)
- Polish administrative influence (western regions)

Key references:
- Janko 1998 "Toponimichnyy slovnyk Ukrayiny"
- Luchyk 2014 "Etymolohichnyy slovnyk toponimiv Ukrayiny"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class UkrainianModule(BaseLanguageModule):
    """Language module for Ukrainian toponyms."""

    language_code = "ukr"
    language_name = "Ukrainian"
    family = "Indo-European"
    branch = "Slavic > East Slavic"
    period = "1200 CE–present"
    script = "Cyrl"

    prefixes = [
        "Novo-",  # new (Novoyavorivsk)
        "Staro-",  # old (Starokostiantyniv)
        "Biło-",  # white (Bila Tserkva)
        "Chorno-",  # black (Chornobyl)
        "Chervono-",  # red (Chervonohrad)
        "Verkhn-",  # upper (Verkhnya)
        "Nyzhn-",  # lower (Nyzhnya)
        "Zaporiz-",  # beyond the rapids
        "Dnipro-",  # Dnieper-related
        "Poltav-",  # field-related
        "Velyk-",  # great (Velyki Mosty)
        "Mal-",  # small (Mali Pidlisky)
    ]

    suffixes = [
        "-iv",  # possessive (Kyiv, Kharkiv, Lviv)
        "-yiv",  # possessive variant
        "-ovo",  # possessive neuter (Dnipropetrovsk oblast)
        "-ino",  # possessive neuter
        "-yntsi",  # patronymic plural (Vinnytsia)
        "-tsi",  # patronymic plural
        "-sti",  # patronymic plural
        "-shchyna",  # region (Volyn-shchyna, Halychyna)
        "-zia",  # abstract/locative (Zaporizhzhia)
        "-sk",  # adjectival (Lutsk, Khmelnitskiy)
        "-ske",  # neuter adjectival
        "-horod",  # city (Uzhhorod, Bilhorod)
        "-hrad",  # city (Pavlohrad)
        "-pil",  # field (Ternopil, Sevastopol variant)
        "-pol",  # field (Melitopol, Nikopol)
        "-vka",  # settlement diminutive
        "-ivka",  # settlement (Zinkivka)
        "-anka",  # settlement
        "-ychi",  # patronymic (Baryshivka→Baranivychi)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "novo": "new",
        "staro": "old",
        "biło": "white",
        "chorno": "black",
        "chervono": "red",
        "verkhn": "upper",
        "nyzhn": "lower",
        "velyk": "great",
        "mal": "small",
        "horod": "city, town",
        "hrad": "city (fortified)",
        "pil": "field",
        "pol": "field",
        "richka": "river",
        "ozero": "lake",
        "hora": "mountain",
        "lis": "forest",
        "pole": "field",
        "dnipr": "Dnieper river",
        "sich": "fortified camp (Cossack)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Ukrainian toponym into morphological components."""
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
        """Classify whether a toponym is likely Ukrainian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        ukrainian_suffixes = ["iv", "yiv", "horod", "hrad", "shchyna", "yntsi", "ivka"]
        for marker in ukrainian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Ukrainian suffix -{marker}")
                score += 0.35
                break

        # Ukrainian-specific phonetic features (transliterated)
        if "zh" in form_lower and "zh" not in "":
            evidence.append("Ukrainian phonetic 'zh'")
            score += 0.1
        if "shch" in form_lower:
            evidence.append("Ukrainian 'shch' (щ)")
            score += 0.15

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Ukrainian components."""
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
