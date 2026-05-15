"""Italian (italiano) language module for toponymic analysis.

Italian toponymy reflects rich historical layering:
- Pre-Indo-European substrata (Etruscan, Ligurian, Sardinian)
- Latin: -anum > -ano (Bassano), -anum > -ana (Ancona)
- Greek (Southern Italy): -polis, -cala
- Germanic (Lombard): -engo, -ingo (Marengo, Gallarate)
- Arabic (Sicily): -caltà, -giblì (Caltanissetta, Gibellina)

Key references:
- Pellegrini 1990 "Toponomastica italiana"
- Gasca Queirazza 1997 "Dizionario di toponomastica"
- Rohlfs 1972 "Studi e ricerche su lingua e dialetti d'Italia"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ItalianModule(BaseLanguageModule):
    """Language module for Italian toponyms."""

    language_code = "ita"
    language_name = "Italian"
    family = "Indo-European"
    branch = "Italic > Romance > Italo-Romance"
    period = "900 CE–present"
    script = "Latn"

    prefixes = [
        "San-",  # saint (San Marino, San Gimignano)
        "Santa-",  # saint feminine (Santa Croce)
        "Santo-",  # saint (Santo Stefano)
        "Monte-",  # mountain (Montepulciano)
        "Castel-",  # castle (Castelfranco)
        "Campo-",  # field (Campobasso)
        "Fonte-",  # spring (Fontebuona)
        "Torre-",  # tower (Torrevieja)
        "Porta-",  # gate (Portofino)
        "Pietra-",  # stone (Pietrasanta)
        "Rocca-",  # fortress/rock (Roccaraso)
        "Villa-",  # villa, estate (Villafranca)
        "Bella-",  # beautiful (Bellagio)
        "Porto-",  # port (Portoferraio)
    ]

    suffixes = [
        "-ano",  # Latin -anum (Milano, Bassano)
        "-ana",  # Latin -anum fem. (Ancona variant)
        "-ino",  # diminutive (Torino)
        "-ina",  # diminutive feminine (Messina)
        "-one",  # augmentative (Rimini→Ariminum)
        "-eto",  # collective (Oliveto = olive grove)
        "-ata",  # collective/action (Vallata)
        "-ello",  # diminutive (Montecatini)
        "-ella",  # diminutive feminine (Viareggio variant)
        "-asco",  # Ligurian/pre-Roman (Monacco, Benasco)
        "-asca",  # Ligurian feminine
        "-engo",  # Lombard/Germanic (Marengo)
        "-ate",  # collective (Gallarate, Lissone variant)
        "-ago",  # Celtic -acum (Asiago)
        "-igo",  # variant (Lavigo)
        "-opoli",  # city (Greek: Gallipoli)
        "-poli",  # city (Napoli, Tripoli)
        "-onte",  # mountain variant
        "-ento",  # water/wind (Salento, Benevento)
        "-erno",  # place (Salerno)
        "-etta",  # diminutive (Molfetta)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "san": "saint",
        "santa": "saint (feminine)",
        "santo": "saint (masculine)",
        "monte": "mountain, hill",
        "castel": "castle, fortified place",
        "campo": "field, plain",
        "fonte": "spring, fountain",
        "torre": "tower",
        "porta": "gate, port",
        "pietra": "stone, rock",
        "rocca": "fortress, cliff",
        "villa": "villa, estate",
        "bella": "beautiful",
        "porto": "port, harbour",
        "fiume": "river",
        "lago": "lake",
        "mare": "sea",
        "isola": "island",
        "bosco": "wood, forest",
        "prato": "meadow",
        "valle": "valley",
        "piano": "plain",
        "colle": "hill",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Italian toponym into morphological components."""
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
                    confidence=0.85,
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
        """Classify whether a toponym is likely Italian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        if form_lower.startswith(("san ", "san-", "santa", "santo")):
            evidence.append("Italian 'San/Santa/Santo' prefix")
            score += 0.4

        italian_suffixes = ["ano", "ino", "eto", "ello", "ella", "engo", "asco", "opoli"]
        for marker in italian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 2:
                evidence.append(f"Italian suffix -{marker}")
                score += 0.3
                break

        italian_prefixes = ["monte", "castel", "campo", "porto", "pietra", "rocca"]
        for marker in italian_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker):
                evidence.append(f"Italian prefix {marker}-")
                score += 0.3
                break

        # Double consonants are common in Italian
        doubles = ["ll", "tt", "rr", "nn", "ss", "cc", "pp", "zz"]
        for d in doubles:
            if d in form_lower:
                evidence.append(f"Italian double consonant '{d}'")
                score += 0.1
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="900–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Italian components."""
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
