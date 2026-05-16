"""Morfessor-based morpheme segmentation for place names.

Provides an unsupervised/semi-supervised neural segmentation approach
using the Morfessor library (Virpioja et al., 2013). This augments
the rule-based language modules with data-driven segmentation.

The workflow:
1. Train a Morfessor model on the toponymic corpus (all name forms)
2. Optionally provide gold-standard annotations for semi-supervised training
3. Segment new names using the trained model
4. Integrate with the existing SegmentationPipeline

References:
- Virpioja et al. 2013. "Morfessor 2.0: Python Implementation and
  Extensions for Morfessor Baseline." Aalto University.
- Creutz & Lagus 2007. "Unsupervised models for morpheme segmentation
  and morphology learning." ACM TSLP.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import morfessor
except ImportError:
    morfessor = None  # type: ignore[assignment]

from toponymia.languages.base import SegmentationResult

logger = logging.getLogger(__name__)


@dataclass
class MorfessorConfig:
    """Configuration for Morfessor training."""

    corpus_threshold: int = 1
    dampening: str = "log"
    algorithm: str = "recursive"
    max_epochs: int = 10
    split_prob: float = 0.5


@dataclass
class MorfessorSegmenter:
    """Morfessor-based morpheme segmenter for toponyms.

    Trains an unsupervised model on place-name corpora and provides
    segmentation compatible with the rule-based pipeline.
    """

    model: Any = field(default=None, repr=False)
    config: MorfessorConfig = field(default_factory=MorfessorConfig)
    trained: bool = False
    corpus_size: int = 0

    def _check_available(self) -> None:
        if morfessor is None:
            msg = (
                "Morfessor is required for neural segmentation. "
                "Install with: pip install toponymia-europaea[nlp-segment]"
            )
            raise ImportError(msg)

    def train(
        self,
        corpus: list[str],
        *,
        annotations: dict[str, list[str]] | None = None,
    ) -> None:
        """Train the Morfessor model on a corpus of name forms.

        Args:
            corpus: List of place-name forms to train on.
            annotations: Optional gold-standard segmentations
                         (name → list of morphemes) for semi-supervised training.
        """
        self._check_available()

        model = morfessor.BaselineModel()

        # Build training data (word, count)
        train_data = [(1, name.lower()) for name in corpus if name.strip()]
        model.load_data(train_data, count_modifier=lambda x: x)

        # Add annotations if provided (semi-supervised)
        if annotations:
            for word, morphemes in annotations.items():
                model.set_compound_annotation(word.lower(), morphemes)
            logger.info(f"Added {len(annotations)} gold-standard annotations")

        # Train
        model.train_batch(
            algorithm=self.config.algorithm,
            max_epochs=self.config.max_epochs,
        )

        self.model = model
        self.trained = True
        self.corpus_size = len(train_data)
        logger.info(f"Morfessor model trained on {self.corpus_size} name forms")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a name form using the trained model.

        Args:
            form: Place-name form to segment.

        Returns:
            List of SegmentationResult objects.
        """
        self._check_available()

        if not self.trained or self.model is None:
            msg = "Model not trained. Call train() first."
            raise RuntimeError(msg)

        morphemes = self.model.viterbi_segment(form.lower())[0]

        if len(morphemes) < 2:
            return [
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.5,
                )
            ]

        results = []
        for i, morpheme in enumerate(morphemes):
            if i == len(morphemes) - 1:
                morph_type = "compound_head"
            elif i == 0:
                morph_type = "compound_modifier"
            else:
                morph_type = "infix"

            results.append(
                SegmentationResult(
                    component=morpheme,
                    position=i,
                    morph_type=morph_type,
                    confidence=0.6,
                )
            )

        return results

    def segment_batch(self, forms: list[str]) -> dict[str, list[SegmentationResult]]:
        """Segment multiple forms.

        Args:
            forms: List of name forms.

        Returns:
            Dict mapping form → segmentation results.
        """
        return {form: self.segment(form) for form in forms}

    def save_model(self, path: Path) -> None:
        """Save trained model to disk."""
        self._check_available()
        if not self.trained or self.model is None:
            msg = "No trained model to save."
            raise RuntimeError(msg)

        io = morfessor.MorfessorIO()
        io.write_binary_model_file(str(path), self.model)
        logger.info(f"Model saved: {path}")

    def load_model(self, path: Path) -> None:
        """Load a pre-trained model from disk."""
        self._check_available()
        io = morfessor.MorfessorIO()
        self.model = io.read_binary_model_file(str(path))
        self.trained = True
        logger.info(f"Model loaded: {path}")


def train_from_databank(
    databank_path: Path,
    *,
    country: str | None = None,
    annotations_path: Path | None = None,
) -> MorfessorSegmenter:
    """Train a Morfessor model from the databank corpus.

    Args:
        databank_path: Path to the databank root.
        country: Optional country filter (e.g. "NO").
        annotations_path: Optional JSONL file with gold segmentations.

    Returns:
        Trained MorfessorSegmenter instance.
    """
    places_dir = databank_path / "places"
    corpus: list[str] = []

    if not places_dir.is_dir():
        msg = f"Databank places directory not found: {places_dir}"
        raise FileNotFoundError(msg)

    for country_dir in sorted(places_dir.iterdir()):
        if not country_dir.is_dir():
            continue
        if country and country_dir.name != country:
            continue
        for jsonl_file in country_dir.glob("*.jsonl"):
            with jsonl_file.open() as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        name = record.get("name_form", "")
                        if name:
                            corpus.append(name)

    # Load annotations if provided
    annotations: dict[str, list[str]] | None = None
    if annotations_path and annotations_path.exists():
        annotations = {}
        with annotations_path.open() as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    name = entry.get("name", "")
                    morphemes = entry.get("morphemes", [])
                    if name and morphemes:
                        annotations[name] = morphemes

    logger.info(f"Training Morfessor on {len(corpus)} name forms")
    segmenter = MorfessorSegmenter()
    segmenter.train(corpus, annotations=annotations)
    return segmenter


def benchmark_against_rules(
    segmenter: MorfessorSegmenter,
    gold_standard: list[dict[str, Any]],
) -> dict[str, float]:
    """Benchmark Morfessor segmentation against gold-standard annotations.

    Args:
        segmenter: Trained MorfessorSegmenter.
        gold_standard: List of dicts with 'name' and 'morphemes' keys.

    Returns:
        Dict with precision, recall, F1 scores.
    """
    tp = 0
    fp = 0
    fn = 0

    for entry in gold_standard:
        name = entry["name"]
        expected = {m.lower() for m in entry["morphemes"]}
        predicted_results = segmenter.segment(name)
        predicted = {r.component.lower() for r in predicted_results}

        tp += len(expected & predicted)
        fp += len(predicted - expected)
        fn += len(expected - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }
