"""Low German language module for toponymic analysis.

Low German (Plattdüütsch/Niederdeutsch, nds) is a West Germanic language
spoken in northern Germany and the northeastern Netherlands. Unlike High
German, it did not undergo the High German consonant shift. Its toponymy
features: -büttel (settlement), -borstel (farmstead), -stedt (place),
-hagen (enclosed settlement). This covers the modern spoken variety;
Middle Low German is handled separately as a historical module.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LowGermanModule(BaseLanguageModule):
    """Language module for Low German toponyms."""

    language_code = "nds"
    language_name = "Low German"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Low German"
    period = "Modern (1500 CE–present)"
    script = "Latn"

    prefixes = [
        "Olden-",
        "Nien-",
        "Lütt-",
        "Groot-",
        "Oost-",
        "West-",
    ]

    suffixes = [
        "-büttel",
        "-borstel",
        "-bostel",
        "-stedt",
        "-stede",
        "-hagen",
        "-husen",
        "-feld",
        "-brook",
        "-dorp",
        "-borg",
        "-wisch",
        "-kamp",
        "-horst",
        "-loh",
    ]

    stems = [
        "water",
        "steen",
        "holt",
        "brook",
        "wisch",
        "kamp",
        "diek",
        "sand",
        "moor",
        "borg",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "olden": "old",
            "nien": "new",
            "lütt": "small",
            "groot": "large",
            "oost": "east",
            "west": "west",
            "büttel": "settlement, dwelling",
            "borstel": "farmstead",
            "bostel": "farmstead",
            "stedt": "place, site",
            "stede": "place, site",
            "hagen": "enclosed settlement",
            "husen": "houses",
            "feld": "field",
            "brook": "marsh, wetland",
            "dorp": "village",
            "borg": "castle, fortification",
            "wisch": "meadow",
            "kamp": "enclosed field",
            "horst": "wooded rise",
            "loh": "clearing, grove",
            "water": "water",
            "steen": "stone",
            "holt": "wood",
            "diek": "dike",
            "moor": "moor, bog",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Low German toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.7,
                    )
                )
                form = form[len(prefix) :]
                form_lower = form.lower()
                break

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                pos = len(results)
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
                        component=form[len(form) - len(suffix) :],
                        position=pos + 1,
                        morph_type="suffix",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.7,
                    )
                )
                return results

        pos = len(results)
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
        """Classify whether a name form belongs to Low German."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Low German suffix -{suffix}")
                score += 0.35
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Low German prefix {prefix}-")
                score += 0.25
                break

        nds_markers = ["ü", "ö", "ee"]
        for marker in nds_markers:
            if marker in form_lower:
                evidence.append(f"Low German grapheme '{marker}'")
                score += 0.15
                break

        nds_elements = ["büttel", "borstel", "hagen", "brook", "wisch"]
        for elem in nds_elements:
            if elem in form_lower:
                evidence.append(f"Characteristic Low German element '{elem}'")
                score += 0.25
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "büttel": ("*bōþla-", "dwelling", ["OE botl", "ON ból"]),
            "borstel": ("*burg-stalli", "farmstead", ["OE burh-steall"]),
            "stedt": ("*stadiz", "place, site", ["OE stede", "HG Stätte"]),
            "hagen": ("*hagō", "enclosure", ["OE haga", "En. haw"]),
            "husen": ("*hūsą", "houses", ["OE hūs", "En. house"]),
            "brook": ("*brōkaz", "marsh", ["OE brōc", "En. brook"]),
            "dorp": ("*þurpa-", "village", ["De. Dorf", "En. thorp"]),
            "horst": ("*hurstiz", "wooded rise", ["OE hyrst", "En. hurst"]),
            "loh": ("*lauhaz", "clearing", ["OE lēah", "En. -ley"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=cognates,
                        sources=["Udolph, Namenkundliche Studien zum Germanenproblem"],
                    )
                )
        return candidates
