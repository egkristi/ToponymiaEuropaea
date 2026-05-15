"""Persian language module for toponymic analysis.

Persian (Fārsi) influenced European toponymy through multiple channels:
- Silk Road trade: Norse/Varangians traded with Persian-speaking merchants
  (rune stones reference "Serkland" = Islamic lands including Persia)
- Via Arabic: Many "Arabic" loanwords in European toponymy are actually Persian
  (e.g., bazar, caravan, khan, shah)
- Via Ottoman Turkish: Ottoman administrative terms are heavily Persian
  (şehir, saray, çeşme, bağ — all Persian origin)
- Via Mongol/Turkic: Steppe empires transmitted Persian terms to Eastern Europe
- Direct Persian substrate: Central Asia, Afghanistan, Tajikistan, parts of Caucasus

Persian elements in European toponymy (via Turkish/Arabic):
- -abad (settlement): widespread in Islamic world
- -istan/-stan (land of): general term
- saray/serai (palace): Aksaray, Sarajevo
- bazar/pazar (market): via Ottoman
- -shahr/-şehir (city): Eskişehir, Bucharest? (disputed)

Key references:
- Steingass 1892 "A Comprehensive Persian-English Dictionary"
- Dehkhoda 1994 "Loghatnāme"
- Kramers 1938 (EI) "Geographical entries" (Encyclopaedia of Islam)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PersianModule(BaseLanguageModule):
    """Language module for Persian-origin toponyms."""

    language_code = "fas"  # ISO 639-3 for Persian
    language_name = "Persian"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Western Iranian"
    period = "Old Persian 525 BCE; Middle Persian 300 BCE–800 CE; New Persian 800 CE–"
    script = "Arab (Perso-Arabic)"

    prefixes = [
        "Shah-",  # king (Shahrud, transmitted as Şah-)
        "Dar-",  # gate, court (Dardanelles? disputed; Darband)
        "Sar-",  # head, top (Saravan, Samarkand?)
        "Deh-",  # village (Dehestan)
        "Rud-",  # river (Shahrud, Harirud)
        "Kuh-",  # mountain (Kuhdasht)
        "Now-",  # new (Nowshahr, Now Deh)
        "Kohn-",  # old (Kohne Shahr)
    ]

    suffixes = [
        "-abad",  # settlement, cultivated place (Islamabad, Hyderabad)
        "-stan",  # land of (Kurdistan, Hindustan, Dagestan)
        "-istan",  # variant
        "-shahr",  # city (Nowshahr; > Turkish -şehir)
        "-kand",  # city (Samarkand, Tashkent < Tash-kand)
        "-kent",  # city (variant; > Turkish)
        "-rud",  # river (Harirud, Shahrud)
        "-darya",  # sea/large river (Amu Darya, Syr Darya)
        "-deh",  # village
        "-kuh",  # mountain
        "-sar",  # head, summit
        "-band",  # dam, closure (Darband = gate-closure)
        "-bagh",  # garden (> Turkish bağ; Baku < Bād-kūbe?)
        "-saray",  # palace (> Turk. saray; Sarajevo < saray + ova)
        "-bazar",  # market (> Turk. pazar; widespread)
        "-khan",  # inn, caravanserai
        "-pul",  # bridge (Pol-e Dokhtar)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "shah": "king, ruler",
        "dar": "gate, door, court (cf. Darius < Dārayavauš)",
        "sar": "head, summit, top",
        "deh": "village",
        "rud": "river, flowing water",
        "kuh": "mountain",
        "now": "new (< Middle Persian nōg)",
        "kohn": "old, ancient",
        "abad": "cultivated place, settlement (< ābād)",
        "stan": "land, place (< IE *steh₂-, stand)",
        "shahr": "city (< Middle Persian šahr < OP xšaθra)",
        "kand": "city, settlement (Sogdian origin)",
        "kent": "city (variant of kand)",
        "darya": "sea, large river (< Old Iranian)",
        "band": "dam, closure, tied",
        "bagh": "garden (< Middle Persian bāg)",
        "saray": "palace, large house (< sarāy)",
        "bazar": "market, marketplace",
        "khan": "inn, caravanserai (< xān)",
        "pul": "bridge (< Middle Persian puhl)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Persian-origin toponym into components."""
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
                    morph_type="compound_head",
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
                    confidence=0.75,
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
        """Classify whether a toponym has Persian origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Highly diagnostic Persian suffixes
        persian_suffixes = ["abad", "stan", "istan", "shahr", "kand", "kent", "darya"]
        for marker in persian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Persian suffix -{marker}")
                score += 0.4
                break

        # Persian elements transmitted via Turkish
        persian_via_turk = ["saray", "bazar", "pazar", "bagh"]
        for marker in persian_via_turk:
            if marker in form_lower:
                evidence.append(f"Persian element '{marker}' (via Turkish)")
                score += 0.25
                break

        # Persian prefixes
        persian_prefixes = ["shah", "sar", "dar", "rud", "kuh"]
        for marker in persian_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Persian prefix {marker}-")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Persian influence (various periods)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Persian components."""
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
