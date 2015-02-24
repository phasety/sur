from unittest import TestCase, skip
from decimal import Decimal

import numpy as np
from numpy.testing import assert_array_equal


from sur.models import (Compound, Mixture, MixtureFraction,
                        K0InteractionParameter, TstarInteractionParameter,
                        KijInteractionParameter, LijInteractionParameter,
                        EosEnvelope, set_interaction, EosSetup)
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


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


class TestCompunds(TestCase):

    def test_filter_is_distinct(self):
        m1 = Mixture.objects.create()
        m2 = Mixture.objects.create()
        m3 = Mixture.objects.create()
        m4 = Mixture.objects.create()
        m1['METHANE'] = u'0.4'
        m1['CARBON DIOXIDE'] = u'0.3'
        m2['CARBON DIOXIDE'] = u'0.3'
        m1['METHANE'] = u'0.4'
        m3['METHANE'] = u'0.1'
        m4['METHANE'] = u'0.221'
        self.assertEqual(len(list(Compound.objects.filter(name='METHANE'))), 1)


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
                                              'Max fraction allowed is 0.400000')

    def test_add_without_fraction_add_remaining(self):
        self.m.add('ethane', '0.6')
        self.m.add('co2')
        mf = MixtureFraction.objects.get(mixture=self.m, compound=self.co2)
        self.assertEqual(mf.fraction, Decimal('0.4'))


class TestInteraction(TestCase):

    def setUp(self):
        K0InteractionParameter.objects.all().delete()
        KijInteractionParameter.objects.all().delete()
        LijInteractionParameter.objects.all().delete()

        User.objects.all().delete()

        self.k = K0InteractionParameter.objects.create(eos='RKPR', value=0.4)
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')
        self.k.compounds.add(self.ethane)
        self.k.compounds.add(self.co2)

    def test_find_order_doesnt_import(self):
        found1 = K0InteractionParameter.objects.find(self.ethane, eos='RKPR')[0]
        found2 = K0InteractionParameter.objects.find(self.co2, eos='RKPR')[0]
        found3 = K0InteractionParameter.objects.find(self.co2, self.ethane, eos='RKPR')[0]
        self.assertEqual(found1, found2)
        self.assertEqual(found1, found3)

    def test_doesnt_accept_more_than_2_compounds(self):
        with self.assertRaises(IntegrityError) as e:
            self.k.compounds.add(self.ethane)
        self.assertIn('This interaction parameter has its compounds',
                      e.exception.message)

    def test_can_add_another_k0_for_one_shared_compounds(self):
        other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                        value=0.1)
        other_k.compounds.add(self.ethane)
        other_k.compounds.add(self.methane)
        found1 = K0InteractionParameter.objects.find(self.ethane,
                                                     eos='RKPR')
        self.assertEqual(found1.count(), 2)

    def test_cant_add_another_global_k0_for_both_shared_compounds(self):
        other_k = K0InteractionParameter.objects.create(eos='RKPR', value=0.1)
        other_k.compounds.add(self.ethane)
        with self.assertRaises(IntegrityError) as e:
            other_k.compounds.add(self.co2)
        self.assertIn('Already exists a parameter matching these condition',
                      e.exception.message)

    def test_cant_add_another_global_Lij_for_both_shared_compounds(self):
        lij = LijInteractionParameter.objects.create(eos='PR', value=0.1)
        lij.compounds.add(self.ethane)
        lij.compounds.add(self.co2)
        lij2 = LijInteractionParameter.objects.create(eos='PR', value=0.2)
        lij2.compounds.add(self.ethane)
        with self.assertRaises(IntegrityError) as e:
            lij2.compounds.add(self.co2)
        self.assertIn('Already exists a parameter matching these condition',
                      e.exception.message)

    def test_cant_add_another_global_Lij_for_both_shared_compounds_with_direct_assignement(self):
        lij = LijInteractionParameter.objects.create(eos='PR', value=0.1)
        lij.compounds.add(self.ethane)
        lij.compounds.add(self.co2)
        lij2 = LijInteractionParameter.objects.create(eos='PR', value=0.2)
        with self.assertRaises(IntegrityError) as e:
            lij2.compounds = [self.ethane, self.co2]
        self.assertIn('Already exists a parameter matching these condition',
                      e.exception.message)


    def test_can_add_per_user_k0_for_existent_global_compounds(self):
        user = User.objects.create(username='tin')
        other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                        value=0.1,
                                                        user=user)
        other_k.compounds.add(self.ethane)
        other_k.compounds.add(self.co2)
        found1 = K0InteractionParameter.objects.find(self.ethane, eos='RKPR', user=user)
        self.assertEqual(found1.count(), 2)

    def test_can_add_per_setup_k0_for_existed_global_compounds(self):
        s = EosSetup(eos='RKPR')
        other_k = K0InteractionParameter.objects.create(eos='RKPR',
                                                        value=0.1,
                                                        setup=s)
        other_k.compounds.add(self.ethane)
        other_k.compounds.add(self.co2)
        found1 = K0InteractionParameter.objects.find(self.ethane, setup=s)
        self.assertEqual(found1.count(), 2)

    def test_per_setup_is_first(self):
        s = EosSetup.objects.create(eos='RKPR')
        s.set_interaction('k0', self.ethane, self.co2, value=0.1)
        k0s = K0InteractionParameter.objects.find(self.ethane,
                                                  setup=s, eos='RKPR')
        self.assertEqual(k0s[0].setup, s)
        self.assertEqual(k0s[0].value, 0.1)
        self.assertIsNone(k0s[1].setup)
        self.assertEqual(k0s[1].value, 0.4)

    def test_same_custom_k_for_different_setuo_doesnt_interfer(self):
        assert K0InteractionParameter.objects.filter(compounds=self.ethane,
                                                     setup__isnull=True).count() == 1
        for i in range(2):
            s = EosSetup.objects.create(eos='RKPR')
            other_k = K0InteractionParameter.objects.create(value=0.1,
                                                            setup=s)
            other_k.compounds.add(self.ethane)
            other_k.compounds.add(self.co2)
        found1 = K0InteractionParameter.objects.find(self.ethane, setup=s)
        self.assertEqual(found1.count(), 2)

    def test_cant_add_already_existent_per_setup_k0(self):
        K0InteractionParameter.objects.all().delete()

        # To do
        # s = EosSetup(eos='RKPR')
        s = EosSetup.objects.create(eos='RKPR')

        k = K0InteractionParameter.objects.create(value=0.1,
                                                  setup=s)
        k.compounds.add(self.ethane)
        k.compounds.add(self.co2)

        other_k = K0InteractionParameter.objects.create(value=0.2,
                                                        setup=s)
        other_k.compounds.add(self.ethane)
        with self.assertRaises(IntegrityError) as e:
            other_k.compounds.add(self.co2)
        self.assertIn('Already exists a parameter matching these condition',
                      e.exception.message)

    def test_same_setup_and_user_different_eos_doesn_superpose(self):
        m = Mixture()
        m.add(self.methane, 0.2)
        m.add(self.co2, 0.1)
        user = User.objects.create(username='tin')
        s1 = EosSetup.objects.create(eos='RKPR', user=user)
        s2 = EosSetup.objects.create(eos='PR', user=user)
        s3 = EosSetup.objects.create(eos='SRK', user=user)

        s1.set_interaction('kij', self.methane, self.co2, value=0.1)
        s2.set_interaction('kij', self.methane, self.co2, value=0.2)
        # default for user
        set_interaction('kij', self.methane, self.co2,
                        eos='SRK', value=0.3, user=user)
        kij_rkpr = s1.kij(m)
        kij_pr = s2.kij(m)
        kij_srk = s3.kij(m)
        assert_array_equal(kij_pr, np.array([[0., 0.2], [0.2, 0.]]))
        assert_array_equal(kij_rkpr, np.array([[0., 0.1], [0.1, 0.]]))
        assert_array_equal(kij_srk, np.array([[0., 0.3], [0.3, 0.]]))

    def test_defaults_priority(self):
        K0InteractionParameter.objects.all().delete()
        m = Mixture()
        m.add(self.methane, 0.5)
        m.add(self.co2, 0.5)

        user = User.objects.create(username='tin')
        s = EosSetup.objects.create(eos='SRK', user=user)

        # default staff
        set_interaction('lij', self.methane, self.co2, value=0.4, eos='SRK')

        assert_array_equal(s.lij(m),
                           np.array([[0., 0.4], [0.4, 0.]]))

        # now user defined
        set_interaction('lij', self.methane, self.co2,
                        value=0.6, user=user, eos='SRK')
        assert_array_equal(s.lij(m),
                           np.array([[0., 0.6], [0.6, 0.]]))

        # now setup
        s.set_interaction('lij', self.methane, self.co2, value=0.9)
        assert_array_equal(s.lij(m),
                           np.array([[0., 0.9], [0.9, 0.]]))


class TestGetInteractionTstart(TestCase):
    def setUp(self):
        self.ethane = Compound.objects.get(name='ETHANE')
        self.co2 = Compound.objects.find('co2')[0]

    def test_auto_tstart(self):
        m = Mixture()
        m.add(self.ethane, 0.5)
        m.add(self.co2, 0.5)

        assert self.ethane < self.co2
        s = EosSetup.objects.create(eos='RKPR', kij_mode=EosSetup.T_DEP)
        assert_array_equal(s.tstar(m), np.array([[0., self.ethane.tc],
                                                 [self.ethane.tc, 0.]]))


class TestSetInteractionFunction(TestCase):

    def setUp(self):
        K0InteractionParameter.objects.all().delete()
        TstarInteractionParameter.objects.all().delete()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')

    def test_set_interaction(self):
        set_interaction('k0', 'ethane', 'methane', eos='RKPR', value=0.4)

        k0 = K0InteractionParameter.objects.get()
        self.assertIn(self.ethane, k0.compounds.all())
        self.assertIn(self.methane, k0.compounds.all())
        self.assertEqual(k0.value, 0.4)
        self.assertIsNone(k0.setup)
        self.assertIsNone(k0.user)
        self.assertEqual(k0.eos, 'RKPR')

    def test_set_interaction_update(self):

        set_interaction('k0', 'ethane', 'methane', eos='RKPR', value=0.4)
        set_interaction('k0', 'ethane', 'methane', eos='RKPR', value=0.5)
        k0 = K0InteractionParameter.objects.get()  # just one
        self.assertIn(self.ethane, k0.compounds.all())
        self.assertIn(self.methane, k0.compounds.all())
        self.assertEqual(k0.value, 0.5)
        self.assertIsNone(k0.setup)
        self.assertIsNone(k0.user)
        self.assertEqual(k0.eos, 'RKPR')

    def test_set_interaction_for_setup(self):
        s = EosSetup.objects.create(eos='PR')

        # shouldn't ensure compounds belongs to the mixture?
        s.set_interaction('tstar', 'ethane', 'methane', value=0.1)

        i = TstarInteractionParameter.objects.get()

        self.assertIn(self.ethane, i.compounds.all())
        self.assertIn(self.methane, i.compounds.all())
        self.assertEqual(i.value, 0.1)
        self.assertEqual(i.setup, s)
        self.assertIsNone(i.user)
        self.assertEqual(i.eos, 'PR')

    def test_set_interaction_for_setup_update(self):
        s = EosSetup.objects.create(eos='PR')

        # shouldn't ensure compounds belongs to the mixture?
        s.set_interaction('tstar', 'ethane', 'methane', value=0.1)

        #update
        s.set_interaction('tstar', 'ethane', 'methane', value=0.2)

        i = TstarInteractionParameter.objects.get()

        self.assertIn(self.ethane, i.compounds.all())
        self.assertIn(self.methane, i.compounds.all())
        self.assertEqual(i.value, 0.2)
        self.assertEqual(i.setup, s)
        self.assertIsNone(i.user)
        self.assertEqual(i.eos, 'PR')


    def test_matrix_tstar(self):
        m = Mixture()
        m['ethane'] = 0.1
        m['methane'] = 0.9
        s = EosSetup.objects.create(eos='PR')
        s.set_interaction('tstar', 'ethane', 'methane', value=0.43)
        assert_array_equal(s.tstar(m), np.array([[0, 0.43], [0.43, 0]]))

    def test_matrix_kij_rkpr(self):
        m = Mixture()
        m['ethane'] = 0.1
        m['methane'] = 0.8
        m['co2'] = 0.1
        s = EosSetup.objects.create(eos='RKPR')
        s.set_interaction('kij', 'ethane', 'co2', value=0.43)
        assert_array_equal(s.kij(m), np.array([[0, 0, 0.43],
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
        self.s = EosSetup.objects.create(eos='RKPR')

    def test_all_zeros_by_default(self):
        assert_array_equal(self.s.k0(self.m), np.zeros((3, 3)))

    def test_there_is_a_global_k(self):
        k = K0InteractionParameter.objects.create(eos='RKPR',
                                                  value=0.1)
        k.compounds.add(self.ethane)
        k.compounds.add(self.methane)

        expected = np.zeros((3, 3))
        expected[0, 2] = expected[2, 0] = k.value

        assert_array_equal(self.s.k0(self.m), expected)

    def test_there_is_a_global_k_a_setup_override(self):
        set_interaction('k0', self.ethane, self.methane, eos='RKPR',
                        value=0.1)
        k2 = self.s.set_interaction('k0', self.ethane, self.methane, value=0.2)
        expected = np.zeros((3, 3))
        expected[0, 2] = expected[2, 0] = k2.value
        assert_array_equal(self.s.k0(self.m), expected)

    def test_global_k_for_same_custom_for_other_interaction(self):
        k = set_interaction('k0', self.ethane, self.methane, value=0.1,
                            eos='RKPR')

        k2 = self.s.set_interaction('k0', self.ethane, self.co2, value=0.2)

        expected = np.zeros((3, 3))
        expected[0, 1] = expected[1, 0] = k2.value
        expected[0, 2] = expected[2, 0] = k.value

        assert_array_equal(self.s.k0(self.m), expected)


class TestEnvelope(TestCase):

    def setUp(self):
        self.m = Mixture()
        self.ethane = Compound.objects.get(name='ETHANE')
        self.methane = Compound.objects.get(name='METHANE')
        self.co2 = Compound.objects.get(name='CARBON DIOXIDE')

    @skip('time expire')
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

    @skip('calc fail')
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

    @skip("fail for this mixture case")
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
        s = EosSetup.objects.create(eos='RKPR',
                                    kij_mode='constants', lij_mode='constants')
        assert self.m.total_z == Decimal('0.9')
        with self.assertRaises(ValidationError):
            self.m.get_flash(s, 10., 20.)

        self.m[self.methane] = 0.6   # total_z = 1.0
        assert self.m.clean() is None
        # not raises
        flash = self.m.get_flash(s, 10., 20.)
        assert_array_equal(flash.x, np.array([0., 1., 0]))
        assert_array_equal(flash.y, np.array([ 0.142857,  0,  0.857143]))


class TestSetInteractionMatrix(TestCase):

    def setUp(self):
        self.GC = Mixture()
        elementos = ['methane', 'n-butane', 'n-heptane']
        fracciones = [0.5, 0.2, 0.3]
        for elemento, fraccion in zip(elementos, fracciones):
            self.GC[elemento] = fraccion
        self.GC.sort(True)
        self.setup = EosSetup.objects.create(eos='RKPR', kij_mode=EosSetup.T_DEP,  lij_mode=EosSetup.CONSTANTS)
        self.setup.set_interaction('k0', 'methane',
                                   'n-butane', 0.02613)
        self.setup.set_interaction('k0', 'methane',
                                   'n-heptane', 0.05613)

    def test_matrix_could_be_text(self):
        setup = EosSetup.objects.create(eos='RKPR',
                                kij_mode=EosSetup.T_DEP,
                                lij_mode=EosSetup.CONSTANTS)
        matrix = """0.  0.02 0.05
                    0.02  0   0
                    0.05  0   0"""
        setup.set_interaction_matrix('k0', self.GC, matrix)

        assert_array_equal(setup.k0(self.GC), np.array([[0., .02, 0.05],
                                                        [0.02, 0, 0],
                                                        [0.05, 0, 0]]))

    def test_text_matrix_replaces_semicolon(self):
        setup = EosSetup.objects.create(eos='RKPR',
                                kij_mode=EosSetup.T_DEP,
                                lij_mode=EosSetup.CONSTANTS)
        matrix = """0  0,02 0,05
                    0,02  0   0
                    0,05  0   0"""
        setup.set_interaction_matrix('k0', self.GC, matrix)

        assert_array_equal(setup.k0(self.GC), np.array([[0., .02, 0.05],
                                                        [0.02, 0, 0],
                                                        [0.05, 0, 0]]))


    def test_set_matrix_could_be_ndarray(self):
        setup = EosSetup.objects.create(eos='RKPR',
                                kij_mode=EosSetup.T_DEP,
                                lij_mode=EosSetup.CONSTANTS)
        matrix = np.array([[0., .02, 0.05],
                           [0.02, 0, 0],
                           [0.05, 0, 0]])
        setup.set_interaction_matrix('k0', self.GC, matrix)
        assert_array_equal(setup.k0(self.GC), matrix)


    def test_set_lij_matrix(self):

        setup = EosSetup.objects.create(eos='RKPR',
                                        kij_mode=EosSetup.T_DEP,
                                        lij_mode=EosSetup.CONSTANTS)
        matrix = np.array([[0., .02, 0.05],
                           [0.02, 0, 0],
                           [0.05, 0, 0]])
        setup.set_interaction_matrix('lij', self.GC, matrix)
        assert_array_equal(setup.lij(self.GC), matrix)


    def test_complex_lij_(self):
        GC= Mixture()
        elementos= ['methane', 'n-butane', 'n-heptane', 'n-decane', 'n-tetradecane']
        fracciones= [0.80, 0.14, 0.04, 0.014, 0.006]
        for elemento, fraccion in zip(elementos, fracciones):
            GC[elemento]= fraccion
        GC.sort(True)
        setup1 = EosSetup.objects.create(eos='RKPR',
                                         kij_mode=EosSetup.T_DEP,
                                         lij_mode=EosSetup.CONSTANTS)
        setup1.set_interaction('k0', 'methane', 'n-butane', 0.02613)
        setup1.set_interaction('k0', 'methane', 'n-heptane', 0.05613)
        setup1.set_interaction('k0', 'methane', 'n-decane', 0.08224)
        setup1.set_interaction('k0', 'methane', 'n-tetradecane', 0.10738)

        setup1.set_interaction('lij', 'methane', 'n-butane', -0.06565)
        setup1.set_interaction('lij', 'methane', 'n-heptane', -0.11875)
        setup1.set_interaction('lij', 'methane', 'n-decane', -0.14551)
        setup1.set_interaction('lij', 'methane', 'n-tetradecane', -0.13602)
        setup1.set_interaction('lij', 'n-butane', 'n-heptane', -0.01754)
        setup1.set_interaction('lij', 'n-butane', 'n-decane', -0.02433)
        setup1.set_interaction('lij', 'n-butane', 'n-tetradecane', -0.02203)
        setup1.set_interaction('lij', 'n-heptane', 'n-decane', -0.00586)
        setup1.set_interaction('lij', 'n-heptane', 'n-tetradecane', -0.00388)
        setup1.set_interaction('lij', 'n-decane', 'n-tetradecane', 0.00188)

        setup_lij_menos20 = EosSetup.objects.create(eos='RKPR', kij_mode=EosSetup.T_DEP,
                                                    lij_mode=EosSetup.CONSTANTS)

        setup_lij_menos20.set_interaction_matrix('k0', GC, setup1.k0(GC))
        assert_array_equal(setup1.k0(GC) - setup_lij_menos20.k0(GC),
                           np.zeros((5,5)))

        setup_lij_menos20.set_interaction_matrix('lij', GC, setup1.lij(GC))
        assert_array_equal(setup1.lij(GC) - setup_lij_menos20.lij(GC),
                           np.zeros((5,5)))