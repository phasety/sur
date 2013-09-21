from unittest import TestCase
from decimal import Decimal

import numpy as np
from numpy.testing import assert_array_equal


from sur.models import Compound, Mixture, MixtureFraction


class TestMixture(TestCase):

    def setUp(self):
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    def test_add_order_is_preserved(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.co2, 0.3)
        self.m.add(self.methane, 0.2)
        expected = [self.ethane, self.co2, self.methane]
        self.assertEqual(list(self.m.compounds.all()), expected)

    def test_sort(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.co2, 0.3)
        self.m.add(self.methane, 0.2)
        expected = [self.methane, self.co2, self.ethane]
        self.m.sort()
        self.assertEqual(list(self.m.compounds.all()), expected)
        assert_array_equal(self.m.z, np.array([0.2, 0.3, 0.1]))

    def test_fraction_order_is_preserved(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.3)
        assert_array_equal(self.m.z, np.array([0.1, 0.2, 0.3]))

    def test_field_tc(self):
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.1)
        self.m.add(self.ethane, 0.3)
        assert_array_equal(self.m.tc, [self.methane.tc, self.co2.tc, self.ethane.tc])

    def test_field_pc(self):
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.1)
        self.m.add(self.ethane, 0.3)
        assert_array_equal(self.m.pc, [self.methane.pc, self.co2.pc, self.ethane.pc])

    def test_field_vc(self):
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.1)
        self.m.add(self.ethane, 0.3)
        assert_array_equal(self.m.vc, [self.methane.vc, self.co2.vc, self.ethane.vc])


class TestMixtureAdd(TestCase):

    def setUp(self):
        MixtureFraction.objects.all().delete()
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    def test_simple_add(self):
        assert MixtureFraction.objects.all().count() == 0
        self.m.add(self.ethane, 0.1)
        self.assertEqual(MixtureFraction.objects.count(), 1)
        mf = MixtureFraction.objects.all().get()
        self.assertEqual(mf.mixture, self.m)
        self.assertEqual(mf.compound, self.ethane)
        self.assertEqual(mf.fraction, Decimal('0.1'))

    def test_add_by_name(self):
        self.m.add('ethane', 0.1)
        mf = MixtureFraction.objects.all().get()
        self.assertEqual(mf.mixture, self.m)
        self.assertEqual(mf.compound, self.ethane)
        self.assertEqual(mf.fraction, Decimal('0.1'))

    def test_add_by_formula(self):
        self.m.add('co2', 0.1)
        mf = MixtureFraction.objects.all().get()
        self.assertEqual(mf.mixture, self.m)
        self.assertEqual(mf.compound, self.co2)
        self.assertEqual(mf.fraction, Decimal('0.1'))

    def test_add_fraction_as_str(self):
        self.m.add('ethane', '0.1')
        mf = MixtureFraction.objects.all().get()
        self.assertEqual(mf.mixture, self.m)
        self.assertEqual(mf.compound, self.ethane)
        self.assertEqual(mf.fraction, Decimal('0.1'))

    def test_cant_add_greater_than_1(self):
        with self.assertRaises(ValueError) as v:
            self.m.add('ethane', '1.2')
        self.assertEqual(v.exception.message, 'Add this fraction would exceed 1.0. '
                                              'Max fraction allowed is 1.0')

    def test_cant_add_greater_than_remaining(self):
        self.m.add('ethane', '0.6')
        with self.assertRaises(ValueError) as v:
            self.m.add('ethane', '0.6')
        self.assertEqual(v.exception.message, 'Add this fraction would exceed 1.0. '
                                              'Max fraction allowed is 0.4000')

    def test_add_without_fraction_add_remaining(self):
        self.m.add('ethane', '0.6')
        self.m.add('co2')
        mf = MixtureFraction.objects.get(mixture=self.m, compound=self.co2)
        self.assertEqual(mf.fraction, Decimal('0.4'))
