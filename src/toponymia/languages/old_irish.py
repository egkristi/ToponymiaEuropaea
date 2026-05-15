"""Old Irish (Goídelc) language module for toponymic analysis.

Old Irish toponymy is essential for Norse-Irish contact studies:
- Vikings founded Dublin (Dubh Linn = black pool), Waterford (Veðrafjǫrðr),
  Wexford (Veisafjǫrðr), Cork, Limerick
- Hybrid Norse-Irish names common (e.g., Leixlip < ON lax+hlaup = salmon+leap)
- Irish elements: baile (town), cill/kill (church), drum (ridge), loch (lake)
- Prefix system: Baile-/Bally-, Kil-/Cill-, Dún-, Rath-, Liss-
- Anglicization obscures Irish origins (Knockmore < Cnoc Mór)

Key references:
- Hogan 1910 "Onomasticon Goedelicum"
- Joyce 1869/1875/1913 "Irish Names of Places" (3 vols)
- Flanagan & Flanagan 1994 "Irish Place Names"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldIrishModule(BaseLanguageModule):
    """Language module for Old Irish (Goídelc) toponyms."""

    language_code = "sga"  # ISO 639-3 for Old Irish
    language_name = "Old Irish"
    family = "Indo-European"
    branch = "Celtic > Insular Celtic > Goidelic"
    period = "600–900 CE"
    script = "Latn"

    prefixes = [
        "Baile-",  # town, homestead (> Bally-)
        "Bally-",  # anglicized baile
        "Cill-",  # church (> Kil-)
        "Kil-",  # anglicized cill
        "Kill-",  # variant
        "Dún-",  # fort (Dundalk, Dunmore)
        "Dun-",  # anglicized
        "Ráth-",  # ring fort (Rathmore)
        "Rath-",  # anglicized
        "Liss-",  # ring fort (Lismore)
        "Lis-",  # variant
        "Drum-",  # ridge (Drumcondra)
        "Knock-",  # hill (< cnoc; Knockmore)
        "Glen-",  # valley (< gleann; Glendalough)
        "Car-",  # rock/cairn (< carraig; Carrick)
        "Carrick-",  # rock
        "Innis-",  # island (< inis; Innisfree)
        "Inis-",  # variant
        "Ard-",  # height (Armagh < Ard Macha)
        "Slieve-",  # mountain (< sliabh; Slieve Mish)
    ]

    suffixes = [
        "-more",  # great (< mór; Dunmore)
        "-beg",  # small (< beag; Ballybeg)
        "-lough",  # lake (< loch; Ballynahinch)
        "-owen",  # river (< abhainn)
        "-avon",  # river (< abhainn)
        "-drum",  # ridge (< druim)
        "-derry",  # oak wood (< doire)
        "-dore",  # variant of derry
        "-agh",  # field (< achadh)
        "-anna",  # marsh (< eanach)
        "-lin",  # pool (< linn; Dublin)
        "-linn",  # pool
        "-roe",  # red (< rua)
        "-duff",  # black (< dubh)
        "-bawn",  # white (< bán)
        "-glass",  # green/stream (< glas)
        "-ross",  # wood/headland (< ros)
        "-ard",  # height
        "-cloon",  # meadow (< cluain)
        "-curry",  # marsh (< currach)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "baile": "town, homestead",
        "bally": "town (anglicized)",
        "cill": "church, monastery cell",
        "kil": "church (anglicized)",
        "dún": "fort, fortified place",
        "dun": "fort (anglicized)",
        "ráth": "ring fort, earthen fort",
        "rath": "ring fort (anglicized)",
        "liss": "ring fort (< lios)",
        "drum": "ridge, back (druim)",
        "knock": "hill (cnoc)",
        "glen": "valley (gleann)",
        "car": "rock, cairn (carraig)",
        "carrick": "rock",
        "innis": "island (inis)",
        "ard": "height, promontory",
        "slieve": "mountain (sliabh)",
        "more": "great, large (mór)",
        "beg": "small (beag)",
        "lough": "lake (loch)",
        "derry": "oak wood (doire)",
        "linn": "pool, waterfall",
        "roe": "red (rua)",
        "duff": "black (dubh)",
        "bawn": "white (bán)",
        "glass": "green, stream (glas)",
        "ross": "wood, headland (ros)",
        "cloon": "meadow (cluain)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Irish toponym into morphological components."""
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
        """Classify whether a toponym is likely Old Irish."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        irish_prefixes = [
            "bally",
            "kil",
            "kill",
            "dun",
            "rath",
            "drum",
            "knock",
            "glen",
            "carrick",
            "inis",
            "ard",
            "slieve",
        ]
        for marker in irish_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Irish prefix {marker}-")
                score += 0.4
                break

        irish_suffixes = ["more", "beg", "lough", "derry", "linn", "ross"]
        for marker in irish_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Irish suffix -{marker}")
                score += 0.3
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="600–1200 CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old Irish components."""
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
