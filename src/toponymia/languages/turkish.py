"""Turkish/Ottoman language module for toponymic analysis.

Ottoman Turkish toponymy is essential for Balkan and Eastern Mediterranean
place-name studies:
- Ottoman Empire controlled the Balkans for 400-500 years (14th-19th c.)
- Massive renaming: Slavic/Greek/Albanian places got Turkish names
- Many European cities retain Turkish-origin names or dual names
- Relevant for Viking studies: Varangians traveled through Ottoman-era
  territories; Norse rune stones reference Serkland (Islamic lands)
- Turkish substrate in Bulgarian, Serbian, Greek, Albanian toponymy

Key references:
- Eren 1999 "Türk Dilinin Etimolojik Sözlüğü"
- Kowalski 1933 "Les Turcs et la langue turque de la Bulgarie du Nord-Est"
- Šabanović 1959 "Bosanski pašaluk"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class TurkishModule(BaseLanguageModule):
    """Language module for Turkish/Ottoman toponyms."""

    language_code = "ota"  # ISO 639-3 for Ottoman Turkish
    language_name = "Ottoman Turkish"
    family = "Turkic"
    branch = "Oghuz > Western Oghuz"
    period = "1299–1922 CE (Ottoman); 1923– (Republic)"
    script = "Latn (modern) / Arab (Ottoman)"

    prefixes = [
        "Kara-",  # black (Karadeniz, Karaman)
        "Ak-",  # white (Akdeniz, Aksaray)
        "Yeşil-",  # green (Yeşilırmak)
        "Kızıl-",  # red (Kızılırmak)
        "Büyük-",  # great (Büyükada)
        "Küçük-",  # small (Küçükçekmece)
        "Yeni-",  # new (Yenişehir)
        "Eski-",  # old (Eskişehir)
        "Demir-",  # iron (Demirkapı)
        "Bey-",  # lord (Beyoğlu, Beykoz)
        "Gül-",  # rose (Güllük)
        "Taş-",  # stone (Taşkent, Taşlıca)
    ]

    suffixes = [
        "-hisar",  # fortress (Rumelihisarı, Anadoluhisarı)
        "-köy",  # village (Arnavutköy, Beşiktaş)
        "-dağ",  # mountain (Uludağ, Kaçkardağı)
        "-dağı",  # mountain (possessive)
        "-tepe",  # hill (Maltepe, Çataltepe)
        "-burnu",  # cape, nose (Sarayburnu)
        "-suyu",  # water/river (possessive)
        "-ova",  # plain (Sakarova, but also Slavic!)
        "-pazar",  # market (Uzunpazar)
        "-saray",  # palace (Aksaray, Beylerbeyi Sarayı)
        "-kale",  # castle (< Gr. kalon? or Turkic)
        "-kent",  # city (Taşkent)
        "-şehir",  # city (< Per. shahr; Eskişehir)
        "-bağ",  # garden (vineyard)
        "-çeşme",  # fountain (< Per. chashma; Çeşme)
        "-pınar",  # spring (Pınarbaşı)
        "-göl",  # lake (Burdur Gölü)
        "-dere",  # valley, stream (Kuşdere)
        "-ada",  # island (Büyükada)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "kara": "black, dark; also: land, earth",
        "ak": "white, bright; also: flowing",
        "yeşil": "green",
        "kızıl": "red, reddish",
        "büyük": "great, large",
        "küçük": "small, little",
        "yeni": "new",
        "eski": "old",
        "demir": "iron",
        "bey": "lord, chief",
        "gül": "rose",
        "taş": "stone",
        "hisar": "fortress, castle",
        "köy": "village",
        "dağ": "mountain",
        "tepe": "hill, mound",
        "burnu": "cape, headland (lit. nose)",
        "ova": "plain, lowland",
        "pazar": "market (< Per. bāzār)",
        "saray": "palace (< Per. sarāy)",
        "kale": "castle, fortification",
        "kent": "city (< Sogdian/Persian)",
        "şehir": "city (< Per. shahr)",
        "çeşme": "fountain, spring (< Per.)",
        "pınar": "spring, source",
        "göl": "lake",
        "dere": "valley, stream, ravine",
        "ada": "island",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Turkish toponym into components."""
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
        """Classify whether a toponym is likely Turkish/Ottoman."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        turk_suffixes = [
            "hisar",
            "köy",
            "dağ",
            "dağı",
            "tepe",
            "şehir",
            "kale",
            "kent",
            "göl",
            "dere",
        ]
        for marker in turk_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Turkish suffix -{marker}")
                score += 0.4
                break

        turk_prefixes = ["kara", "ak", "kızıl", "yeşil", "yeni", "eski", "büyük", "küçük"]
        for marker in turk_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Turkish prefix {marker}-")
                score += 0.3
                break

        # Turkish-specific characters
        turk_chars = ["ş", "ç", "ğ", "ı", "ö", "ü"]
        for ch in turk_chars:
            if ch in form_lower:
                evidence.append(f"Turkish orthography '{ch}'")
                score += 0.15
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1299–1922 CE (Ottoman)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Turkish components."""
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
