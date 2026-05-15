"""Scots Gaelic language module for toponymic analysis.

Scots Gaelic (Gàidhlig) is essential for Norse-Celtic contact studies:
- The Hebrides, western Highlands, and islands were bilingual zones
- "Gall-Gàidheil" (foreign Gaels) = Norse-Gaelic hybrid population
- Many place-names show Norse + Gaelic fusion (e.g., ON dalr + G. fhìn)
- Gaelic displaced Pictish, then coexisted with Norse for centuries
- Distinguishing Scots Gaelic from Irish is critical for localization

Norse-Gaelic hybrid patterns:
- ON personal name + Gaelic generic: Tórr Somerled (Torridon?)
- ON generic + Gaelic qualifier: Loch Snizort (< ON Sneis-fjörðr?)
- Gaelic adaptation of ON: Diùra (Jura < ON Dýr-ey)

Key references:
- Watson 1926 "The History of the Celtic Place-Names of Scotland"
- Cox 2002 "The Place-Names of Carloway, Lewis"
- Gammeltoft 2001 "The Place-Name Element bólstaðr in the Danelaw"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ScotsGaelicModule(BaseLanguageModule):
    """Language module for Scots Gaelic toponyms."""

    language_code = "gla"  # ISO 639-3 for Scottish Gaelic
    language_name = "Scots Gaelic"
    family = "Indo-European"
    branch = "Celtic > Goidelic"
    period = "10th century CE – present"
    script = "Latn"

    prefixes = [
        "Ach-",  # field (< achadh; Achmore, Achnasheen)
        "Ard-",  # height (< àrd; Ardnamurchan, Ardrossan)
        "Bal-",  # farm/township (< baile; Balmoral, Balloch)
        "Ben-",  # mountain (< beinn; Ben Nevis, Ben More)
        "Carn-",  # cairn (< càrn; Cairngorm)
        "Craig-",  # rock (< creag; Craigellachie)
        "Drum-",  # ridge (< druim; Drumnadrochit)
        "Dun-",  # fort (< dùn; Dundee, Dunvegan)
        "Glen-",  # valley (< gleann; Glencoe, Glenfinnan)
        "Inver-",  # river mouth (< inbhir; Inverness, Inverary)
        "Kil-",  # church (< cill; Kilmarnock, Kildonan)
        "Kin-",  # head (< ceann; Kinlochleven, Kintyre)
        "Loch-",  # lake/inlet (< loch; Lochaber, Lochinver)
        "Strath-",  # wide valley (< srath; Strathmore, Strathclyde)
        "Tober-",  # well (< tobar; Tobermory)
    ]

    suffixes = [
        "-more",  # great (< mòr; Aviemore, Strath More)
        "-beg",  # small (< beag; Carbeg, Portbeg)
        "-ban",  # white (< bàn; Ruthven Ban)
        "-dubh",  # black (< dubh; Inver Dubh)
        "-gorm",  # blue/green (< gorm; Cairngorm)
        "-dearg",  # red (< dearg; Sgurr Dearg)
        "-dale",  # can be Norse dalr OR Gaelic adaptation
        "-ish",  # island (< innis; Langamish)
        "-pool",  # pool/bay (< poll; Ullapool)
        "-aig",  # bay (< Norse vík via Gaelic; Portnalong → -aig)
        "-ey",  # island (Norse loan in Gaelic context)
        "-bost",  # farm (< ON bólstaðr via Gaelic; Lewis names)
        "-shader",  # shieling (< ON setr via Gaelic; Lewis)
        "-nis",  # headland (< ON nes via Gaelic; Cellarnis)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ach": "field (< achadh)",
        "ard": "high point, height (< àrd)",
        "bal": "farm, township (< baile)",
        "ben": "mountain peak (< beinn)",
        "carn": "cairn, rocky hill (< càrn)",
        "craig": "rock, crag (< creag)",
        "drum": "ridge (< druim)",
        "dun": "fort, fortified hill (< dùn)",
        "glen": "narrow valley (< gleann)",
        "inver": "river mouth, confluence (< inbhir)",
        "kil": "church, cell (< cill < Lat. cella)",
        "kin": "head, headland (< ceann)",
        "loch": "lake or sea inlet (< loch)",
        "strath": "broad valley (< srath)",
        "tober": "well, spring (< tobar)",
        "more": "great, large (< mòr)",
        "beg": "small, little (< beag)",
        "ban": "white, fair (< bàn)",
        "dubh": "black, dark (< dubh)",
        "gorm": "blue, green (< gorm)",
        "dearg": "red (< dearg)",
        "pool": "pool, muddy place (< poll)",
        "bost": "farm (< ON bólstaðr, Gaelicized)",
        "shader": "shieling (< ON setr, Gaelicized)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Scots Gaelic toponym into components."""
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
                    confidence=0.85,
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
                    confidence=0.8,
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
        """Classify whether a toponym is likely Scots Gaelic."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        gaelic_prefixes = [
            "bal",
            "ben",
            "glen",
            "inver",
            "kil",
            "kin",
            "strath",
            "ard",
            "drum",
            "dun",
            "loch",
        ]
        for marker in gaelic_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Scots Gaelic prefix {marker}-")
                score += 0.4
                break

        # Norse-Gaelic hybrid markers (diagnostic of Hebridean zone)
        hybrid_markers = ["bost", "shader", "aig"]
        for marker in hybrid_markers:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Norse-Gaelic hybrid suffix -{marker}")
                score += 0.35
                break

        # Gaelic color/size qualifiers
        gaelic_quals = ["more", "beg", "ban", "dubh", "gorm", "dearg"]
        for marker in gaelic_quals:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 2:
                evidence.append(f"Gaelic qualifier -{marker}")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="10th century – present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Scots Gaelic components."""
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
