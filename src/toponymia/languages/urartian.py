"""Urartian language module for toponymic analysis.

Urartian (𒌨𒀀𒊑𒋗, xur) is an extinct Hurro-Urartian language of the Kingdom
of Urartu in Eastern Anatolia, Armenia, and NW Iran (860–590 BCE). Key
toponymic patterns: suffixes -ni (locative), -inili (city), -iani (region);
elements -shu/-shini (city), erebu- (seize?). Critical pre-Armenian substrate:
Erebuni → Yerevan, Tushpa → Van. Attested in cuneiform inscriptions.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class UrartianModule(BaseLanguageModule):
    """Language module for Urartian toponyms."""

    language_code = "xur"
    language_name = "Urartian"
    family = "Hurro-Urartian"
    branch = "Urartian"
    period = "Iron Age (860–590 BCE)"
    script = "Xsux"

    prefixes = [
        "Ere-",
        "Ar-",
        "Tur-",
    ]

    suffixes = [
        "-ni",
        "-inili",
        "-iani",
        "-shini",
        "-uni",
        "-nili",
        "-a",
        "-khi",
    ]

    stems = [
        "erebu",
        "tushp",
        "argisht",
        "men",
        "shu",
        "biain",
        "ard",
        "qulh",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "ere": "seize, capture (prefix/root)",
            "ar": "give, grant (prefix/root)",
            "tur": "come, approach (prefix/root)",
            "ni": "locative (in, at)",
            "inili": "city (founded city suffix)",
            "iani": "region, land",
            "shini": "built place / city",
            "uni": "place (locative)",
            "nili": "city (variant)",
            "a": "case ending",
            "khi": "place, land",
            "erebu": "seize (cf. Erebuni)",
            "tushp": "capital (Tushpa = Van)",
            "argisht": "royal name (Argishti)",
            "men": "great, supreme (cf. Menua)",
            "shu": "city, settlement",
            "biain": "Biaini (self-name of Urartu)",
            "ard": "order, arrangement",
            "qulh": "land, territory",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Urartian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 2:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.55,
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
                        confidence=0.7,
                    )
                )
                return results

        pos = len(results)
        results.append(
            SegmentationResult(
                component=form,
                position=pos,
                morph_type="stem",
                confidence=0.3,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Urartian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Urartian suffix -{suffix}")
                score += 0.3
                break

        urartian_markers = ["erebu", "tushp", "argisht", "biain", "menua"]
        for marker in urartian_markers:
            if marker in form_lower:
                evidence.append(f"Known Urartian royal/place name '{marker}'")
                score += 0.4
                break

        if form_lower.endswith(("inili", "shini")):
            evidence.append("Urartian city-founding suffix")
            score += 0.2

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="iron-age",
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "erebu": ("erebu-ni", "capture/seize (fortress name → Yerevan)", ["Hurrian erəb-"]),
            "tushp": ("tušpa", "capital city (→ Van)", []),
            "ni": ("-ni", "locative suffix", ["Hurrian -ni"]),
            "inili": ("-i-ni-li", "city (royal foundation)", ["Hurrian -inili"]),
            "argisht": ("Argišti", "royal name (king Argishti I/II)", []),
            "biain": ("Biainili", "self-name of Urartu", []),
            "men": ("menu-a", "great, supreme (king Menua)", ["Hurrian men-"]),
            "shu": ("šu-", "city/settlement", ["Hurrian šu-"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower().rstrip("-")
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=cognates,
                        sound_changes=["Urartian → Armenian adaptation"],
                        sources=[
                            "Diakonoff, The Pre-history of the Armenian People",
                            "Salvini, Geschichte und Kultur der Urartäer",
                        ],
                    )
                )
        return candidates
