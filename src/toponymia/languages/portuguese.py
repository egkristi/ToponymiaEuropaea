"""Portuguese language module for toponymic analysis.

Portuguese toponymy is directly relevant to Norwegian place-name studies
through the centuries-old KLIPPFISK/BACALHAU trade connection:

The Norway-Portugal trade axis (1500s–present):
- Bergen → Porto/Lisbon: dried/salted cod (tørrfisk, klippfisk)
- Portuguese merchants in Bergen from the 15th century
- Norwegian trading posts in Portugal
- "Bacalhau" (codfish) became Portugal's national dish from Norwegian exports
- Aveiro, Porto, Lisbon: major import ports for Norwegian fish
- Kristiansund → Ålesund → Bergen: klippfisk export centers

Toponymic relevance:
- Portuguese trade names appearing in Norwegian port contexts
- Norwegian place-names in Portuguese maritime records
- Trade-route toponymy (harbors, fishing grounds, drying racks)
- Loanwords in coastal Norwegian dialects from Portuguese contact

Portuguese linguistic layers:
- Pre-Roman (Celtic/Lusitanian) substrate
- Latin/Roman stratum
- Germanic (Suevic/Visigothic) superstrate (5th–8th c.)
- Arabic superstrate (711–1249, reconquest completed earlier than Spain)
- Norse/Viking raids (9th–11th c.): Lordemão < ON Loðinn+maðr
- Maritime expansion vocabulary (15th c. onwards)

Norse contact in Portugal:
- Viking raids on Lisbon (844 CE), Porto, Galician coast
- Lordemão (Coimbra district) < ON personal name compound
- Normandos/Nordoman- place-names
- Possible Norse settlement traces in Douro estuary

Key references:
- Machado 1984 "Dicionário Onomástico Etimológico da Língua Portuguesa"
- Piel & Kremer 1976 "Hispano-gotisches Namenbuch"
- Fernandes 1999 "Toponímia Portuguesa"
- Kurlansky 1997 "Cod: A Biography of the Fish that Changed the World"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PortugueseModule(BaseLanguageModule):
    """Language module for Portuguese toponyms."""

    language_code = "por"  # ISO 639-3
    language_name = "Portuguese"
    family = "Indo-European"
    branch = "Romance > Ibero-Romance > Galician-Portuguese"
    period = "9th century CE–present (from Galician-Portuguese)"
    script = "Latn"

    prefixes = [
        "Vila-",  # town, estate (Vila Nova, Vila Real)
        "Val-",  # valley (Valongo, Valença)
        "Monte-",  # mountain (Montemor, Montenegro)
        "Fonte-",  # spring (Fontes, Fontelo)
        "Ponte-",  # bridge (Ponte de Lima, Pontével)
        "Torre-",  # tower (Torres Vedras, Torredeita)
        "Cas-",  # house (< Lat. casa; Cascais?)
        "Guarda-",  # guard post (Guarda, Guardão)
        "Porto-",  # port, harbor (Porto, Portimão)
        "Foz-",  # river mouth (< Lat. fauces; Foz do Douro)
        "Ria-",  # estuary (Ria de Aveiro)
        "Pena-",  # rock (< Celtic *penna; Penafiel, Peniche)
        "Alm-",  # Arabic article (Almada, Almeida)
        "Al-",  # Arabic article (Algarve < al-Gharb 'the west')
    ]

    suffixes = [
        "-ão",  # augmentative (Leirão, Portimão)
        "-inho",  # diminutive (Mozinho, Calvinho)
        "-eira",  # place of activity (Oliveira, Pedreira)
        "-osa",  # abundance (Formosa, Pedrosa)
        "-ais",  # plural/place (Cascais, Odemirais)
        "-ães",  # patronymic plural (Guimarães < Vimaranes)
        "-ões",  # patronymic plural (Famalicões)
        "-elo",  # diminutive (Fontelo, Gondelo)
        "-ém",  # locative (Belém < Bethlehem, Santarém)
        "-inha",  # diminutive feminine (Ladinha)
        "-ade",  # place quality (Saudade, Felgueiras)
        "-al",  # grove/place of (Pinhal, Olival, Funchal)
        "-edo",  # grove of (Arvoredo, Azinhedo)
        "-oso",  # abundance (Pedroso, Fragoso)
        "-ã",  # plain/flat (Lousã)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "vila": "town, estate (< Lat. villa)",
        "val": "valley (< Lat. vallis)",
        "monte": "mountain, hill (< Lat. mons)",
        "fonte": "spring, fountain (< Lat. fons)",
        "ponte": "bridge (< Lat. pons)",
        "torre": "tower (< Lat. turris)",
        "porto": "port, harbor (< Lat. portus)",
        "foz": "river mouth (< Lat. fauces)",
        "ria": "estuary, tidal inlet",
        "pena": "rock, cliff (< Celtic *penna)",
        "praia": "beach (< Lat. plaga)",
        "cabo": "cape (< Lat. caput; Cabo da Roca)",
        "ilha": "island (< Lat. insula)",
        "rio": "river (< Lat. rivus)",
        "serra": "mountain range (< Lat. serra 'saw')",
        "campo": "field (< Lat. campus)",
        "pedra": "stone (< Lat. petra)",
        "vinha": "vineyard (< Lat. vinea)",
        "olival": "olive grove",
        "pinhal": "pine forest",
        "funchal": "fennel place (< Lat. funuculum; Madeira capital)",
        "guarda": "guard, watch-post",
        "castelo": "castle (< Lat. castellum)",
        "cruz": "cross (Christian naming layer)",
    }

    # Norse-related names in Portugal
    NORSE_CONTACT_NAMES: dict[str, str] = {
        "lordemão": "< ON Loðinn + maðr (Norse personal name compound)",
        "normandos": "place-names referencing Norse raiders",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Portuguese toponym into components."""
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

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                self.ELEMENT_MEANINGS.get(suffix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=stem,
                            position=0,
                            morph_type="compound_modifier",
                            confidence=0.7,
                        ),
                        SegmentationResult(
                            component=suffix, position=1, morph_type="compound_head", confidence=0.7
                        ),
                    ]
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                self.ELEMENT_MEANINGS.get(prefix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.65
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.65
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Portuguese."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Portuguese-specific suffixes
        port_suffixes = ["ães", "ões", "ão", "inho", "eira", "elo"]
        for suf in port_suffixes:
            if form_lower.endswith(suf):
                evidence.append(f"Portuguese suffix '-{suf}'")
                score += 0.5
                break

        # Portuguese prefixes
        port_prefixes = ["vila", "foz", "porto"]
        for pref in port_prefixes:
            if form_lower.startswith(pref):
                evidence.append(f"Portuguese prefix '{pref}-'")
                score += 0.4
                break

        # Portuguese orthographic markers (ã, õ, ç, lh, nh)
        if "ã" in form_lower or "õ" in form_lower:
            evidence.append("Portuguese nasal vowels (ã/õ)")
            score += 0.3
        if "nh" in form_lower or "lh" in form_lower:
            evidence.append("Portuguese digraph (nh/lh)")
            score += 0.2

        # Norse contact names
        for name in self.NORSE_CONTACT_NAMES:
            if name in form_lower:
                evidence.append(f"Norse contact name in Portugal: {self.NORSE_CONTACT_NAMES[name]}")
                score += 0.6
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Portuguese etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form = components[0].component if components else ""
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        lemma=f"*{element}",
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                    )
                )

        return candidates
