"""Norman/Old French language module for toponymic analysis.

Norman French (Normand) is CRITICAL for Nordic toponymy because the
Normans were literally Norsemen — Rollo's Vikings settled in Normandy
(911 CE Treaty of Saint-Clair-sur-Epte) and their descendants spread:
- Normandy: Norse + French hybrid toponymy (Dieppe < ON djúpr, Honfleur < ON flóð)
- England after 1066: massive French renaming layer (Beaumont, Richmond)
- Sicily/Southern Italy: Norman kingdom (1071–1194)
- Crusader States: Outremer (1098–1291)
- The "Norman" suffix patterns spread across 4 countries

Scandinavian elements preserved in Norman French:
- -bec (< ON bekkr, stream): Caudebec, Bolbec
- -fleur (< ON flóð/fleyr, tidal inlet): Honfleur, Barfleur, Harfleur
- -tot/-toft (< ON toft, homestead): Yvetot, Lanquetot
- -beuf (< ON bú/bóð, dwelling): Elbeuf, Quillebeuf
- -dalle (< ON dalr, valley): Dieppedalle, Oudalle
- -hogue/-hague (< ON haugr, mound): La Hague, La Hougue

Key references:
- Adigard des Gautries 1954 "Les noms de personnes scandinaves en Normandie"
- de Beaurepaire 1986 "Les noms des communes de la Seine-Maritime"
- Fellows-Jensen 1985 "Scandinavian settlement in England: the place-name evidence"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class NormanFrenchModule(BaseLanguageModule):
    """Language module for Norman/Old French toponyms."""

    language_code = "fro"  # ISO 639-3 for Old French
    language_name = "Norman French"
    family = "Indo-European"
    branch = "Romance > Gallo-Romance > Oïl > Norman"
    period = "911–1500 CE"
    script = "Latn"

    prefixes = [
        "Beau-",  # beautiful (Beaumont, Beaulieu)
        "Bel-",  # beautiful (variant; Belvoir)
        "Mont-",  # mountain (Montfort, Montgomery)
        "Font-",  # spring (Fontenay, Fontainebleau)
        "Pont-",  # bridge (Pontefract, Pontoise)
        "Grand-",  # great (Grandcamp, Grandville)
        "Neuf-",  # new (Neufchâtel, Neufbourg)
        "Vieux-",  # old (Vieux-Pont, Vieux-Rouen)
        "Haut-",  # high (Hauterive, Hauteville)
        "Riche-",  # rich/powerful (Richmond)
    ]

    suffixes = [
        # Norse-origin suffixes in Normandy
        "-bec",  # stream (< ON bekkr; Caudebec, Bolbec)
        "-beuf",  # dwelling (< ON bú/bóð; Elbeuf, Quillebeuf)
        "-fleur",  # tidal inlet (< ON flóð; Honfleur, Barfleur)
        "-tot",  # homestead (< ON toft; Yvetot, Lanquetot)
        "-toft",  # variant (Lowestoft in England)
        "-dalle",  # valley (< ON dalr; Dieppedalle)
        "-hogue",  # mound (< ON haugr; La Hougue)
        "-hague",  # enclosure (< ON hagi; La Hague)
        "-londe",  # grove (< ON lundr; La Londe, Boolonde)
        "-thuit",  # clearing (< ON þveit; Bracquetuit)
        # French-origin suffixes
        "-ville",  # town (< Lat. villa; Deauville, Granville)
        "-mont",  # mountain (Beaumont, Claremont)
        "-court",  # farmstead (< Lat. curtis; Harcourt)
        "-mesnil",  # homestead (< Lat. mansionile; Le Mesnil)
        "-mare",  # pond (< ON marr; Caumare, Étremare)
        "-ey",  # island (< ON ey; Jersey, Guernsey)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "beau": "beautiful, fine (< Lat. bellus)",
        "bel": "beautiful (variant)",
        "mont": "mountain, hill (< Lat. mons)",
        "font": "spring, fountain (< Lat. fons)",
        "pont": "bridge (< Lat. pons)",
        "grand": "great, large",
        "neuf": "new (< Lat. novus)",
        "haut": "high (< Lat. altus)",
        "riche": "rich, powerful (< Frankish rīki)",
        "bec": "stream (< ON bekkr)",
        "beuf": "dwelling (< ON bú/bóð)",
        "fleur": "tidal inlet (< ON flóð, NOT flower)",
        "tot": "homestead (< ON toft)",
        "dalle": "valley (< ON dalr)",
        "hogue": "mound, hillock (< ON haugr)",
        "hague": "enclosure (< ON hagi)",
        "londe": "grove, wood (< ON lundr)",
        "thuit": "clearing (< ON þveit)",
        "ville": "town, estate (< Lat. villa)",
        "court": "farmstead (< Lat. curtis)",
        "mesnil": "homestead, manor (< Lat. mansionile)",
        "mare": "pond, pool (< ON marr/Gmc *mari)",
        "ey": "island (< ON ey)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Norman French toponym into components."""
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
        """Classify whether a toponym is likely Norman French."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Norse-Norman hybrid suffixes (very diagnostic)
        norse_norman = ["bec", "beuf", "fleur", "tot", "dalle", "hogue", "hague", "londe", "thuit"]
        for marker in norse_norman:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Norse-Norman suffix -{marker}")
                score += 0.45
                break

        # French suffixes
        french_suffixes = ["ville", "mont", "court", "mesnil"]
        for marker in french_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Norman French suffix -{marker}")
                score += 0.3
                break

        # Norman French prefixes
        norman_prefixes = ["beau", "bel", "mont", "pont", "neuf", "haut"]
        for marker in norman_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Norman prefix {marker}-")
                score += 0.25
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="911–1500 CE (Norman)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Norman French components."""
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
