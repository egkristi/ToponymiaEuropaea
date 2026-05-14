# Adding a Language Module

Language modules are the core extension mechanism for supporting new languages in Toponymia Europaea. Each module encapsulates the linguistic knowledge needed to segment, classify, and etymologize place names from a specific language or language period.

## Interface

Every language module must subclass `BaseLanguageModule` and implement three methods:

```python
from toponymia.languages.base import (
    BaseLanguageModule,
    SegmentationResult,
    LanguageClassification,
    EtymologyCandidate,
)

class MyLanguageModule(BaseLanguageModule):
    # Required class-level metadata
    language_code = "xxx"      # ISO 639-3 code
    language_name = "My Language"
    family = "Language Family"
    branch = "Family > Branch"
    period = "Start-End CE"
    script = "Latn"            # ISO 15924 script code
    
    # Known toponymic elements
    suffixes = ["-suffix1", "-suffix2"]
    prefixes = ["prefix1-", "prefix2-"]
    stems = ["stem1", "stem2"]
    
    def segment(self, form: str) -> list[SegmentationResult]:
        """Break a name form into morphological components."""
        ...
    
    def classify(self, form: str) -> LanguageClassification:
        """Assess probability that a form belongs to this language."""
        ...
    
    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        ...
```

## Step-by-Step Guide

### 1. Research the Language's Toponymic Inventory

Before writing code, document:
- Common toponymic suffixes and their meanings
- Common first elements (modifiers)
- Historical sound changes relevant to place names
- Known substrates and superstrates
- Key academic references

### 2. Create the Module File

Create `src/toponymia/languages/your_language.py`.

### 3. Implement Segmentation

The `segment()` method should:
- Try to match known suffixes (longest match first)
- Identify compound boundaries
- Return components with position and morph_type
- Assign confidence based on match quality

```python
def segment(self, form: str) -> list[SegmentationResult]:
    results = []
    form_lower = form.lower()
    
    # Try suffix matching
    for suffix in sorted(self.suffixes, key=len, reverse=True):
        clean_suffix = suffix.lstrip("-")
        if form_lower.endswith(clean_suffix):
            stem = form[:len(form) - len(clean_suffix)]
            results.append(SegmentationResult(
                component=stem, position=0,
                morph_type="compound_modifier", confidence=0.6
            ))
            results.append(SegmentationResult(
                component=form[len(stem):], position=1,
                morph_type="compound_head", lemma=clean_suffix, confidence=0.7
            ))
            return results
    
    # Fallback: whole form as stem
    return [SegmentationResult(component=form, position=0, morph_type="stem", confidence=0.3)]
```

### 4. Implement Classification

The `classify()` method should return a confidence score (0-1) with evidence:

```python
def classify(self, form: str) -> LanguageClassification:
    evidence = []
    score = 0.0
    
    # Check for known elements
    if any(form.lower().endswith(s.lstrip("-")) for s in self.suffixes):
        evidence.append("known suffix match")
        score += 0.4
    
    # Check for language-specific phonological features
    # ...
    
    return LanguageClassification(
        language_code=self.language_code,
        confidence=min(score, 1.0),
        evidence=evidence,
    )
```

### 5. Implement Etymology

Provide meaning candidates for known elements:

```python
def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
    candidates = []
    meanings = {
        "suffix1": ("lemma", "meaning", ["cognate1", "cognate2"]),
        # ...
    }
    for comp in components:
        key = (comp.lemma or comp.component).lower()
        if key in meanings:
            lemma, meaning, cognates = meanings[key]
            candidates.append(EtymologyCandidate(
                lemma=lemma, meaning=meaning,
                language_code=self.language_code,
                confidence=0.7, cognates=cognates,
            ))
    return candidates
```

### 6. Write Tests

Create `tests/test_languages/test_your_language.py`:

```python
from toponymia.languages.your_language import MyLanguageModule

def test_known_suffix_segmentation():
    module = MyLanguageModule()
    results = module.segment("Exampletown")
    assert len(results) == 2
    assert results[1].morph_type == "compound_head"

def test_classification_confidence():
    module = MyLanguageModule()
    result = module.classify("Exampletown")
    assert result.confidence > 0.5
    assert result.language_code == "xxx"
```

### 7. Register the Module

The module is auto-discovered if placed in `src/toponymia/languages/`. No manual registration needed beyond creating the file.

## Guidelines

- **Be conservative with confidence scores.** It's better to understate certainty than overstate it.
- **Document your sources.** Each known element should reference academic literature.
- **Handle ambiguity.** Many elements are shared across languages (e.g., -berg in Norse, German, Dutch). Your classifier should return appropriate confidence, not claim exclusivity.
- **Consider historical sound changes.** A module for Old English should recognize that modern -ham might reflect OE -hām but could also reflect -hamm (water meadow).
- **Test with real examples.** Use well-attested place names from the scholarly literature.
