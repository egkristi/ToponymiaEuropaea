"""Analysis pipeline stages."""

from toponymia.pipelines.normalize import NormalizationPipeline
from toponymia.pipelines.segment import SegmentationPipeline

__all__ = ["NormalizationPipeline", "SegmentationPipeline"]
