from unittest import TestCase
from decimal import Decimal

import numpy as np
from numpy.testing import assert_array_equal


from sur.models import (Compound, Mixture, MixtureFraction,
                        K0InteractionParameter, TstarInteractionParameter,
                        EosEnvelope, set_interaction)
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


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
        self.assertEqual(list(self.m.compounds), expected)

    def test_sort(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.co2, 0.3)
        self.m.add(self.methane, 0.2)
        expected = [self.methane, self.ethane, self.co2, ]
        self.m.sort()
        self.assertEqual(list(self.m.compounds), expected)
        assert_array_equal(self.m.z, np.array([0.2, 0.1, 0.3]))

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

    def test_decimal_round(self):
        self.m['ETHANE'] = u'0.4'
        self.m['CARBON DIOXIDE'] = u'0.3'
        self.m['n-PENTANE'] = u'0.2'
        self.m['n-HEXANE'] = 0.1
        self.assertIsNone(self.m.clean())


class TestMixtureMagicMeths(TestCase):

    def setUp(self):
        Mixture.objects.all().delete()
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    def test__len__is_zero(self):
        assert self.m.fractions.count() == 0
        self.assertEqual(len(self.m), 0)

    def test__len__zero(self):
        self.m.add(self.methane, 0.2)
        assert self.m.fractions.count() == 1
        self.assertEqual(len(self.m), 1)

    def test_simple_get_attr(self):
        self.m.add(self.methane, 0.2)
        self.assertEqual(self.m[self.methane], Decimal('0.2'))

    def test_get_attr_using_str(self):
        self.m.add(self.methane, 0.2)
        self.assertEqual(self.m['methane'], Decimal('0.2'))

    def test_get_attr_raises_type_exception_for_other_types(self):
        self.m.add(self.methane, 0.2)
        with self.assertRaises(TypeError):
            self.m[1j]

    def test_get_attr_raises_keyexception_for_unknown_key(self):
        with self.assertRaises(KeyError) as e:
            self.m['methane']
        self.assertIn('is not part of this mixture', e.exception.message)

    def test_get_attr_raises_keyexception_for_unknown_keys(self):
        with self.assertRaises(KeyError) as e:
            self.m['unknown_compound']
        self.assertIn('unknown compound', e.exception.message)

    def test_get_attr_raises_keyexception_for_unknown_compound_keys(self):
        with self.assertRaises(KeyError):
            self.m[self.methane]

    def test_simple_set_attr(self):
        self.m[self.methane] = 0.2
        self.assertEqual(self.m[self.methane], Decimal('0.2'))

    def test_simple_set_attr_as_str(self):
        self.m[self.ethane] = '0.1'
        self.assertEqual(self.m[self.ethane], Decimal('0.1'))

    def test_set_attr_overrides_previous(self):
        self.m.add(self.ethane, '0.1')
        self.m[self.ethane] = '0.4'
        self.assertEqual(self.m[self.ethane], Decimal('0.4'))

    def test_set_overrides_fail_is_sum_is_gt_1(self):
        self.m[self.ethane] = '0.4'
        self.m[self.methane] = '0.5'
        with self.assertRaises(ValueError):
            self.m[self.methane] = '0.7'
        assert_array_equal(self.m.z, [0.4, 0.5])

    def test_set_overrides_not_fail_is_sum_is_lte_1(self):
        self.m[self.ethane] = '0.4'
        self.m[self.methane] = '0.5'
        self.m[self.methane] = '0.3'
        assert_array_equal(self.m.z, [0.4, 0.3])

    def test_set_attr_raises_keyexception_for_unknown_keys(self):
        with self.assertRaises(KeyError):
            self.m['unknown_compound'] = 0.4

    def test_del_item(self):
        self.m[self.methane] = 0.2
        del self.m[self.methane]
        self.assertEqual(len(self.m), 0)

    def test_del_item_preserve_positions(self):
        self.m[self.methane] = 0.1
        self.m[self.ethane] = 0.2
        self.m[self.co2] = 0.3
        del self.m[self.ethane]
        expected = [(self.methane, Decimal('0.1')),
                    (self.co2, Decimal('0.3'))]
        self.assertEqual(list(self.m), expected)
        del self.m[self.methane]
        self.assertEqual(list(self.m), [(self.co2, Decimal('0.3'))])

    def test_del_attr_raises_keyexception_for_unknown_keys(self):
        with self.assertRaises(KeyError) as e:
            del self.m['unknown_compound']
        self.assertIn('unknown compound', e.exception.message)

    def test_del_attr_raises_keyexception_for_compound_not_in_the_mixture_keys(self):
        self.m[self.methane] = 0.2
        with self.assertRaises(KeyError) as e:
            del self.m['ethane']
        self.assertIn('is not part of this mixture', e.exception.message)

    def test_iter(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.methane, 0.2)
        self.m.add(self.co2, 0.3)
        expected = [(self.ethane, Decimal('0.1')),
                    (self.methane, Decimal('0.2')),
                    (self.co2, Decimal('0.3'))]
        self.assertEqual([i for i in self.m], expected)


class TestMixtureAdd(TestCase):

    def setUp(self):
        MixtureFraction.objects.all().delete()
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')
        self.methane = Compound.objects.get(name='METHANE')

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

    def test_add_many_iterables(self):
        self.m.add_many([self.ethane, self.methane, self.co2], [0.1, 0.2, 0.3])
        expected = [(self.ethane, Decimal('0.1')),
                    (self.methane, Decimal('0.2')),
                    (self.co2, Decimal('0.3'))]
        self.assertEqual([i for i in self.m], expected)

    def test_add_many_string(self):
        self.m.add_many("ethane methane co2", "0.1 0.2 0.3")
        expected = [(self.ethane, Decimal('0.1')),
                    (self.methane, Decimal('0.2')),
                    (self.co2, Decimal('0.3'))]
        self.assertEqual([i for i in self.m], expected)

    def test_add_many_must_have_same_size(self):
        with self.assertRaises(ValueError):
            self.m.add_many("ethane methane", "0.1 0.2 0.3")

    def test_cant_add_greater_than_1(self):
        with self.assertRaises(ValueError) as v:
            self.m.add('ethane', '1.2')
        self.assertEqual(v.exception.message, 'Add this fraction would exceed 1.0. '
                                              'Max fraction allowed is 1.0')

    def test_cant_add_greater_than_remaining(self):
        self.m.add('ethane', '0.6')
        with self.assertRaises(ValueError) as v:
            self.m.add('methane', '0.6')
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
        self.methane = Compound.objects.get(name='METHANE')
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


class TestSetInteractionFunction(TestCase):

    def setUp(self):
        K0InteractionParameter.objects.all().delete()
        TstarInteractionParameter.objects.all().delete()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')

    def test_set_interaction(self):
        set_interaction('RKPR', 'k0', 'ethane', 'methane', value=0.4)
        k0 = K0InteractionParameter.objects.get()
        self.assertIn(self.ethane, k0.compounds.all())
        self.assertIn(self.methane, k0.compounds.all())
        self.assertEqual(k0.value, 0.4)
        self.assertIsNone(k0.mixture)
        self.assertEqual(k0.eos, 'RKPR')

    def test_set_interaction_update(self):
        set_interaction('RKPR', 'k0', 'ethane', 'methane', value=0.4)
        set_interaction('RKPR', 'k0', 'methane', 'ethane', value=0.5)
        k0 = K0InteractionParameter.objects.get()  # just one
        self.assertIn(self.ethane, k0.compounds.all())
        self.assertIn(self.methane, k0.compounds.all())
        self.assertEqual(k0.value, 0.5)
        self.assertIsNone(k0.mixture)
        self.assertEqual(k0.eos, 'RKPR')

    def test_set_interaction_for_mix(self):
        m = Mixture()
        m.save()
        # shouldn't ensure compounds belongs to the mixture?
        set_interaction('PR', 'tstar', 'ethane', 'methane', value=0.1, mixture=m)
        i = TstarInteractionParameter.objects.get()
        self.assertIn(self.ethane, i.compounds.all())
        self.assertIn(self.methane, i.compounds.all())
        self.assertEqual(i.value, 0.1)
        self.assertEqual(i.mixture, m)
        self.assertEqual(i.eos, 'PR')

    def test_matrix_tstar(self):
        m = Mixture()
        m['ethane'] = 0.1
        m['methane'] = 0.9
        m.set_interaction('PR', 'tstar', 'ethane', 'methane', value=0.43)
        assert_array_equal(m.tstar('pr'), np.array([[0, 0.43], [0.43, 0]]))

    def test_matrix_kij_rkpr(self):
        m = Mixture()
        m['ethane'] = 0.1
        m['methane'] = 0.8
        m['co2'] = 0.1
        m.set_interaction('rkpr', 'kij', 'ethane', 'co2', value=0.43)
        assert_array_equal(m.tstar('pr'), np.array([[0, 0, 0.43],
                                                    [0, 0, 0.],
                                                    [0.43, 0, 0]]))



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


class TestEnvelope(TestCase):

    def setUp(self):
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    def test_envelope_requires_a_clean_mixture(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.co2, 0.3)
        self.m.add(self.methane, 0.5)
        assert self.m.total_z == Decimal('0.9')
        with self.assertRaises(ValidationError):
            EosEnvelope.objects.create(mixture=self.m)

        self.m[self.methane] = 0.6   # total_z = 1.0
        assert self.m.clean() is None
        # not raises
        EosEnvelope.objects.create(mixture=self.m)

    def test_envelope_object_calc_env_on_save(self):
        self.m.add(self.ethane, 1)
        env = EosEnvelope.objects.create(mixture=self.m)
        self.assertIsInstance(env.p, np.ndarray)
        self.assertIsInstance(env.t, np.ndarray)
        self.assertIsInstance(env.rho, np.ndarray)
        self.assertTrue(env.p.shape == env.t.shape == env.rho.shape)

        self.assertIsInstance(env.p_cri, np.ndarray)
        self.assertIsInstance(env.t_cri, np.ndarray)
        self.assertIsInstance(env.rho_cri, np.ndarray)
        self.assertTrue(env.p_cri.shape == env.t_cri.shape == env.rho_cri.shape)

    def test_get_default_envelope_is_the_same(self):
        self.m.add(self.ethane, 1)
        env = EosEnvelope.objects.create(mixture=self.m)
        self.assertEqual(env, self.m.get_envelope())


class TestFlash(TestCase):

    def setUp(self):
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    def test_flash_requires_a_clean_mixture(self):
        self.m.add(self.ethane, 0.1)
        self.m.add(self.co2, 0.3)
        self.m.add(self.methane, 0.5)
        assert self.m.total_z == Decimal('0.9')
        with self.assertRaises(ValidationError):
            self.m.get_flash(10., 20.)

        self.m[self.methane] = 0.6   # total_z = 1.0
        assert self.m.clean() is None
        # not raises
        self.m.get_flash(10., 20.)
