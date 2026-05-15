"""Old Church Slavonic language module for toponymic analysis.

Old Church Slavonic (OCS) was the first literary Slavic language (9th c.),
used as a liturgical and administrative language across Orthodox Slavdom:
- Created by Saints Cyril and Methodius (863 CE) for Great Moravia
- Became the ecclesiastical language of Bulgaria, Serbia, Rus', Romania
- Church-related place-names across Eastern Europe use OCS elements
- Important for understanding the religious naming layer:
  - Monastery/church-based settlements (Sveti/Святой- names)
  - Hagiographic place-names (named after saints in OCS form)
- OCS forms vs. vernacular forms help date name creation
- Vikings in Rus' encountered OCS as the prestige written language

Key references:
- Lunt 2001 "Old Church Slavonic Grammar"
- Miklosich 1927 "Die Bildung der slavischen Personen- und Ortsnamen"
- Schuster-Šewc 1978–1996 "Historisch-etymologisches Wörterbuch"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldChurchSlavonicModule(BaseLanguageModule):
    """Language module for Old Church Slavonic toponyms."""

    language_code = "chu"  # ISO 639-3 for Church Slavonic
    language_name = "Old Church Slavonic"
    family = "Indo-European"
    branch = "Slavic > South Slavic (literary standard)"
    period = "863–1100 CE (classical); 1100+ (Church Slavonic recensions)"
    script = "Cyrl/Glag"

    prefixes = [
        "Sveto-",  # holy (Светогорск, church names)
        "Sveti-",  # saint (Свети Влас, Serbian church names)
        "Bogo-",  # God (Богородица, divine names)
        "Blago-",  # blessed (Благовещенск)
        "Preo-",  # most-holy (Преображенск)
        "Voskre-",  # resurrection (Воскресенск)
        "Troic-",  # Trinity (Троицк)
        "Uspen-",  # Dormition (Успенск)
        "Pokrov-",  # Protection/Intercession (Покров)
        "Belo-",  # white (< OCS bělŭ; Белоозеро)
        "Novo-",  # new (< OCS novŭ; Новгород)
        "Staro-",  # old (< OCS starŭ; Старая Ладога)
        "Veliko-",  # great (< OCS velikŭ; Великий Новгород)
    ]

    suffixes = [
        "-grad",  # city (< OCS gradŭ; Белград, Новгород)
        "-gorod",  # city (East Slavic reflex; Новгород)
        "-monastyr",  # monastery
        "-lavra",  # important monastery (Лавра)
        "-pustyn",  # hermitage (пустынь)
        "-pogost",  # churchyard/parish (погост)
        "-cerkov",  # church (церковь)
        "-sobor",  # cathedral (собор)
        "-ozero",  # lake (< OCS ezero; Белоозеро)
        "-pole",  # field (< OCS polje; Чистополь)
        "-gora",  # mountain (< OCS gora; Святогорск)
        "-reka",  # river (< OCS rěka)
        "-selo",  # village (< OCS selo)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "sveto": "holy, sacred (< svętŭ)",
        "sveti": "saint, holy one",
        "bogo": "God (< bogŭ)",
        "blago": "blessed, good (< blagŭ)",
        "preo": "transfiguration, most-holy",
        "voskre": "resurrection (< vŭskrěsenie)",
        "troic": "Trinity (< troica)",
        "uspen": "Dormition (< usŭpenie)",
        "pokrov": "Protection/Intercession of Theotokos",
        "belo": "white (< bělŭ)",
        "novo": "new (< novŭ)",
        "staro": "old (< starŭ)",
        "veliko": "great (< velikŭ)",
        "grad": "city, fortified place (< gradŭ)",
        "gorod": "city (East Slavic form of gradŭ)",
        "ozero": "lake (< ezero)",
        "pole": "field (< polje)",
        "gora": "mountain (< gora)",
        "selo": "village, settlement",
        "pogost": "churchyard, parish center",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an OCS-influenced toponym into components."""
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
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.85,
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
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.85,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
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
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
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
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.85,
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
        """Classify whether a toponym uses OCS ecclesiastical elements."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Church/religious prefixes (very diagnostic of OCS layer)
        ocs_religious = [
            "sveto",
            "sveti",
            "bogo",
            "blago",
            "voskre",
            "troic",
            "uspen",
            "pokrov",
        ]
        for marker in ocs_religious:
            if form_lower.startswith(marker) and len(form_lower) > len(marker):
                evidence.append(f"OCS religious element {marker}-")
                score += 0.45
                break

        # OCS-form suffixes
        ocs_suffixes = ["grad", "gorod", "pogost", "monastyr"]
        for marker in ocs_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"OCS suffix -{marker}")
                score += 0.3
                break

        # OCS qualifiers
        ocs_quals = ["novo", "staro", "veliko", "belo"]
        for marker in ocs_quals:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 2:
                evidence.append(f"OCS qualifier {marker}-")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="863 CE+ (Church Slavonic)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for OCS components."""
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
