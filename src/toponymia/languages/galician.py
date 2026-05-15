"""Galician language module for toponymic analysis.

Galician (galego) is critical for Norse-Iberian contact studies because
Galicia was the PRIMARY target of Viking raids on the Iberian Peninsula:

Norse/Viking contact in Galicia (844–1066 CE):
- First raid: 844 CE on the Galician coast (before Seville)
- Major campaigns: 858–861 (Björn Ironside & Hastein)
- Repeated raids throughout 10th–11th centuries
- Attempted settlements in Ría de Arousa area
- "Normandos" place-names across coastal Galicia
- The Diocese of Iria Flavia (now Padrón) recorded Norse attacks

Specific Norse traces in Galician toponymy:
- Lordemão/Normannorum references in medieval documents
- Ría de Arousa: possible temporary Norse settlement
- Cedofeita (Porto/N.Galicia): possibly < *cito facta (quickly built;
  legend says rebuilt quickly after Norse destruction)
- Toponímia "dos normandos" along Rías Baixas
- Portonovo, Vilanova de Arousa area: raided repeatedly
- Catoira: site of defensive Torres de Oeste against Norse

Galician-Norwegian connections beyond Vikings:
- Camino de Santiago pilgrimage from Scandinavia (medieval)
- Maritime trade (fish, wine, salt) Bergen→Galicia→Norway
- Shared Atlantic maritime vocabulary
- Similar ría/fjord coastal geography creating parallel naming

Galician as a language:
- Medieval Galician-Portuguese (same language until ~14th c.)
- Diverged from Portuguese after political separation
- Celtic substrate (Gallaeci were Celtic; cf. Welsh Cymru)
- Latin/Romance main layer
- Germanic (Suevic) superstrate in NW Iberia specifically

Key references:
- Piel 1937 "Os nomes germânicos na toponímia portuguesa"
- Baliñas 2004 "Gallegos del año mil"
- Almazán 1986 "Gallaecia Scandinavica"
- Christys 2015 "Vikings in the South"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class GalicianModule(BaseLanguageModule):
    """Language module for Galician toponyms."""

    language_code = "glg"  # ISO 639-3
    language_name = "Galician"
    family = "Indo-European"
    branch = "Romance > Ibero-Romance > Galician-Portuguese > Galician"
    period = "Medieval (9th c.) – present; Celtic substrate from 1st millennium BCE"
    script = "Latn"

    prefixes = [
        "Vila-",  # town (Vilagarcía, Vilanova)
        "San-",  # saint (Santiago, San Martiño)
        "Santa-",  # saint (Santa Comba)
        "Ponte-",  # bridge (Pontevedra, Ponteareas)
        "Porto-",  # port (Portonovo, Portosín)
        "Monte-",  # mountain (Monterrei)
        "Fonte-",  # spring (Fontefría)
        "Val-",  # valley (Valdeorras)
        "Cas-",  # house (Castiñeiras)
        "Ría-",  # estuary (unique Galician geographic feature)
        "Foz-",  # mouth (Foz, Fozcara)
        "Pena-",  # rock (Peñarrubia; < Celtic *penna)
        "Castro-",  # hillfort (< Celtic *castron; Castro Caldelas)
        "Coto-",  # hillock, knoll (Cotobade)
    ]

    suffixes = [
        # Celtic substrate (pre-Roman)
        "-briga",  # fortification (< Celtic *briga; Nemetobriga)
        "-bre",  # < Celtic *briga reduced (Monforte → not, but Alcabre)
        # Latin/Romance
        "-eiro",  # place/person of (Ribadeiro, Outeiro)
        "-eira",  # feminine (Oliveira, Ribeira)
        "-ós",  # Latin -osus abundance (Quirós, Valdoviñós?)
        "-ín",  # diminutive (Marín, Cambriñó)
        "-iño",  # diminutive (Camiño, Cariño)
        "-ón",  # augmentative (Gijón [Asturian], Padrón)
        "-ás",  # place plural (Ponteareas)
        "-ade",  # < Latin -ate (Saudade)
        "-ño",  # diminutive (Caramiñal)
        # Germanic (Suevic) superstrate
        "-mil",  # < Germanic *-helm? (Gondomar < Gunde-mir?)
        "-monde",  # < Germanic *mund (Redondela? debated)
        "-riz",  # < Germanic *-riks (Guitiriz < Gothic Witteriks?)
        # Norse contact traces
        "-mão",  # < ON maðr? (Lordemão)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "vila": "town, estate (< Lat. villa)",
        "ponte": "bridge (< Lat. pons; Pontevedra = 'old bridge')",
        "porto": "port, harbor (< Lat. portus)",
        "fonte": "spring, fountain (< Lat. fons)",
        "val": "valley (< Lat. vallis)",
        "ría": "coastal estuary (Galician geographic term; cf. fjord)",
        "foz": "river mouth (< Lat. fauces)",
        "pena": "rock, cliff (< Celtic *penna; extensive in Galicia)",
        "castro": "hillfort (< Celtic *castron; pre-Roman settlement type)",
        "coto": "hillock, rounded hill (Celtic substrate?)",
        "briga": "fortified height (Celtic; cf. -burg Germanic)",
        "eiro": "place associated with (< Lat. -arium)",
        "lama": "mudflat, marshland (Celtic/pre-Roman)",
        "carballeira": "oak grove (< Celtic *carballo 'oak')",
        "carballo": "oak (< Celtic; Galician national tree)",
        "agra": "cultivated field (Celtic substrate)",
        "toxo": "gorse (characteristic Galician landscape plant)",
        "outeiro": "hillock, mound (< Lat. altarium)",
        "normando": "Norseman (< Lat. Northmannus; Viking reference)",
    }

    # Known Norse contact names in Galicia
    NORSE_CONTACT_NAMES: dict[str, str] = {
        "lordemão": "< ON Loðinn + maðr (Norse personal name compound)",
        "normando": "place-names referencing Norse/Viking raiders",
        "catoira": "site of Torres de Oeste, anti-Norse fortification",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Galician toponym into components."""
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

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                meaning = self.ELEMENT_MEANINGS.get(suffix, "")
                results.append(
                    SegmentationResult(
                        segments=[stem, suffix],
                        language=self.language_code,
                        confidence=0.7,
                        notes=f"Galician: '{stem}' + '-{suffix}' ({meaning})",
                    )
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                meaning = self.ELEMENT_MEANINGS.get(prefix, "")
                results.append(
                    SegmentationResult(
                        segments=[prefix, remainder],
                        language=self.language_code,
                        confidence=0.65,
                        notes=(f"Galician prefix '{prefix}' ({meaning}) + '{remainder}'"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Galician."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Galician-specific suffixes
        gal_suffixes = ["eiro", "eira", "iño", "ás", "bre"]
        for suf in gal_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Galician suffix '-{suf}'")
                score += 0.45
                break

        # Celtic substrate markers (pre-Roman)
        celtic_elements = ["castro", "briga", "coto", "carballo", "lama"]
        for elem in celtic_elements:
            if elem in form_lower:
                evidence.append(f"Celtic substrate element '{elem}'")
                score += 0.4
                break

        # Galician orthographic markers (ñ, distinctive from Portuguese)
        if "ñ" in form_lower:
            evidence.append("Galician orthography (ñ)")
            score += 0.15

        # Ría geographic feature (unique Galician term)
        if "ría" in form_lower or form_lower.startswith("ria"):
            evidence.append("Galician 'ría' (coastal estuary; cf. Norwegian fjord)")
            score += 0.4

        # Norse contact markers
        for name, desc in self.NORSE_CONTACT_NAMES.items():
            if name in form_lower:
                evidence.append(f"Norse contact trace: {desc}")
                score += 0.5
                break

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Galician etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.6,
                        notes=f"Galician element '{element}' in '{form}'",
                    )
                )

        return candidates
