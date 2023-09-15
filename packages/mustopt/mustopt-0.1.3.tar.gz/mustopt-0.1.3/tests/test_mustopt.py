import unittest

from hamcrest import assert_that, equal_to

from mustopt import MustOpt


class TestMustOpt(unittest.TestCase):
    def test_empty_new_is_invalid(self):
        assert_that(MustOpt.new().valid(), equal_to(False))

    def test_new_from_value_is_valid(self):
        assert_that(MustOpt.new(1).valid(), equal_to(True))

    def test_unset_makes_container_invalid(self):
        val = MustOpt.new(1)
        val.unset()
        assert_that(val.valid(), equal_to(False))

    def test_set_value_makes_container_valid(self):
        val = MustOpt.new()
        val.set(1)
        assert_that(val.valid(), equal_to(True))

    def test_set_none_makes_container_invalid(self):
        val = MustOpt.new()
        val.set(None)
        assert_that(val.valid(), equal_to(False))

    def test_must_from_valid_container_works(self):
        assert_that(MustOpt.new(1).must(), equal_to(1))

    def test_must_from_invalid_container_raises_exception(self):
        try:
            MustOpt.new().must()
        except RuntimeError as e:
            assert_that(str(e), equal_to('Underlying value is not valid'))
