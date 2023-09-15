import unittest

import numpy as np

import powerfit


class Test_Limit(unittest.TestCase):
    """
    Limit class.
    """

    def test_main(self):
        x = np.random.random(100).reshape(10, 10)
        lim = powerfit.Limit()

        for datum in x:
            lim += datum

        self.assertAlmostEqual(lim.lower, np.min(x))
        self.assertAlmostEqual(lim.upper, np.max(x))


class Test_powerlaw(unittest.TestCase):
    """
    Fit a powerlaw.
    """

    def test_prefactor_exponent(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * x**3.4
        fit = powerfit.powerlaw(x, y)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], 3.4))

    def test_prefactor(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * x**3.4
        fit = powerfit.powerlaw(x, y, exponent=3.4)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], 3.4))

    def test_exponent(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * x**3.4
        fit = powerfit.powerlaw(x, y, prefactor=1.2)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], 3.4))


class Test_exp(unittest.TestCase):
    """
    Fit an exponential.
    """

    def test_prefactor_exponent(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * 3.4)
        fit = powerfit.exp(x, y)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], 3.4))

    def test_prefactor_negative_exponent(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * -3.4)
        fit = powerfit.exp(x, y)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], -3.4))

    def test_prefactor(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * 3.4)
        fit = powerfit.exp(x, y, exponent=3.4)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], 3.4))

    def test_exponent(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 * np.exp(x * 3.4)
        fit = powerfit.exp(x, y, prefactor=1.2)
        self.assertTrue(np.isclose(fit["prefactor"], 1.2))
        self.assertTrue(np.isclose(fit["exponent"], 3.4))


class Test_log(unittest.TestCase):
    """
    Fit an logarithmic function.
    """

    def test_prefactor_exponent(self):
        x = np.linspace(0, 1, 1000)[1:]
        y = 1.2 + 3.4 * np.log(x)
        fit = powerfit.log(x, y)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], 3.4))

    def test_prefactor_negative_prefactor(self):
        x = np.linspace(0, 1, 1000)[1:]
        y = 1.2 - 3.4 * np.log(x)
        fit = powerfit.log(x, y)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], -3.4))

    def test_prefactor(self):
        x = np.linspace(0, 1, 1000)[1:]
        y = 1.2 + 3.4 * np.log(x)
        fit = powerfit.log(x, y, slope=3.4)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], 3.4))

    def test_exponent(self):
        x = np.linspace(0, 1, 1000)[1:]
        y = 1.2 + 3.4 * np.log(x)
        fit = powerfit.log(x, y, offset=1.2)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], 3.4))


class Test_linear(unittest.TestCase):
    """
    Fit a linear.
    """

    def test_offset_slope(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 + 3.4 * x
        fit = powerfit.linear(x, y)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], 3.4))

    def test_slope(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 + 3.4 * x
        fit = powerfit.linear(x, y, slope=3.4)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], 3.4))

    def test_offset(self):
        x = np.linspace(0, 1, 1000)
        y = 1.2 + 3.4 * x
        fit = powerfit.linear(x, y, offset=1.2)
        self.assertTrue(np.isclose(fit["offset"], 1.2))
        self.assertTrue(np.isclose(fit["slope"], 3.4))
