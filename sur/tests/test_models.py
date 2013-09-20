from unittest import TestCase
import numpy as np
from numpy.testing import assert_array_equal

from sur.models import Compound, Mixture


class TestMixture(TestCase):

    def setUp(self):
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    def test_order_is_weight(self):

        self.m.add(self.ethane, 0.1)
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.3)

        expected = sorted([self.ethane, self.methane, self.co2],
                          key=lambda c: c.weight)
        self.assertEqual(list(self.m.compounds.all()), expected)

    def test_fraction_order_is_preserved(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.3)
        assert_array_equal(self.m.z, np.array([0.2, 0.3, 0.1]))





