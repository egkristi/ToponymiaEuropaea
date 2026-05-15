"""Kurdish language module for toponymic analysis.

Kurdish (Kurdî/کوردی) is a Northwestern Iranian language spoken across
Kurdistan (Turkey, Iraq, Iran, Syria). It is an important substrate in
Eastern Turkish and Northern Iraqi toponymy.

Kurdish toponymic features:
- Iranian compound structure with Turkic/Arabic overlay
- Suffixes: -abad, -istan (shared with Persian)
- Stems: çiya (mountain), av (water), gol (lake), dêr (monastery)
- Notable names: Diyarbakır (< Amida + Bakr), Erbil (Arbīl < Arba-ilu),
  Sulaymaniyah, Duhok, Kerkuk

Key references:
- Izady 1992 "The Kurds: A Concise Handbook"
- Hassanpour 1992 "Nationalism and Language in Kurdistan"
- Minorsky 1943 "The Kurds" (Encyclopaedia of Islam)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KurdishModule(BaseLanguageModule):
    """Language module for Kurdish-origin toponyms."""

    language_code = "kur"
    language_name = "Kurdish"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Northwestern Iranian"
    period = "Old Kurdish uncertain; Modern Kurdish 16th c.–"
    script = "Latn (Kurmanji); Arab (Sorani)"

    prefixes = [
        "Ser-",  # on, above (Serhat, Serêkaniyê)
        "Bin-",  # under (Bingöl < Bîngol = 1000 lakes)
        "Çar-",  # four (Çarçella)
        "Deh-",  # village (shared with Persian)
        "Qal-",  # fortress (Qala Diza)
        "Şar-",  # city (Şaredar)
        "Gir-",  # big (Girê Spî)
    ]

    suffixes = [
        "-abad",  # settlement (shared with Persian)
        "-istan",  # land of (Kurdistan)
        "-an",  # plural/locative (Hewlêran)
        "-ê",  # Kurmanji oblique case
        "-geh",  # place (penabergeh = refuge)
        "-xane",  # house (nexweşxane = hospital)
        "-gund",  # village (common Kurdish)
        "-dêr",  # monastery, shrine
        "-awa",  # water, spring (Sulaymāniyya < Slemānî + awa?)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "çiya": "mountain",
        "av": "water (< Old Iranian *āp-)",
        "gol": "lake",
        "dêr": "monastery, shrine (< Syriac dayrā)",
        "gund": "village",
        "şar": "city (< Persian šahr)",
        "qala": "fortress (< Arabic qalʿa)",
        "ser": "on, above, head",
        "bin": "under, below",
        "dar": "tree, wood",
        "zinar": "cliff, rock",
        "çem": "river (< Old Iranian *čama-)",
        "gel": "people, nation",
        "spî": "white",
        "reş": "black",
        "sor": "red",
        "girê": "hill, mound",
        "deşt": "plain, steppe (< Persian dašt)",
        "dol": "valley",
        "kanî": "spring, well (< qanāt?)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kurdish-origin toponym into components."""
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
                    confidence=0.75,
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
                    confidence=0.75,
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
                    confidence=0.75,
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
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym has Kurdish origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        kurd_markers = ["gund", "dêr", "kanî", "çem", "girê"]
        for marker in kurd_markers:
            if marker in form_lower:
                evidence.append(f"Kurdish element '{marker}'")
                score += 0.4
                break

        kurd_prefixes = ["ser", "bin", "gir"]
        for marker in kurd_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Kurdish prefix {marker}-")
                score += 0.25
                break

        # Kurdish-specific phonology (ê, î, û — circumflex vowels)
        if "ê" in form_lower or "î" in form_lower:
            evidence.append("Kurdish-specific vowels (ê, î)")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Kurdish stratum" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Kurdish components."""
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
                        cognates=["Persian " + comp.lemma],
                    )
                )
        return candidates
