from unittest import TestCase
from decimal import Decimal

import numpy as np
from numpy.testing import assert_array_equal

from sur.models import (Compound, Mixture, MixtureFraction,
                        K0InteractionParameter)
from django.db.utils import IntegrityError


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


class TestInteraction(TestCase):

    def setUp(self):
        K0InteractionParameter.objects.all().delete()
        self.k = K0InteractionParameter.objects.create(eos='RKPR', value=0.4)
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='ETHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')
        self.k.compounds.add(self.ethane)
        self.k.compounds.add(self.co2)

    def test_find_order_doesnt_import(self):
        found1 = K0InteractionParameter.objects.find('RKPR', self.ethane)[0]
        found2 = K0InteractionParameter.objects.find('RKPR', self.co2)[0]
        found3 = K0InteractionParameter.objects.find('RKPR', self.co2, self.ethane)[0]
        self.assertEqual(found1, found2)
        self.assertEqual(found1, found3)

    def test_doesnt_accept_more_than_2_compounds(self):
        with self.assertRaises(IntegrityError) as e:
            self.k.compounds.add(self.ethane)
        self.assertIn('This interaction parameter has its compounds',
                      e.exception.message)

    def test_can_add_another_k0_for_one_shared_compounds(self):
        other_k = K0InteractionParameter.objects.create(eos='RKPR', value=0.1)
        other_k.compounds.add(self.ethane)
        other_k.compounds.add(self.methane)
        found1 = K0InteractionParameter.objects.find('RKPR', self.ethane)
        self.assertEqual(found1.count(), 2)

    def test_cant_add_another_global_k0_for_both_shared_compounds(self):
        other_k = K0InteractionParameter.objects.create(eos='RKPR', value=0.1)
        other_k.compounds.add(self.ethane)
        with self.assertRaises(IntegrityError) as e:
            other_k.compounds.add(self.co2)
        self.assertIn('Already exists a parameter matching these condition',
                      e.exception.message)

    def test_can_add_per_mixture_k0_for_existed_global_compounds(self):
        m = Mixture()
        m.add(self.methane, 0.2)
        m.add(self.co2, 0.1)
        other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                        value=0.1,
                                                        mixture=m)
        other_k.compounds.add(self.ethane)
        other_k.compounds.add(self.co2)
        found1 = K0InteractionParameter.objects.find('RKPR', self.ethane, mixture=m)
        self.assertEqual(found1.count(), 2)

    def test_per_mixture_compound_is_first(self):
        m = Mixture()
        m.add(self.methane, 0.2)
        m.add(self.co2, 0.1)
        other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                        value=0.1,
                                                        mixture=m)
        other_k.compounds.add(self.ethane)
        other_k.compounds.add(self.co2)
        k0s = K0InteractionParameter.objects.find('RKPR', self.ethane, mixture=m)
        self.assertEqual(k0s[0].mixture, m)
        self.assertEqual(k0s[0].value, 0.1)
        self.assertIsNone(k0s[1].mixture)
        self.assertEqual(k0s[1].value, 0.4)

    def test_same_custom_k_for_different_mixture_doesnt_interfer(self):
        assert K0InteractionParameter.objects.filter(compounds=self.ethane,
                                                     mixture__isnull=True).count() == 1
        for i in range(2):
            m = Mixture()
            m.add(self.methane, 0.2)
            m.add(self.co2, 0.1)
            other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                            value=0.1,
                                                            mixture=m)
            other_k.compounds.add(self.ethane)
            other_k.compounds.add(self.co2)
        found1 = K0InteractionParameter.objects.find('RKPR', self.ethane, mixture=m)
        self.assertEqual(found1.count(), 2)

    def test_cant_add_already_existent_per_mixture_k0(self):
        m = Mixture()
        m.add(self.methane, 0.2)
        m.add(self.co2, 0.1)
        k = K0InteractionParameter.objects.create(eos='RKPR',
                                                  value=0.1,
                                                  mixture=m)
        k.compounds.add(self.ethane)
        k.compounds.add(self.co2)

        other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                        value=0.1,
                                                        mixture=m)
        other_k.compounds.add(self.ethane)
        with self.assertRaises(IntegrityError) as e:
            other_k.compounds.add(self.co2)
        self.assertIn('Already exists a parameter matching these condition',
                      e.exception.message)


class TestK0(TestCase):

    def setUp(self):

        K0InteractionParameter.objects.all().delete()
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')
        self.m.add(self.ethane, 0.1)
        self.m.add(self.co2, 0.3)
        self.m.add(self.methane, 0.2)

    def test_all_zeros_by_default(self):
        assert_array_equal(self.m.k0('RKPR'), np.zeros((3, 3)))

    def test_there_is_a_global_k(self):
        k = K0InteractionParameter.objects.create(eos='RKPR',
                                                  value=0.1)
        k.compounds.add(self.ethane)
        k.compounds.add(self.methane)

        expected = np.zeros((3, 3))
        expected[0, 2] = expected[2, 0] = k.value

        assert_array_equal(self.m.k0('RKPR'), expected)

    def test_there_is_a_global_k_a_mixture_override(self):
        k = K0InteractionParameter.objects.create(eos='RKPR',
                                                  value=0.1)
        k.compounds.add(self.ethane)
        k.compounds.add(self.methane)

        k2 = K0InteractionParameter.objects.create(eos='RKPR',
                                                   value=0.2,
                                                   mixture=self.m)
        k2.compounds.add(self.ethane)
        k2.compounds.add(self.methane)

        expected = np.zeros((3, 3))
        expected[0, 2] = expected[2, 0] = k2.value

        assert_array_equal(self.m.k0('RKPR'), expected)

    def test_global_k_for_same_custom_for_other_interaction(self):
        k = K0InteractionParameter.objects.create(eos='RKPR',
                                                  value=0.1)
        k.compounds.add(self.ethane)
        k.compounds.add(self.methane)

        k2 = K0InteractionParameter.objects.create(eos='RKPR',
                                                   value=0.2,
                                                   mixture=self.m)
        k2.compounds.add(self.ethane)
        k2.compounds.add(self.co2)

        expected = np.zeros((3, 3))
        expected[0, 1] = expected[1, 0] = k2.value
        expected[0, 2] = expected[2, 0] = k.value

        assert_array_equal(self.m.k0('RKPR'), expected)


