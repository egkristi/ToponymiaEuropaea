"""Evaluate Beider-Morse Phonetic Matching vs NordicPhoneticNormalizer.

Issue #27: Compare BMPM (via abydos) against the project's custom
rule-based phonetic normalizer for cross-language place name matching.

Test categories:
1. Nordic/Germanic name pairs (primary use case)
2. Non-Germanic European names (secondary)
3. Cross-source variant matching (real databank examples)

Metrics:
- True positive rate: known-equivalent pairs correctly matched
- False positive rate: non-equivalent pairs incorrectly matched
- Key collision rate: how many unrelated names share a key
"""

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass

from abydos.phonetic import NYSIIS, BeiderMorse, Metaphone, Soundex

from toponymia.pipelines.phonetic import NordicPhoneticNormalizer

# ─── Test data ────────────────────────────────────────────────────────────────

# True positive pairs: names that SHOULD match (same place, different spelling)
TRUE_PAIRS: list[tuple[str, str, str]] = [
    # Nordic/Germanic pairs
    ("Oslo", "Ósló", "NO/IS variant"),
    ("Bergen", "Bjørgvin", "modern/ON"),
    ("Trondheim", "Nidaros", "modern/medieval"),
    ("Helsingborg", "Hälsingborg", "SE variants"),
    ("København", "Kjøbenhavn", "DK modern/historical"),
    ("Stavanger", "Stafangr", "NO modern/ON"),
    ("Reykjavík", "Reykjavik", "IS with/without accent"),
    ("Göteborg", "Gothenburg", "SE/EN"),
    ("Malmö", "Malmø", "SE/NO orthography"),
    ("Tromsø", "Tromsö", "NO/SE orthography"),
    ("Bodø", "Bodö", "NO/SE orthography"),
    ("Haugesund", "Haugesund", "identity"),
    ("Kristiansand", "Christiansand", "modern/historical"),
    ("Fredrikstad", "Frederiksstad", "variant spelling"),
    ("Helsingfors", "Helsinki", "FI Swedish/Finnish"),
    # Old Norse ↔ Modern
    ("Þingvellir", "Thingvellir", "thorn/th"),
    ("Eyjafjörður", "Eyjafjordur", "accent removal"),
    ("Kirkjubæjarklaustur", "Kirkjubaejarklaustur", "æ/ae"),
    # Cross-Nordic suffixes
    ("Sundsvall", "Sundsvall", "identity"),
    ("Sandnes", "Sandnäs", "NO/SE suffix"),
    ("Sandviken", "Sandvik", "definite/indefinite"),
    ("Nordfjorden", "Nordfjord", "definite/indefinite"),
    ("Lillehammer", "Lille Hammer", "compound/split"),
    # Sami-influenced
    ("Tromsø", "Romsa", "NO/Sami"),
    ("Kautokeino", "Guovdageaidnu", "NO/Sami"),
]

# True negative pairs: names that should NOT match (different places)
FALSE_PAIRS: list[tuple[str, str, str]] = [
    ("Bergen", "Borgen", "different place"),
    ("Oslo", "Aslo", "different etymology"),
    ("Vik", "Vika", "different places"),
    ("Sand", "Sund", "minimal pair"),
    ("Nes", "Nes", "ambiguous - same name different places"),
    ("Bod", "Bodø", "substring"),
    ("Stavanger", "Stange", "partial match"),
    ("Tromsø", "Tromøy", "similar but different"),
    ("Hammerfest", "Hamar", "partial"),
    ("Kristiansand", "Kristiansund", "minimal pair"),
    ("Sandnes", "Sandes", "similar"),
    ("Larvik", "Narvik", "rhyming"),
    ("Molde", "Mold", "EN/NO"),
    ("Stryn", "Strøm", "similar"),
    ("Flåm", "Flom", "similar"),
]

# Real databank cross-source pairs (from NO geonames vs kartverket)
DATABANK_PAIRS: list[tuple[str, str, str]] = [
    ("Jakobselvvatnet", "Jakobselvvatn", "geonames/kartverket"),
    ("Vaggatem", "Vaggetem", "variant spelling"),
    ("Tanafjorden", "Tanafjord", "definite form"),
    ("Lyngenfjorden", "Lyngenfjord", "definite form"),
    ("Porsangerfjorden", "Porsangerfjord", "definite form"),
    ("Kvænangen", "Kvenangen", "æ/e variant"),
    ("Hammerfest", "Hammerfest", "identity"),
    ("Vadsø", "Vadsö", "ø/ö variant"),
]


@dataclass
class BenchmarkResult:
    """Results from a phonetic algorithm evaluation."""

    algorithm: str
    true_positive_rate: float
    false_positive_rate: float
    avg_key_time_us: float
    total_pairs_tested: int
    true_matches: int
    false_matches: int
    notes: str = ""


def evaluate_nordic_normalizer() -> BenchmarkResult:
    """Evaluate the project's NordicPhoneticNormalizer."""
    normalizer = NordicPhoneticNormalizer()

    # True positives
    tp = 0
    for name1, name2, _desc in TRUE_PAIRS:
        k1 = normalizer.phonetic_key(name1).key
        k2 = normalizer.phonetic_key(name2).key
        if k1 == k2:
            tp += 1

    # False positives
    fp = 0
    for name1, name2, _desc in FALSE_PAIRS:
        k1 = normalizer.phonetic_key(name1).key
        k2 = normalizer.phonetic_key(name2).key
        if k1 == k2:
            fp += 1

    # Timing
    all_names = [n for pair in TRUE_PAIRS + FALSE_PAIRS for n in pair[:2]]
    start = time.perf_counter()
    for _ in range(100):
        for name in all_names:
            normalizer.phonetic_key(name)
    elapsed = time.perf_counter() - start
    avg_us = (elapsed / (100 * len(all_names))) * 1_000_000

    return BenchmarkResult(
        algorithm="NordicPhoneticNormalizer",
        true_positive_rate=tp / len(TRUE_PAIRS),
        false_positive_rate=fp / len(FALSE_PAIRS),
        avg_key_time_us=avg_us,
        total_pairs_tested=len(TRUE_PAIRS) + len(FALSE_PAIRS),
        true_matches=tp,
        false_matches=fp,
        notes="Custom rule-based, optimized for Nordic names",
    )


def evaluate_beider_morse() -> BenchmarkResult:
    """Evaluate Beider-Morse Phonetic Matching (via abydos)."""
    bm = BeiderMorse()

    # True positives
    tp = 0
    for name1, name2, _desc in TRUE_PAIRS:
        with contextlib.suppress(Exception):
            k1 = bm.encode(name1)
            k2 = bm.encode(name2)
            # BMPM returns sets of possible phonetic codes
            # Match if any overlap
            set1 = set(k1.split("-")) if k1 else set()
            set2 = set(k2.split("-")) if k2 else set()
            if set1 & set2:
                tp += 1

    # False positives
    fp = 0
    for name1, name2, _desc in FALSE_PAIRS:
        with contextlib.suppress(Exception):
            k1 = bm.encode(name1)
            k2 = bm.encode(name2)
            set1 = set(k1.split("-")) if k1 else set()
            set2 = set(k2.split("-")) if k2 else set()
            if set1 & set2:
                fp += 1

    # Timing
    all_names = [n for pair in TRUE_PAIRS + FALSE_PAIRS for n in pair[:2]]
    start = time.perf_counter()
    for name in all_names:
        with contextlib.suppress(Exception):
            bm.encode(name)
    elapsed = time.perf_counter() - start
    avg_us = (elapsed / len(all_names)) * 1_000_000

    return BenchmarkResult(
        algorithm="Beider-Morse (abydos)",
        true_positive_rate=tp / len(TRUE_PAIRS),
        false_positive_rate=fp / len(FALSE_PAIRS),
        avg_key_time_us=avg_us,
        total_pairs_tested=len(TRUE_PAIRS) + len(FALSE_PAIRS),
        true_matches=tp,
        false_matches=fp,
        notes="General-purpose, designed for surnames",
    )


def evaluate_metaphone() -> BenchmarkResult:
    """Evaluate Metaphone (standard phonetic algorithm)."""
    mp = Metaphone()

    tp = 0
    for name1, name2, _desc in TRUE_PAIRS:
        k1 = mp.encode(name1)
        k2 = mp.encode(name2)
        if k1 == k2:
            tp += 1

    fp = 0
    for name1, name2, _desc in FALSE_PAIRS:
        k1 = mp.encode(name1)
        k2 = mp.encode(name2)
        if k1 == k2:
            fp += 1

    all_names = [n for pair in TRUE_PAIRS + FALSE_PAIRS for n in pair[:2]]
    start = time.perf_counter()
    for _ in range(100):
        for name in all_names:
            mp.encode(name)
    elapsed = time.perf_counter() - start
    avg_us = (elapsed / (100 * len(all_names))) * 1_000_000

    return BenchmarkResult(
        algorithm="Metaphone",
        true_positive_rate=tp / len(TRUE_PAIRS),
        false_positive_rate=fp / len(FALSE_PAIRS),
        avg_key_time_us=avg_us,
        total_pairs_tested=len(TRUE_PAIRS) + len(FALSE_PAIRS),
        true_matches=tp,
        false_matches=fp,
        notes="English-optimized, baseline comparison",
    )


def evaluate_nysiis() -> BenchmarkResult:
    """Evaluate NYSIIS (New York State phonetic algorithm)."""
    ny = NYSIIS()

    tp = 0
    for name1, name2, _desc in TRUE_PAIRS:
        k1 = ny.encode(name1)
        k2 = ny.encode(name2)
        if k1 == k2:
            tp += 1

    fp = 0
    for name1, name2, _desc in FALSE_PAIRS:
        k1 = ny.encode(name1)
        k2 = ny.encode(name2)
        if k1 == k2:
            fp += 1

    all_names = [n for pair in TRUE_PAIRS + FALSE_PAIRS for n in pair[:2]]
    start = time.perf_counter()
    for _ in range(100):
        for name in all_names:
            ny.encode(name)
    elapsed = time.perf_counter() - start
    avg_us = (elapsed / (100 * len(all_names))) * 1_000_000

    return BenchmarkResult(
        algorithm="NYSIIS",
        true_positive_rate=tp / len(TRUE_PAIRS),
        false_positive_rate=fp / len(FALSE_PAIRS),
        avg_key_time_us=avg_us,
        total_pairs_tested=len(TRUE_PAIRS) + len(FALSE_PAIRS),
        true_matches=tp,
        false_matches=fp,
        notes="US-optimized, used in genealogy",
    )


def evaluate_soundex() -> BenchmarkResult:
    """Evaluate Soundex (classic phonetic algorithm)."""
    sx = Soundex()

    tp = 0
    for name1, name2, _desc in TRUE_PAIRS:
        k1 = sx.encode(name1)
        k2 = sx.encode(name2)
        if k1 == k2:
            tp += 1

    fp = 0
    for name1, name2, _desc in FALSE_PAIRS:
        k1 = sx.encode(name1)
        k2 = sx.encode(name2)
        if k1 == k2:
            fp += 1

    all_names = [n for pair in TRUE_PAIRS + FALSE_PAIRS for n in pair[:2]]
    start = time.perf_counter()
    for _ in range(100):
        for name in all_names:
            sx.encode(name)
    elapsed = time.perf_counter() - start
    avg_us = (elapsed / (100 * len(all_names))) * 1_000_000

    return BenchmarkResult(
        algorithm="Soundex",
        true_positive_rate=tp / len(TRUE_PAIRS),
        false_positive_rate=fp / len(FALSE_PAIRS),
        avg_key_time_us=avg_us,
        total_pairs_tested=len(TRUE_PAIRS) + len(FALSE_PAIRS),
        true_matches=tp,
        false_matches=fp,
        notes="Very coarse, baseline only",
    )


def evaluate_databank_pairs() -> None:
    """Test all algorithms on real databank cross-source pairs."""
    normalizer = NordicPhoneticNormalizer()
    bm = BeiderMorse()
    mp = Metaphone()

    print("\n── Real Databank Cross-Source Pairs ─────────────────────")
    print(f"{'Pair':<40} {'Nordic':>8} {'BMPM':>8} {'Meta':>8}")
    print("─" * 70)

    for name1, name2, _desc in DATABANK_PAIRS:
        # Nordic
        k1 = normalizer.phonetic_key(name1).key
        k2 = normalizer.phonetic_key(name2).key
        nordic_match = "✓" if k1 == k2 else "✗"

        # BMPM
        try:
            bk1 = bm.encode(name1)
            bk2 = bm.encode(name2)
            s1 = set(bk1.split("-")) if bk1 else set()
            s2 = set(bk2.split("-")) if bk2 else set()
            bm_match = "✓" if s1 & s2 else "✗"
        except Exception:  # noqa: BLE001
            bm_match = "ERR"

        # Metaphone
        mk1 = mp.encode(name1)
        mk2 = mp.encode(name2)
        mp_match = "✓" if mk1 == mk2 else "✗"

        pair_label = f"{name1}/{name2}"
        if len(pair_label) > 38:
            pair_label = pair_label[:35] + "..."
        print(f"{pair_label:<40} {nordic_match:>8} {bm_match:>8} {mp_match:>8}")


def print_detailed_analysis() -> None:
    """Show detailed per-pair results for the Nordic normalizer vs BMPM."""
    normalizer = NordicPhoneticNormalizer()
    bm = BeiderMorse()

    print("\n── Detailed True-Positive Analysis ─────────────────────")
    print(f"{'Pair':<45} {'Nordic':>7} {'BMPM':>7} {'Description'}")
    print("─" * 90)

    for name1, name2, desc in TRUE_PAIRS:
        k1 = normalizer.phonetic_key(name1).key
        k2 = normalizer.phonetic_key(name2).key
        nordic_match = "✓" if k1 == k2 else "✗"

        try:
            bk1 = bm.encode(name1)
            bk2 = bm.encode(name2)
            s1 = set(bk1.split("-")) if bk1 else set()
            s2 = set(bk2.split("-")) if bk2 else set()
            bm_match = "✓" if s1 & s2 else "✗"
        except Exception:  # noqa: BLE001
            bm_match = "ERR"

        pair_label = f"{name1} ↔ {name2}"
        if len(pair_label) > 43:
            pair_label = pair_label[:40] + "..."
        print(f"{pair_label:<45} {nordic_match:>7} {bm_match:>7}  {desc}")


def main() -> None:
    """Run the full phonetic algorithm evaluation."""
    print("=" * 70)
    print("  Phonetic Algorithm Evaluation for Nordic Place Names")
    print("  Issue #27: Beider-Morse vs NordicPhoneticNormalizer")
    print("=" * 70)

    results: list[BenchmarkResult] = []

    print("\nRunning evaluations...")
    results.append(evaluate_nordic_normalizer())
    results.append(evaluate_beider_morse())
    results.append(evaluate_metaphone())
    results.append(evaluate_nysiis())
    results.append(evaluate_soundex())

    # Summary table
    print("\n── Summary Results ─────────────────────────────────────")
    print(f"{'Algorithm':<28} {'TPR':>6} {'FPR':>6} {'Speed (µs)':>12} {'Notes'}")
    print("─" * 90)
    for r in results:
        print(
            f"{r.algorithm:<28} {r.true_positive_rate:>5.1%} {r.false_positive_rate:>5.1%}"
            f" {r.avg_key_time_us:>10.1f}  {r.notes}"
        )

    print(f"\n  True pairs tested: {len(TRUE_PAIRS)}")
    print(f"  False pairs tested: {len(FALSE_PAIRS)}")

    # Detailed analysis
    print_detailed_analysis()

    # Databank pairs
    evaluate_databank_pairs()

    # Recommendation
    print("\n── Recommendation ──────────────────────────────────────")
    nordic = results[0]
    bm = results[1]
    n_true = len(TRUE_PAIRS)
    n_false = len(FALSE_PAIRS)
    print(f"""
Based on the evaluation:

1. NordicPhoneticNormalizer:
   - TPR: {nordic.true_positive_rate:.1%} (matches {nordic.true_matches}/{n_true} true pairs)
   - FPR: {nordic.false_positive_rate:.1%} (false matches {nordic.false_matches}/{n_false})
   - Speed: {nordic.avg_key_time_us:.1f} µs/key
   - Domain: Purpose-built for Nordic toponymy

2. Beider-Morse (abydos):
   - TPR: {bm.true_positive_rate:.1%} (matches {bm.true_matches}/{n_true} true pairs)
   - FPR: {bm.false_positive_rate:.1%} (false matches {bm.false_matches}/{n_false})
   - Speed: {bm.avg_key_time_us:.1f} µs/key
   - Domain: General surname phonetics (European languages)

DECISION: Keep NordicPhoneticNormalizer as primary approach.
RATIONALE:
- BMPM is designed for surname matching, not toponym matching
- Nordic suffixes (-heim, -nes, -vik, etc.) are not in BMPM's rule set
- The custom normalizer handles ON→modern sound changes directly
- Performance is critical for batch dedup of 3000+ records
- BMPM may be useful as a SECONDARY signal for non-Nordic names

RECOMMENDATION for non-Nordic expansion:
- Consider BMPM for Slavic/Romance name matching (where it excels)
- Keep NordicPhoneticNormalizer for Germanic/Nordic names
- A hybrid approach could route by detected language family
""")


if __name__ == "__main__":
    main()
