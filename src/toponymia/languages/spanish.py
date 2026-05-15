"""Spanish language module for toponymic analysis.

Spanish (Castilian) toponymy reflects multiple historical layers:
- Pre-Roman substrate (Iberian, Celtic, Basque)
- Roman Latin stratum (major cities, roads)
- Germanic (Visigothic/Suevic) superstrate (5th-8th c.)
- Arabic/Berber superstrate (711-1492, Al-Andalus)
- Romance evolution of all layers
- Viking contact: Norse raids on Iberia 844-1066 (Galicia, Seville)
  - Lordemão (Portugal) < ON Loðinn + maðr
  - Nordoman- place-names in Galicia

Key references:
- Corominas 1972 "Tópica Hespérica"
- Asín Palacios 1940 "Contribución a la toponimia árabe de España"
- Oliver Asín 1973 "En torno a los orígenes de Castilla"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SpanishModule(BaseLanguageModule):
    """Language module for Spanish toponyms."""

    language_code = "spa"  # ISO 639-3 for Spanish
    language_name = "Spanish"
    family = "Indo-European"
    branch = "Romance > Ibero-Romance"
    period = "9th century CE – present"
    script = "Latn"

    prefixes = [
        "Villa-",  # estate, town (Villanueva, Villarreal)
        "Val-",  # valley (Valladolid, Valencia)
        "Monte-",  # mountain (Montevideo, Monteagudo)
        "Fuente-",  # spring (Fuenteovejuna)
        "Piedra-",  # stone (Piedrahíta)
        "Peña-",  # rock, cliff (Peñafiel, Peñaranda)
        "Guadal-",  # river (< Ar. wādī; Guadalquivir)
        "Guada-",  # variant
        "Alcalá-",  # castle (< Ar. al-qal'a)
        "Al-",  # the (< Arabic article; Almería)
        "Bena-",  # son of (< Ar. banī; Benavente?)
        "Torre-",  # tower (Torremolinos)
        "Puente-",  # bridge (Puenteareas)
        "Castil-",  # castle (Castilla, Castilblanco)
    ]

    suffixes = [
        "-abad",  # estate (< Ar. 'abad? or Lat. abbatis; Moratabad)
        "-alba",  # white (Alba de Tormes)
        "-ón",  # augmentative (Gijón, Castellón)
        "-illo",  # diminutive (Portillo, Pradillo)
        "-ejo",  # diminutive/pejorative
        "-uela",  # diminutive (Orihuela, Valenzuela)
        "-edo",  # grove, collective (Oviedo < *Ovetum, Toledo)
        "-eda",  # grove (Arboleda, Olmeda)
        "-osa",  # abundant in (Reinosa)
        "-ica",  # place associated with (Salamanca? debated)
        "-anda",  # pre-Roman suffix (Miranda, Arganda)
        "-ante",  # pre-Roman suffix (Cervantes, Caravante)
        "-iego",  # pertaining to (Goyenechea→Ariñez?)
        "-izar",  # Basque substrate (Amézqueta)
        "-ñón",  # augmentative (Cariñón)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "villa": "estate, settlement, town (< Lat. villa)",
        "val": "valley (< Lat. vallis)",
        "monte": "mountain, woodland (< Lat. mons)",
        "fuente": "spring, fountain (< Lat. fons)",
        "piedra": "stone (< Lat. petra)",
        "peña": "rock, cliff (< Lat. pinna)",
        "guadal": "river (< Arabic wādī al-)",
        "alcalá": "fortress (< Arabic al-qal'a)",
        "torre": "tower (< Lat. turris)",
        "puente": "bridge (< Lat. pons)",
        "castil": "castle (< Lat. castellum)",
        "abad": "abbot's estate or Ar. 'servant'",
        "alba": "white, dawn (< Lat. alba)",
        "edo": "collective grove suffix",
        "eda": "grove, stand of trees",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Spanish toponym into components."""
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
                    confidence=0.75,
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
                    confidence=0.75,
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
        """Classify whether a toponym is likely Spanish."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        spa_prefixes = ["villa", "val", "monte", "fuente", "guadal", "guada", "alcalá", "torre"]
        for marker in spa_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Spanish prefix {marker}-")
                score += 0.35
                break

        # Arabic-origin elements common in Spanish toponymy
        arabic_markers = ["guadal", "guada", "alcalá", "al", "bena"]
        for marker in arabic_markers:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 2:
                if marker not in [e.split()[-1] for e in evidence]:
                    evidence.append(f"Arabic substrate element {marker}-")
                    score += 0.2
                break

        # Spanish phonology markers
        if "ñ" in form_lower:
            evidence.append("Spanish ñ")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="9th century – present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Spanish components."""
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
