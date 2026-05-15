"""Old English (Anglo-Saxon) language module for toponymic analysis.

Old English toponymy is crucial for understanding Norse-English contact
in the Danelaw (c. 865–954 CE):
- Norse-English hybrid names: Grimston (ON Grímr + OE tūn)
- Scandinavian substitution: -by replacing -tūn, -thwaite for -lēah
- Distinctive OE elements: -tūn (farm), -hām (homestead), -lēah (clearing)
- Phonological markers: OE /tʃ/ (church) vs ON /k/ (kirk)
- River names from Celtic (Avon, Thames) preserved through OE

Key references:
- Smith 1956 "English Place-Name Elements" (EPNS vols 25–26)
- Gelling & Cole 2000 "The Landscape of Place-Names"
- Fellows-Jensen 1972 "Scandinavian Settlement Names in Yorkshire"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldEnglishModule(BaseLanguageModule):
    """Language module for Old English (Anglo-Saxon) toponyms."""

    language_code = "ang"  # ISO 639-3 for Old English
    language_name = "Old English"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Anglo-Frisian"
    period = "450–1100 CE"
    script = "Latn"

    prefixes = [
        "East-",  # east (Easton)
        "West-",  # west (Weston)
        "North-",  # north (Norton)
        "South-",  # south (Sutton < sūþ+tūn)
        "Great-",  # great (< grēat)
        "Little-",  # little (< lȳtel)
        "Long-",  # long (Longford)
        "Broad-",  # broad (Bradford)
        "High-",  # high (Highgate)
        "New-",  # new (< nīwe; Newcastle)
        "Old-",  # old (< eald; Oldham)
        "King-",  # king (< cyning; Kingston)
        "Bishop-",  # bishop (< biscop; Bishopstoke)
        "Ash-",  # ash tree (< æsc; Ashford)
        "Oak-",  # oak (< āc; Oakland)
    ]

    suffixes = [
        "-ton",  # farmstead, village (< tūn; most common)
        "-tun",  # variant spelling
        "-ham",  # homestead, village (< hām; Birmingham)
        "-ley",  # clearing, meadow (< lēah; Burnley)
        "-leigh",  # variant of -ley
        "-stead",  # place (< stede; Hampstead)
        "-ford",  # river crossing (< ford; Oxford)
        "-bury",  # fortified place (< burh; Canterbury)
        "-borough",  # variant of -bury (Marlborough)
        "-burgh",  # variant (Edinburgh—though Gaelic)
        "-worth",  # enclosure (< worþ; Tamworth)
        "-wick",  # farm, dwelling (< wīc; Warwick)
        "-field",  # open land (< feld; Sheffield)
        "-hurst",  # wooded hill (< hyrst; Sandhurst)
        "-den",  # valley, pasture (< denu; Tenterden)
        "-combe",  # short valley (< cumb; Ilfracombe)
        "-stow",  # holy place, meeting place (< stōw; Felixstowe)
        "-minster",  # monastery (< mynster; Westminster)
        "-church",  # church (< cirice; Christchurch)
        "-bridge",  # bridge (< brycg; Cambridge)
        "-well",  # spring (< wella; Hartlepool variant)
        "-pool",  # pool (< pōl; Liverpool)
        "-mouth",  # river mouth (< mūþ; Plymouth)
        "-borne",  # stream (< burna; Eastbourne)
        "-cot",  # cottage (< cot; Didcot)
        "-cote",  # variant (Dovecote)
        "-stead",  # place (Homestead)
        "-stoke",  # place, outlying farm (< stoc; Basingstoke)
        "-ing",  # people of (< -ingas; Reading)
        "-ingham",  # homestead of X's people
        "-ington",  # farm of X's people
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ton": "farmstead, village (tūn)",
        "tun": "farmstead, village",
        "ham": "homestead, village (hām)",
        "ley": "woodland clearing (lēah)",
        "leigh": "woodland clearing",
        "stead": "place, site (stede)",
        "ford": "river crossing",
        "bury": "fortified place (burh)",
        "borough": "fortified place",
        "worth": "enclosure (worþ)",
        "wick": "farm, dairy farm (wīc)",
        "field": "open land (feld)",
        "hurst": "wooded hill (hyrst)",
        "den": "valley, woodland pasture (denu)",
        "combe": "short valley (cumb)",
        "stow": "holy place, meeting place (stōw)",
        "minster": "monastery (mynster)",
        "church": "church (cirice)",
        "bridge": "bridge (brycg)",
        "well": "spring, stream (wella)",
        "pool": "pool, harbour (pōl)",
        "mouth": "river mouth (mūþ)",
        "borne": "stream (burna)",
        "cot": "cottage, shelter",
        "stoke": "outlying farm (stoc)",
        "ing": "people of, followers of (-ingas)",
        "ingham": "homestead of X's people",
        "ington": "farmstead of X's people",
        "east": "east (ēast)",
        "west": "west",
        "north": "north (norþ)",
        "south": "south (sūþ)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old English toponym into morphological components."""
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

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            if matched_prefix and stem.lower().startswith(matched_prefix):
                results.append(
                    SegmentationResult(
                        component=stem[: len(matched_prefix)],
                        position=0,
                        morph_type="compound_modifier",
                        lemma=matched_prefix,
                        confidence=0.8,
                    )
                )
                mid = stem[len(matched_prefix) :]
                if mid:
                    results.append(
                        SegmentationResult(
                            component=mid,
                            position=1,
                            morph_type="stem",
                            lemma=mid.lower(),
                            confidence=0.5,
                        )
                    )
            else:
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
                    confidence=0.7,
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
        """Classify whether a toponym is likely Old English."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        oe_suffixes = [
            "ingham",
            "ington",
            "ton",
            "ham",
            "ley",
            "leigh",
            "stead",
            "ford",
            "bury",
            "borough",
            "worth",
            "wick",
            "field",
            "hurst",
            "combe",
            "stow",
            "minster",
            "church",
            "bridge",
        ]
        for marker in oe_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"OE suffix -{marker}")
                score += 0.4
                break

        # -ing- medial (people of) pattern
        if "ing" in form_lower[1:-3]:
            evidence.append("OE -ing- patronymic medial")
            score += 0.15

        # OE vs ON distinguishers
        if form_lower.startswith("ch") or "church" in form_lower:
            evidence.append("OE /tʃ/ (vs ON /k/)")
            score += 0.1

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="450–1100 CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented OE components."""
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
                        cognates=[],
                    )
                )
        return candidates
