"""Russian (русский) language module for toponymic analysis.

Russian toponymy reflects the vast geographic extent of Slavic settlement
from Novgorod to Vladivostok:
- Possessive suffixes: -ov/-ev, -in/-ino (from personal names)
- Locative suffixes: -sk/-ск, -grad/-gorod (fortified town)
- Topographic roots: река (river), озеро (lake), гора (mountain)
- Finno-Ugric substrata in northern regions (-ma, -ga, -ks)
- Turkic substrata in southern/eastern regions (-su, -dag)

Key references:
- Vasmer 1953–1958 "Russisches Etymologisches Wörterbuch"
- Pospelov 2002 "Geograficheskie nazvaniya mira"
- Nikonov 1966 "Kratkij toponimicheskij slovar'"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class RussianModule(BaseLanguageModule):
    """Language module for Russian toponyms."""

    language_code = "rus"
    language_name = "Russian"
    family = "Indo-European"
    branch = "Slavic > East Slavic"
    period = "1100 CE–present"
    script = "Cyrl"

    prefixes = [
        "Novo-",  # new (Novosibirsk)
        "Staro-",  # old (Staroye)
        "Bolsho-",  # great (Bolshoye)
        "Malo-",  # small (Maloye)
        "Belo-",  # white (Belgorod)
        "Cherno-",  # black (Chernigov)
        "Krasno-",  # red/beautiful (Krasnodar)
        "Verkh-",  # upper (Verkhoyansk)
        "Nizh-",  # lower (Nizhny Novgorod)
        "Pod-",  # under (Podolsk)
        "Za-",  # beyond (Zagorsk)
        "Ust-",  # mouth of river (Ust-Kamenogorsk)
        "Sredne-",  # middle (Sredneuralsk)
        "Severo-",  # north (Severodvinsk)
        "Yuzhno-",  # south (Yuzhno-Sakhalinsk)
    ]

    suffixes = [
        "-ov",  # possessive masculine (Petrov, Pskov)
        "-ovo",  # possessive neuter (Domodedovo)
        "-ev",  # possessive soft stem (Medvedev)
        "-evo",  # possessive neuter soft (Sheremetyevo)
        "-in",  # possessive feminine (Pushkin)
        "-ino",  # possessive neuter feminine (Tsaritsino)
        "-sk",  # adjectival (Novosibirsk, Smolensk)
        "-skiy",  # adjectival long form
        "-skoye",  # neuter adjectival (Tsarskoye Selo)
        "-gorod",  # city (Novgorod, Volgograd)
        "-grad",  # city (Leningrad, Volgograd)
        "-gorsk",  # city on mountain
        "-sk",  # city/town
        "-ka",  # diminutive (Moskva→Moskovka)
        "-ki",  # plural (Lyubertsy)
        "-tsy",  # plural of inhabitants
        "-tsevo",  # possessive from -ts root
        "-ovka",  # settlement (Petrovka)
        "-evka",  # settlement (soft stem)
        "-inka",  # diminutive settlement
        "-yata",  # patronymic plural
        "-ichi",  # patronymic plural (south)
        "-itsy",  # patronymic plural
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "novo": "new",
        "staro": "old",
        "bolsho": "great, large",
        "malo": "small, little",
        "belo": "white, bright",
        "cherno": "black, dark",
        "krasno": "red, beautiful",
        "verkh": "upper, top",
        "nizh": "lower, bottom",
        "ust": "mouth (of river)",
        "sredne": "middle",
        "severo": "north",
        "yuzhno": "south",
        "gorod": "city, fortified town",
        "grad": "city (elevated style)",
        "reka": "river",
        "ozero": "lake",
        "gora": "mountain, hill",
        "pole": "field",
        "les": "forest",
        "bor": "pine forest",
        "dol": "valley, dale",
        "yar": "ravine, steep bank",
        "kamen": "stone, rock",
        "volok": "portage, watershed",
        "ostrov": "island",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Russian toponym into morphological components."""
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
        """Classify whether a toponym is likely Russian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        russian_suffixes = [
            "gorod",
            "grad",
            "gorsk",
            "ovka",
            "evka",
            "ovo",
            "evo",
            "ino",
            "sk",
            "tsy",
        ]
        for marker in russian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Russian suffix -{marker}")
                score += 0.3
                break

        russian_prefixes = ["novo", "staro", "belo", "cherno", "krasno", "verkh", "nizh", "ust"]
        for marker in russian_prefixes:
            if form_lower.startswith(marker):
                evidence.append(f"Russian prefix {marker}-")
                score += 0.3
                break

        # Cyrillic transliteration patterns
        russian_patterns = ["zh", "shch", "kh", "ts"]
        for pat in russian_patterns:
            if pat in form_lower:
                evidence.append(f"Russian phonetic pattern '{pat}'")
                score += 0.1
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1100–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented Russian components."""
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
