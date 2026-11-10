import unittest

from implementation import clamp


class ClampReturnValueTests(unittest.TestCase):
    def test_value_within_bounds_is_returned(self):
        self.assertEqual(clamp(3, 1, 5), 3)
        self.assertEqual(clamp(0, -2, 2), 0)
        self.assertEqual(clamp(-5, -9, -2), -5)

    def test_value_below_lower_is_clipped_to_lower(self):
        self.assertEqual(clamp(-8, -3, 4), -3)
        self.assertEqual(clamp(-100, -3, 4), -3)

    def test_value_above_upper_is_clipped_to_upper(self):
        self.assertEqual(clamp(12, -3, 4), 4)
        self.assertEqual(clamp(100, -3, 4), 4)

    def test_equal_bounds_clamp_to_that_bound(self):
        self.assertEqual(clamp(9, 2, 2), 2)
        self.assertEqual(clamp(2, 2, 2), 2)
        self.assertEqual(clamp(-5, 2, 2), 2)

    def test_negative_values_are_not_absolute_valued(self):
        self.assertEqual(clamp(-5, -9, -2), -5)
        self.assertEqual(clamp(-4, -9, 0), -4)
        self.assertEqual(clamp(-1, -9, -2), -2)

    def test_result_is_exact_builtin_int(self):
        result = clamp(3, 1, 5)
        self.assertIs(type(result), int)
        clipped = clamp(12, -3, 4)
        self.assertIs(type(clipped), int)


class ClampBoundsTests(unittest.TestCase):
    def test_reversed_bounds_raise_value_error(self):
        with self.assertRaises(ValueError):
            clamp(1, 5, 2)

    def test_reversed_bounds_checked_even_with_value_outside(self):
        with self.assertRaises(ValueError):
            clamp(100, 5, 2)
        with self.assertRaises(ValueError):
            clamp(-100, 5, 2)

    def test_equal_bounds_are_valid_not_reversed(self):
        self.assertEqual(clamp(1, 2, 2), 2)


class ClampTypeTests(unittest.TestCase):
    def _assert_all_type_errors(self):
        bad = [True, False, 1.0, 3.5, "3", None, [1], (1,), {1: 2}, {1}]
        for b in bad:
            for args in (
                (b, 0, 2),
                (1, b, 2),
                (1, 0, b),
            ):
                with self.subTest(args=args):
                    with self.assertRaises(TypeError):
                        clamp(*args)

    def test_non_int_inputs_raise_type_error(self):
        self._assert_all_type_errors()

    def test_bool_is_rejected(self):
        for args in ((True, 0, 2), (False, 0, 2), (1, True, 2), (1, 0, True)):
            with self.subTest(args=args):
                with self.assertRaises(TypeError):
                    clamp(*args)

    def test_float_is_rejected(self):
        for args in ((1.0, 0, 2), (1, 0.5, 2), (1, 0, 2.0)):
            with self.subTest(args=args):
                with self.assertRaises(TypeError):
                    clamp(*args)

    def test_types_checked_before_comparing_reversed_bounds(self):
        with self.assertRaises(TypeError):
            clamp(None, 5, 2)
        with self.assertRaises(TypeError):
            clamp(True, 5, 2)


if __name__ == "__main__":
    unittest.main()
