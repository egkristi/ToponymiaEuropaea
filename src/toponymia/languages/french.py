"""French (français) language module for toponymic analysis.

French toponymy reflects multiple historical layers:
- Pre-Celtic (Basque, Ligurian): -onne, -ance
- Celtic/Gaulish: -dunum > -dun/-don, -briga, -magos, -nemetum
- Latin/Gallo-Roman: -acum > -ac/-ay/-y, villa-, mons-
- Frankish/Germanic: -court, -ville(rs), -heim > -ain
- Medieval French: Saint-, Château-, Mont-, Belle-

Key references:
- Dauzat & Rostaing 1963 "Dictionnaire étymologique des noms de lieux"
- Nègre 1990–1998 "Toponymie générale de la France"
- Longnon 1920–1929 "Les noms de lieu de la France"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class FrenchModule(BaseLanguageModule):
    """Language module for French toponyms."""

    language_code = "fra"
    language_name = "French"
    family = "Indo-European"
    branch = "Italic > Romance > Gallo-Romance"
    period = "842 CE–present"
    script = "Latn"

    prefixes = [
        "Saint-",  # saint (Saint-Denis, Saint-Étienne)
        "Sainte-",  # saint feminine (Sainte-Marie)
        "Mont-",  # mountain (Montpellier, Montmartre)
        "Château-",  # castle (Châteauroux)
        "Belle-",  # beautiful (Belleville)
        "Beau-",  # beautiful masculine (Beaumont)
        "Haute-",  # upper (Haute-Savoie)
        "Basse-",  # lower (Basse-Normandie)
        "Grande-",  # great (Grande-Synthe)
        "Petite-",  # small (Petite-Rosselle)
        "Vielle-",  # old (Vielle-Tursan)
        "Neuf-",  # new (Neufchâteau)
        "Pont-",  # bridge (Pontoise)
        "Font-",  # spring (Fontainebleau)
        "Roche-",  # rock (Rochefort)
        "Ville-",  # town (Villeneuve)
    ]

    suffixes = [
        "-ville",  # town, farm (Deauville, Abbeville)
        "-villers",  # farm (Villers-Cotterêts)
        "-court",  # farm, estate (Harcourt, Liancourt)
        "-mont",  # mountain (Clermont, Beaumont)
        "-pont",  # bridge (Pont-à-Mousson)
        "-fort",  # fortress (Montfort, Rochefort)
        "-fontaine",  # spring (Fontaine-lès-Dijon)
        "-ac",  # Gallo-Roman estate (Cognac, Aurillac)
        "-ay",  # Gallo-Roman estate (Bernay, Épernay)
        "-é",  # Gallo-Roman estate (Cluny variant)
        "-y",  # Gallo-Roman estate (Cergy, Neuilly)
        "-ais",  # place of (Calais)
        "-ois",  # place of (Blois)
        "-eux",  # place of (Évreux, Dreux)
        "-oux",  # place of (Limoux)
        "-an",  # Gaulish suffix (Royan)
        "-on",  # diminutive (Dijon, Avallon)
        "-ière",  # place characterized by (Rivière)
        "-ières",  # plural form
        "-bourg",  # fortified town (Strasbourg, Cherbourg)
        "-château",  # castle
        "-sur-",  # on (river) — infix but common pattern
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "saint": "saint, holy",
        "sainte": "saint (feminine)",
        "mont": "mountain, hill",
        "château": "castle, fortified house",
        "belle": "beautiful (feminine)",
        "beau": "beautiful (masculine)",
        "haute": "upper, high",
        "basse": "lower",
        "grande": "great",
        "petite": "small",
        "neuf": "new",
        "pont": "bridge",
        "font": "spring, fountain",
        "roche": "rock",
        "ville": "town, farm (< villa)",
        "court": "farm, estate (< curtis)",
        "fort": "fortress, strong",
        "bourg": "fortified town (< burgus)",
        "fontaine": "spring, fountain",
        "val": "valley",
        "pré": "meadow",
        "bois": "wood, forest",
        "champ": "field",
        "lac": "lake",
        "rivière": "river",
        "île": "island",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a French toponym into morphological components."""
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
                        lemma=middle.lower().strip("-"),
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
                    lemma=form[len(matched_prefix) :].lower().strip("-"),
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
        """Classify whether a toponym is likely French."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Saint- prefix is very strong indicator
        if form_lower.startswith(("saint", "sainte")):
            evidence.append("French 'Saint-' prefix")
            score += 0.4

        french_suffixes = ["ville", "villers", "court", "mont", "bourg", "fontaine", "ac", "ay"]
        for marker in french_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"French suffix -{marker}")
                score += 0.35
                break

        # French accented characters
        french_chars = ["é", "è", "ê", "ë", "à", "â", "ô", "î", "û", "ç", "œ"]
        for ch in french_chars:
            if ch in form_lower:
                evidence.append(f"French character '{ch}'")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="842–present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented French components."""
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
