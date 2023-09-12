import numpy as np

from asl_utility import np_helpers


class TestAllClose:
    def test_trivial_equal(self):
        assert np_helpers.allclose(1.0, 1.0)

    def test_trivial_inequal(self):
        assert not np_helpers.allclose(1.0, 0.0)

    def test_significant_equal(self):
        assert np_helpers.allclose(1.0000003, 1.0)

    def test_significant_inequal(self):
        assert not np_helpers.allclose(1.0000005, 1.0)


class TestRound:
    def test_trivial(self):
        assert np_helpers.round_to_precision(1.0) == 1.0  # Actually do exact equality here to filter out float's rounding errors
        assert np_helpers.round_to_precision(1.5) == 1.5

    def test_significant_equal(self):
        assert np_helpers.round_to_precision(1.0000004) == 1.0
        assert np_helpers.round_to_precision(1.0) == 1.0

    def test_significant_inequal(self):
        assert np_helpers.round_to_precision(1.0000010) != 1.0
        assert np_helpers.round_to_precision(1.0000005) != 1.0
        assert np_helpers.round_to_precision(1.0000005) == 1.000001
