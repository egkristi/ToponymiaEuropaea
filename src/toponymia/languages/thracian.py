"""Thracian language module for toponymic analysis.

Thracian (txh) is an IE (satem) language spoken in the Balkans from the 2nd
millennium BCE until the 6th c. CE. Poorly attested (glosses, names, ~20 short
inscriptions). Major Balkan toponymic substrate.

Toponymic hallmarks:
- Suffixes: -diza (fortress), -bria (city), -para (river settlement),
  -dava (stronghold, shared with Dacian?)
- Philippopolis (Plovdiv), Serdica (Sofia), Bizye (Vize)
- Satem language: *k̑ > s, *g̑ > z
- Important substrate in Bulgarian/Greek Thrace place-names

Key references: Duridanov 1985 "Die Sprache der Thraker",
Detschew 1957 "Die thrakischen Sprachreste"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "diza": "fortress / fortified place",
    "bria": "city / town",
    "para": "river settlement / ford",
    "dava": "stronghold (shared with Dacian)",
    "aba": "water / river",
    "upa": "water / river",
    "sura": "strong / salt",
    "ula": "diminutive / place",
    "issa": "place suffix",
}

_PREFIXES: dict[str, str] = {
    "sar": "head / chief (< *ser- 'flow'?)",
    "ber": "marsh / carry (< *bher-)",
    "din": "fort / hill",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "serdica": ("serdica", "Serdica (Sofia, < tribe Serdi)"),
    "philippopolis": ("philippopolis", "Plovdiv (Greek rename of Pulpudeva)"),
    "pulpudeva": ("pulpudeva", "Plovdiv (Thracian: 'Philip's city')"),
    "bizye": ("bizye", "Bizye (Vize, < *biz- ?)"),
    "kabyle": ("kabyle", "Kabyle (< *kab- 'height'?)"),
    "beroe": ("beroe", "Beroe (Stara Zagora)"),
    "mesembria": ("mesembria", "Mesembria (Nesebar, 'Melsas city')"),
    "selymbria": ("selymbria", "Selymbria (Silivri)"),
    "tylis": ("tylis", "Tylis (Thracian kingdom in Anatolia)"),
    "uskudama": ("uskudama", "Uskudama (Edirne/Adrianople)"),
    "deultum": ("deultum", "Deultum (< *deul- ?)"),
    "nicopolis": ("nicopolis", "Nicopolis ad Istrum"),
}

_PHONOLOGICAL_MARKERS = {"dz", "zd", "sk", "br"}


class ThracianModule(BaseLanguageModule):
    """Language module for Thracian (txh) toponyms."""

    language_code = "txh"
    language_name = "Thracian"
    family = "Indo-European"
    branch = "Satem (Daco-Thracian?)"
    period = "2nd millennium BCE – 6th c. CE"
    script = "Grek"

    suffixes = list(_SUFFIXES.keys())
    prefixes = list(_PREFIXES.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        if fl in _KNOWN_ELEMENTS:
            lemma, meaning = _KNOWN_ELEMENTS[fl]
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=lemma,
                    meaning=meaning,
                    confidence=0.75,
                )
            )
            return results

        pos = 0
        for pfx, meaning in sorted(_PREFIXES.items(), key=lambda x: -len(x[0])):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                results.append(
                    SegmentationResult(
                        component=form[: len(pfx)],
                        position=pos,
                        morph_type="prefix",
                        lemma=pfx,
                        meaning=meaning,
                        confidence=0.5,
                    )
                )
                form = form[len(pfx) :]
                fl = fl[len(pfx) :]
                pos += 1
                break

        matched_suffix = ""
        matched_meaning = ""
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                matched_suffix = sfx
                matched_meaning = meaning
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            sfx_part = form[len(form) - len(matched_suffix) :]
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
                    component=sfx_part,
                    position=pos + 1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_meaning,
                    confidence=0.6,
                )
            )
        else:
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
        fl = form.lower()
        score = 0.0
        evidence: list[str] = []

        if fl in _KNOWN_ELEMENTS:
            score += 0.7
            evidence.append(f"Known Thracian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.35
                evidence.append(f"Thracian suffix -{sfx}")
                break

        for pfx in _PREFIXES:
            if fl.startswith(pfx):
                score += 0.15
                evidence.append(f"Thracian prefix {pfx}-")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Thracian phonological cluster '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="thracian" if score > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            cl = comp.component.lower()
            if cl in _KNOWN_ELEMENTS:
                lemma, meaning = _KNOWN_ELEMENTS[cl]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=[],
                        sound_changes=["satem: *k̑ > s"],
                        sources=["Duridanov 1985", "Detschew 1957"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=[],
                        sources=["Detschew 1957"],
                    )
                )
        return candidates
