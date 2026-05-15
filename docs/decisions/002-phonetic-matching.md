# Decision: Phonetic Matching Algorithm for Toponymia Europaea

**Issue:** #27 — Evaluate Beider-Morse Phonetic Matching  
**Date:** 2025-01-20  
**Status:** DECIDED — Keep NordicPhoneticNormalizer, do not adopt BMPM  

---

## Context

The project needs phonetic matching to:
1. Deduplicate place names across sources (GeoNames, Kartverket, OSM)
2. Match historical/modern spelling variants
3. Handle cross-Nordic orthographic differences (NO/SE/DK/IS/FI)

Currently using: `NordicPhoneticNormalizer` (custom rule-based, in `src/toponymia/pipelines/phonetic.py`)

## Algorithms Evaluated

| Algorithm | TPR | FPR | Speed (µs/key) | Domain |
|-----------|-----|-----|-----------------|--------|
| **NordicPhoneticNormalizer** | **36.0%** | **6.7%** | **10.8** | Nordic toponymy |
| Beider-Morse (abydos) | 8.0% | 13.3% | 1505.7 | European surnames |
| Metaphone | 48.0% | 53.3% | 2.4 | English names |
| NYSIIS | 40.0% | 40.0% | 4.3 | US census |
| Soundex | 72.0% | 60.0% | 1.6 | Very coarse matching |

**Test corpus:** 25 true-positive pairs (same place, different spellings) + 15 true-negative pairs (different places, similar names).

## Key Findings

### 1. BMPM is unsuitable for Nordic toponyms
- Only matched 2/25 true pairs (both identity matches)
- Higher false positive rate than our normalizer (13.3% vs 6.7%)
- 140× slower per key (1506 µs vs 10.8 µs)
- No awareness of Nordic onomastic suffixes (-heim, -nes, -vik, -stad, etc.)
- Designed for surname phonetics, not toponym morphology

### 2. NordicPhoneticNormalizer excels at its design target
- Best precision (lowest FPR) of all algorithms tested
- Handles cross-Nordic orthography (ö/ø, ä/æ, aa/å)
- Handles Old Norse → Modern reflexes (þ→t, ð→d, ǫ→o)
- Handles suffix definite forms (fjorden→fjord, viken→vik)
- Fast enough for batch processing (10.8 µs × 3000 records = 32 ms)

### 3. All algorithms struggle with deeply different names
- No algorithm matches Bergen ↔ Bjørgvin (requires etymological knowledge)
- No algorithm matches Kautokeino ↔ Guovdageaidnu (cross-language borrowing)
- These require the **language module classify/etymologize** path, not phonetics

### 4. Generic algorithms have unacceptable FPR for onomastic work
- Soundex: 60% FPR — would create many false duplicate links
- Metaphone/NYSIIS: 40-53% FPR — too many collisions
- Only our normalizer keeps FPR under 10%

## Decision

**Keep NordicPhoneticNormalizer as the sole phonetic matching approach.**

### Rationale
1. Domain-specific rules dramatically outperform general-purpose algorithms
2. BMPM adds complexity and a heavy dependency for no benefit on our data
3. The 36% TPR is appropriate — cases it misses require etymological analysis, not better phonetics
4. Low FPR (6.7%) is critical for data integrity in a research platform

### Improvements to NordicPhoneticNormalizer (future work)
Based on the evaluation, these enhancements could increase TPR without hurting FPR:

1. **Accent stripping**: `á→a, í→i, ó→o, ú→u, ö→o` (would catch Ósló, Reykjavík)
2. **K/Ch/C equivalence**: `ch→k, c→k` (would catch Christiansand → Kristiansand)  
3. **Definite article stripping**: `-et$, -en$, -a$` (would catch Jakobselvvatnet)
4. **æ/ae equivalence**: Already partially covered but needs expansion

### For non-Nordic expansion
When the project expands to Slavic/Romance/Celtic names:
- Consider language-family-specific normalizers (same pattern as NordicPhoneticNormalizer)
- BMPM could be evaluated again for Slavic names specifically
- A routing layer could dispatch to the appropriate normalizer by detected language

## Benchmark Reproduction

```bash
uv run python benchmarks/phonetic_evaluation.py
```

## References

- Beider, A. & Morse, S.P. (2008). "An Alternative Phonetic Matching Algorithm"
- abydos library: https://github.com/chrislit/abydos
- Current implementation: `src/toponymia/pipelines/phonetic.py`
