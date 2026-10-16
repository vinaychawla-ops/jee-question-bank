"""Tests for jee_pipeline.taxonomy (audit Cat 7)."""

from jee_pipeline.taxonomy import canonical_chapter, canonicalize


def test_case_duplicates_fold():
    assert canonicalize(["Biomolecules", "biomolecules"]) == ["Biomolecules and Polymers"]
    assert canonicalize(["Chemical Bonding", "chemical bonding"]) == ["Chemical Bonding"]
    assert canonicalize(["d-Block Elements", "d and f Block Elements"]) == ["d- and f-Block Elements"]


def test_overlapping_labels_merge():
    assert canonicalize(["AC Circuits", "Alternating Current", "LCR Circuits"]) == ["EMI and AC"]
    assert canonicalize(["Circle", "Circles"]) == ["Circles"]
    assert canonicalize(["Atomic Physics", "Atoms", "Nuclei"]) == ["Modern Physics"]


def test_order_preserved_and_deduped():
    assert canonicalize(["Circles", "Circle", "Probability"]) == ["Circles", "Probability"]
