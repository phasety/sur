# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from itertools import combinations
from functools import partial

from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.utils import IntegrityError

from picklefield.fields import PickledObjectField
import numpy as np

from envelope import envelope as envelope_routine
from envelope import flash as flash_routine
from . import units
from . import eos


DEFAULT_MAX_LENGTH = 255
MAX_DIGITS = 15
DECIMAL_PLACES = 5


class CompoundManager(models.Manager):

    def find(self, val, exact=False):
        """
        Given an string, looks for compounds matching
        name, formula o aliases.

        If ``exact`` is True, the filter try to match
        the whole val (case insensitive).
        Otherwise, match as `starts with` (case insensitive).
        """
        if isinstance(val, self.model):
            return self.filter(id=val.id)

        criteria = "iexact" if exact else "istartswith"

        lookup = lambda key: dict((("%s__%s" % (key, criteria), val),))

        q_name = Q(**lookup('name'))
        q_formula = Q(**lookup('formula'))
        q_alias = Q(**lookup('aliases__name'))

        return self.filter(q_name | q_formula | q_alias).distinct()


def t_unit():
    return models.CharField(max_length=DEFAULT_MAX_LENGTH,
                            choices=units.Temperature.CHOICES,
                            default=units.Temperature.KELVIN)


def p_unit():
    return models.CharField(max_length=DEFAULT_MAX_LENGTH,
                            choices=units.Pressure.CHOICES,
                            default=units.Pressure.BAR)


def v_unit():
    return models.CharField(max_length=DEFAULT_MAX_LENGTH,
                            choices=units.DensityVolume.CHOICES,
                            default=units.DensityVolume.LITER_MOL)


class Compound(models.Model):
    objects = CompoundManager()

    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    formula = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    formula_extended = models.TextField(null=True, blank=True)
    tc = models.FloatField(verbose_name='Critical Temperature')
    tc_unit = t_unit()
    pc = models.FloatField(verbose_name='Critical Pressure')
    pc_unit = p_unit()
    vc = models.FloatField(verbose_name='Critical Volume')
    vc_unit = v_unit()
    acentric_factor = models.FloatField(null=True, blank=True)
    a = models.FloatField(null=True, blank=True)
    b = models.FloatField(null=True, blank=True)
    c = models.FloatField(null=True, blank=True)
    d = models.FloatField(null=True, blank=True)
    delta1 = models.FloatField(null=True, blank=True)
    weight = models.FloatField(editable=False, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        self._eos_params = {}       # cache
        super(Compound, self).__init__(*args, **kwargs)

    def _get_eos_params(self, model, exclude=[]):
        if isinstance(model, basestring):
            try:
                model = eos.NAMES[model.upper()]
            except KeyError:
                raise ValueError('Unknown %s model' % model)
        if model in exclude:
            raise ValueError("This parameter can't be calculated for %s"
                             % model.MODEL_NAME)

        try:
            # is it already calculated?
            return self._eos_params[model.MODEL_NAME]
        except KeyError:
            if model == eos.RKPR:
                if self.delta1:
                    # delta1 defined. use it
                    params = eos.RKPR.from_constants(self.tc, self.pc,
                                                     self.acentric_factor,
                                                     del1=self.delta1)[1]
                else:
                    # use a default zrat = 1.16
                    Vcrat = 1.16
                    params = eos.RKPR.from_constants(self.tc, self.pc,
                                                     self.acentric_factor,
                                                     vc=self.vc * Vcrat)[1]
            else:
                params = model.from_constants(self.tc, self.pc,
                                              self.acentric_factor)[1]
            self._eos_params[model.MODEL_NAME] = params
            return params

    def get_ac(self, model):
        """Return the critical value for the attractive parameter
           for PR, SRK or RKPR"""
        return self._get_eos_params(model)[0]

    def get_b(self, model):
        """Return the temperature dependence of the attractive parameter
           for PR and the repulsive parameter in SRK and RKPR [l/mol]"""
        return self._get_eos_params(model)[1]

    def get_delta1(self):
        """Return the RK-PR third parameter"""
        return self._get_eos_params('RKPR')[2]

    def get_k(self):
        """Return the parameter for the temperature dependence
           of the attractive parameter for the RKPR eos"""
        return self._get_eos_params('RKPR')[3]

    def get_m(self, model):
        """Parameter for temperature dependence of the
           attractive parameter for PR or SRK"""
        return self._get_eos_params(model, exclude=[eos.RKPR])[3]

    def __unicode__(self):
        return self.name

    def create_alias(self, alias, permanent=True):
        """
        Create an alias for this compound. if ``permanent`` is True
        it's is written to disk to persist over sessions
        """
        a = Alias(compound=self, name=alias)
        a.save()
        if permanent:
            a.save(using='disk')

    def calculate_weight(self):
        """
        An aproximation to determine if a compound is heavier than
        other
        """
        try:
            return self.tc ** 14 / self.pc
        except ZeroDivisionError:
            return 0.0

    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    class Meta:
        ordering = ('mixturefraction__position', 'weight')


class Alias(models.Model):
    """
    Some shortchuts to find Compounds.
    Example: 'c5' -> Pentane
    """
    compound = models.ForeignKey('Compound', related_name="aliases")
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                            unique=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.compound.name)


class InteractionManager(models.Manager):

    def find(self, model, compound1, compound2=None, mixture=None):
        """
        filter interactions for EOS and compounds
        globally defined on specific for a mixture.
        """
        if isinstance(model, basestring):
            try:
                model = eos.NAMES[model.upper()]
            except KeyError:
                raise ValueError('Unknown %s model' % model)

        comps = Compound.objects.find(compound1)
        qs = self.filter(eos=model.MODEL_NAME, compounds__in=comps)
        if compound2:
            comps = Compound.objects.find(compound2)
            qs = qs.filter(compounds__in=comps)

        # only global or mixture
        mix_q = Q(mixture__isnull=True)
        if mixture:
            mix_q |= Q(mixture=mixture)
        qs = qs.filter(mix_q)
        return qs


class AbstractInteractionParameter(models.Model):
    class Meta:
        abstract = True
        ordering = ['-mixture']

    objects = InteractionManager()

    compounds = models.ManyToManyField('Compound')
    eos = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                           choices=eos.CHOICES)
    value = models.FloatField()
    mixture = models.ForeignKey('Mixture', null=True)


@receiver(m2m_changed)
def verify_parameter_uniquesness(sender, **kwargs):
    parameter = kwargs.get('instance', None)
    if not isinstance(parameter, AbstractInteractionParameter):
        return
    cls = type(parameter)
    compounds_set = kwargs.get('pk_set', None)
    action = kwargs.get('action', None)
    if action == 'pre_add':
        if parameter.compounds.count() == 2:
            raise IntegrityError('This interaction parameter has its compounds '
                                 'already defined')
        qs = cls.objects.filter(compounds__in=parameter.compounds.all()).\
            filter(compounds__id__in=compounds_set)
        if parameter.mixture:
            qs = qs.filter(mixture=parameter.mixture)
        else:
            qs = qs.filter(mixture__isnull=True)
        if qs.exists():
            raise IntegrityError('Already exists a parameter matching these condition')


class KijInteractionParameter(AbstractInteractionParameter):
    """Constanst for Kij in mode Kij constant"""
    pass


class K0InteractionParameter(AbstractInteractionParameter):
    """Ko constanst for Kij as f(T) = K0*e^(-T/T*)"""
    pass


class TstarInteractionParameter(AbstractInteractionParameter):
    """T* constanst for Kij as f(T) = K0*e^(-T/T*)"""
    pass


class LijInteractionParameter(AbstractInteractionParameter):
    """Lij constanst"""
    pass


class MixtureFraction(models.Model):
    mixture = models.ForeignKey('Mixture', related_name='fractions')
    compound = models.ForeignKey('Compound')
    fraction = models.DecimalField(decimal_places=4,
                                   max_digits=MAX_DIGITS,
                                   validators=[MinValueValidator(0.),
                                               MaxValueValidator(1.)])
    position = models.PositiveIntegerField(editable=False)

    def save(self, *args, **kwargs):
        if self.position is None:
            self.position = MixtureFraction.objects.all().count()
        self.full_clean()

        super(MixtureFraction, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("mixture", "compound")
        ordering = ('position',)


class Mixture(models.Model):
    # use self.compounds
    Compounds = models.ManyToManyField(Compound, through='MixtureFraction')

    @property
    def compounds(self):
        return self.Compounds.all()

    @property
    def z(self):
        """
        the :abbr:`Z (Composition array)` as a :class:`numpy.array` instance
        in the same order than ``self.compounds``
        """
        return np.array([float(f.fraction) for f in self.fractions.all()])

    @property
    def total_z(self):
        """
        Return the summatory of z fractions.
        Should sum 1.0 to be a valid mixture
        """
        return self.fractions.aggregate(total=models.Sum('fraction'))['total'] or 0

    def __len__(self):
        return self.fractions.count()

    def __repr__(self):
        return repr(list(self))

    def __item_preprocess(self, key):
        if not isinstance(key, (Compound, basestring)):
            raise TypeError('%s has a non valid key type' % key)

        if isinstance(key, basestring):
            try:
                key = Compound.objects.find(key, exact=True).get()
            except Compound.DoesNotExist:
                raise KeyError('%s is an unknown compound' % key)
        return key

    def __getitem__(self, key):
        key = self.__item_preprocess(key)
        try:
            return self.fractions.get(compound=key).fraction
        except MixtureFraction.DoesNotExist:
            raise KeyError('%s is not part of this mixture' % key)

    def __setitem__(self, key, value):
        key = self.__item_preprocess(key)
        try:
            self.add(key, value)
        except ValidationError:
            # already exists
            mf = self.fractions.get(compound=key)
            mf.fraction = value
            mf.save()

    def __delitem__(self, key):
        key = self.__item_preprocess(key)
        try:
            self.fractions.get(compound=key).delete()
            self.sort(False)
        except MixtureFraction.DoesNotExist:
            raise KeyError('%s is not part of this mixture' % key)

    def __iter__(self):
        """
        return an iterator of (compound, z_fraction) tuples
        """
        return ((mf.compound, mf.fraction) for mf in self.fractions.all())

    def as_json(self):

        return json.dumps([(mf.compound.name, str(mf.fraction))
                           for mf in self.fractions.all()])

    def _compounds_array_field(self, field_or_meth, as_array=True,
                               call_args=()):
        """helper to construct an array-like from compound's properties"""
        values = [getattr(v, field_or_meth) for v in self.compounds]
        if callable(values[0]):
            values = [v(*call_args) for v in values]
        if as_array:
            values = np.array(values)
        return values

    @property
    def tc(self):
        """
        return the :abbr:`Tc (Critical temperature)` array.

        It is the :abbr:`Tc` of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds``
        """
        return self._compounds_array_field('tc')

    @property
    def pc(self):
        """
        return the :abbr:`Pc (Critical pressure)` array.

        It is the :abbr:`Pc` of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds``
        """
        return self._compounds_array_field('pc')

    @property
    def vc(self):
        """
        return the :abbr:`Vc (Critical volume)` array.

        It is the :abbr:`Vc` of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds``
        """
        return self._compounds_array_field('vc')

    @property
    def acentric_factor(self):
        """
        return the :abbr:`$\omega$ (acentric_factor)` array.

        It is the :abbr:`$\omega$ of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds``
        """
        return self._compounds_array_field('acentric_factor')

    def _get_interaction_matrix(self, eos_model, model_class):
        """
        return the 2d square matrix of the Model interaction parameters
        """
        compounds = self.compounds
        n = compounds.count()
        m = np.zeros((n, n))
        for ((x, c1), (y, c2)) in combinations(enumerate(compounds), 2):
            try:
                k = model_class.objects.find(eos_model, c1, c2, self)[0].value
                m[x, y] = k
            except:
                pass

        # 0 1 2    0 0 0
        # 0 0 0 +  1 0 0
        # 0 0 0    2 0 0

        diagonal_mirrored = np.rot90(np.flipud(m), -1)
        return m + diagonal_mirrored

    # interaction matrices
    def k0(self, eos):
        return self._get_interaction_matrix(eos, K0InteractionParameter)

    def tstar(self, eos):
        return self._get_interaction_matrix(eos, TstarInteractionParameter)

    def kij(self, eos):
        return self._get_interaction_matrix(eos, KijInteractionParameter)

    def lij(self, eos):
        return self._get_interaction_matrix(eos, LijInteractionParameter)

    def sort(self, by_weight=True):
        """Sort the mixture by compound's weight or
           by position
        """
        qs = self.fractions.all()
        if by_weight:
            qs = qs.order_by('compound__weight')
        for pos, f in enumerate(qs):
            f.position = pos
            f.save()

    # model params vectors
    def get_ac(self, model):
        """Return the critical value for the attractive parameter
           array for PR, SRK or RKPR"""
        return self._compounds_array_field('get_ac', call_args=(model,))

    def get_b(self, model):
        """Return the temperature dependence of the attractive parameter
           array for PR and the repulsive parameter in SRK and RKPR [l/mol]"""
        return self._compounds_array_field('get_b', call_args=(model,))

    def get_delta1(self):
        """Return the RK-PR third parameter array"""
        return self._compounds_array_field('get_delta1')

    def get_k(self):
        """Return the parameter for the temperature dependence
           of the attractive parameter array for the RKPR eos"""
        return self._compounds_array_field('get_k')

    def get_m(self, model):
        """Parameter for temperature dependence of the
           attractive parameter for PR or SRK"""
        return self._compounds_array_field('get_m', call_args=(model,))

    def reset(self):
        """delete all MixtureFractions"""
        self.fractions.all().delete()

    def add_many(self, compounds, fractions):
        """shortcut to add many compounds to the mixture at once.

            compounds and fractions could be iterables or strings.
        """
        if isinstance(compounds, basestring):
            compounds = compounds.split()

        if isinstance(fractions, basestring):
            fractions = fractions.replace(',', '.').split()

        if len(fractions) != len(compounds):
            raise ValueError('compounds and fractions must have the same size')

        for compound, fraction in zip(compounds, fractions):
            self.add(compound, fraction)

    def add(self, compound, fraction=None):
        """
        Add compound fraction to the mixture.

        Compound could be a :class:`Compound` instance or
        a string passed to :meth:`Compound.objects.find`


        if fraction is None, it is set to the complement to reach
        ``self.total_z == Decimal('1.0')``
        """

        if not self.id:
            self.save()
        if isinstance(compound, basestring):
            compound = Compound.objects.find(compound, exact=True).get()

        # already exists?
        mf = MixtureFraction.objects.filter(mixture=self,
                                            compound=compound)
        actual_fraction = mf.get().fraction if mf.exists() else 0

        if fraction:
            future_total = Decimal(str(fraction)) + self.total_z - actual_fraction
            if future_total > Decimal('1.0'):
                raise ValueError('Add this fraction would exceed 1.0. Max fraction '
                                 'allowed is %s' % (Decimal('1.0') - self.total_z))
        else:
            fraction = Decimal('1.0') - self.total_z + actual_fraction

        MixtureFraction.objects.create(mixture=self,
                                       compound=compound,
                                       fraction=str(fraction))

    def clean(self):

        if self.total_z != Decimal('1.0'):
            raise ValidationError('The mixture fractions should sum 1.0')

    def get_envelope(self, eos='RKPR', kij='t_dep', lij='constants'):
        """Get the envelope object for this mixture, calculated using
        the `eos` (RKPR, SRK or PR) and the selected interaction parameters
        mode.

        kij: ``'t_dep'`` or ``'constants'``
        lij: ``'zero'`, `0` or ``'constants'``
        """
        lij = 'zero' if lij in (0, '0') else lij
        try:
            mode = {('t_dep', 'zero'): Kij_constant_Lij_0,
                    ('constants', 'constants'): Kij_constant_Lij_constant,
                    ('t_dep', 'constants'): Kij_t_Lij_constant,
                    ('t_dep', 'zero'): Kij_t_Lij_0}[(kij, lij)]
        except KeyError:
            raise ValueError('Not valid kij and/or lij')
        return EosEnvelope.objects.get_or_create(mixture=self,
                                                 eos=eos,
                                                 mode=mode)[0]

    def get_flash(self, t, p, eos='RKPR', kij='t_dep', lij='constants'):
        """
        Get the flash on (t, p) for this mixture, calculated using
        the `eos` (RKPR, SRK or PR) and the selected interaction parameters
        mode.

        kij: ``'t_dep'`` or ``'constants'``
        lij: ``'zero'`, `0` or ``'constants'``
        """
        lij = 'zero' if lij in (0, '0') else lij
        try:
            mode = {('t_dep', 'zero'): Kij_constant_Lij_0,
                    ('constants', 'constants'): Kij_constant_Lij_constant,
                    ('t_dep', 'constants'): Kij_t_Lij_constant,
                    ('t_dep', 'zero'): Kij_t_Lij_0}[(kij, lij)]
        except KeyError:
            raise ValueError('Not valid kij and/or lij')
        return Flash.objects.get_or_create(t=t,
                                           p=p,
                                           input_mixture=self,
                                           eos=eos,
                                           mode=mode)[0]


Kij_constant_Lij_0 = 'Kij_constant_Lij_0'
Kij_constant_Lij_constant = 'Kij_constant_Lij_constant'
Kij_t_Lij_constant = 'Kij_t_Lij_constant'
Kij_t_Lij_0 = 'Kij_t_Lij_0'

INTERACTION_MODE_CHOICES = ((Kij_constant_Lij_0, 'Kij constant value and Lij=0'),
                            (Kij_constant_Lij_constant, 'Kij and Lij constant'),
                            (Kij_t_Lij_constant, 'Kij (T) and Lij constant'),
                            (Kij_t_Lij_0, 'Kij (T) and Lij=0'))


class Envelope(models.Model):
    """
    A base object for envelopes.
    """
    class Meta:
        abstract = True

    mixture = models.ForeignKey('Mixture', related_name='%(class)s')
    p = PickledObjectField(editable=False,
                           help_text=u'Presure array of the envelope P-T')
    t = PickledObjectField(editable=False,
                           help_text=u'Temperature array of the envelope P-T')
    rho = PickledObjectField(editable=False,
                             help_text=u'Density array of the envelope P-T')

    p_cri = PickledObjectField(editable=False,
                               help_text=u'Presure coordenates of critical points')
    t_cri = PickledObjectField(editable=False,
                               help_text=u'Temperature coordenates of critical points')
    rho_cri = PickledObjectField(editable=False,
                                 help_text=u'Density coordenates of critical points')


class ExperimentalEnvelope(Envelope):
    pass


class EosEnvelope(Envelope):
    eos = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                           choices=eos.CHOICES,
                           default=eos.RKPR.MODEL_NAME)
    mode = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                            choices=INTERACTION_MODE_CHOICES,
                            default=Kij_t_Lij_constant)

    class Meta:
        unique_together = (('mixture', 'eos', 'mode'),)

    def _calc(self):
        """
        calculate the envelope based on the given parameters
        ``mixture``, ``eos``, ``mode``.

        """
        m = self.mixture  # just in sake of brevity
        m.clean()
        envelope = partial(envelope_routine, eos.NAMES[self.eos], m.z, m.tc,
                           m.pc, m.acentric_factor,
                           m.get_ac(self.eos), m.get_b(self.eos))

        if self.eos == eos.RKPR.MODEL_NAME:
            envelope = partial(envelope, k=m.get_k(), delta1=m.get_delta1())
        else:
            envelope = partial(envelope, m=m.get_m(self.eos))

        if self.mode == Kij_constant_Lij_0:
            env_result = envelope(kij=m.kij(self.eos))
        elif self.mode == Kij_constant_Lij_constant:
            env_result = envelope(kij=m.kij(self.eos), lij=m.lij(self.eos))
        elif self.mode == Kij_t_Lij_0:
            env_result = envelope(k0=m.k0(self.eos), tstar=m.tstar(self.eos))
        elif self.mode == Kij_t_Lij_constant:
            env_result = envelope(k0=m.k0(self.eos), tstar=m.tstar(self.eos),
                                  lij=m.lij(self.eos))

        self.p, self.t, self.rho = env_result[0]
        self.p_cri, self.t_cri, self.rho_cri = env_result[1]

    def save(self, *args, **kwargs):
        if not self.id:
            # calculate everything the first time
            self._calc()
        super(Envelope, self).save(*args, **kwargs)


class Flash(models.Model):
    input_mixture = models.ForeignKey('Mixture', related_name='flashes')
    t = models.FloatField(verbose_name='Temperature of the flash')
    p = models.FloatField(verbose_name='Pressure of the flash')

    eos = models.CharField(max_length=DEFAULT_MAX_LENGTH, choices=eos.CHOICES)
    mode = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                            choices=INTERACTION_MODE_CHOICES)
    vapour_mixture = models.ForeignKey('Mixture', editable=False,
                                       related_name='flashes_as_gas')
    liquid_mixture = models.ForeignKey('Mixture', editable=False,
                                       related_name='flashes_as_liquid')
    rho_l = models.FloatField(verbose_name='Density of liquid')
    rho_v = models.FloatField(verbose_name='Density of vapour')
    beta = models.FloatField(verbose_name='Vapour fraction',
                             validators=[MinValueValidator(0.),
                                         MaxValueValidator(1.)])

    class Meta:
        unique_together = (('t', 'p', 'input_mixture', 'eos', 'mode'),)

    def clean(self):
        z_calculated = self.y * self.beta + self.x * (1 - self.beta)
        if not np.allclose(self.input_mixture.z, z_calculated):
            raise ValidationError('Not all Zi != Yi*beta + Xi*(1 - beta)')

    def _calc(self):
        """
        Calculate the flash for the given t and p
        """
        m = self.input_mixture  # just in sake of brevity
        m.clean()
        flash = partial(flash_routine, self.t, self.p, eos.NAMES[self.eos], m.z, m.tc,
                        m.pc, m.acentric_factor, m.get_ac(self.eos), m.get_b(self.eos))

        if self.eos == eos.RKPR.MODEL_NAME:
            flash = partial(flash, k=m.get_k(), delta1=m.get_delta1())
        else:
            flash = partial(flash, m=m.get_m(self.eos))

        if self.mode == Kij_constant_Lij_0:
            flash_result = flash(kij=m.kij(self.eos))
        elif self.mode == Kij_constant_Lij_constant:
            flash_result = flash(kij=m.kij(self.eos), lij=m.lij(self.eos))
        elif self.mode == Kij_t_Lij_0:
            flash_result = flash(k0=m.k0(self.eos), tstar=m.tstar(self.eos))
        elif self.mode == Kij_t_Lij_constant:
            flash_result = flash(k0=m.k0(self.eos), tstar=m.tstar(self.eos),
                                 lij=m.lij(self.eos))

        self.x, self.y, self.rho_l, self.rho_v, self.beta = flash_result

    def save(self, *args, **kwargs):
        if not self.id:
            # calculate the first time
            self._calc()
        super(Flash, self).save(*args, **kwargs)

    @property
    def x(self):
        return self.liquid_mixture.z

    @x.setter
    def x(self, liquid_mixture_composition):
        size = self.input_mixture.compounds.count()
        if len(liquid_mixture_composition) != size:
            raise ValueError('X must be same size than input_mixture (%d)' % size)

        try:
            self.liquid_mixture.delete()
        except Mixture.DoesNotExist:
            pass
        m = Mixture()
        m.add_many(self.input_mixture.compounds, liquid_mixture_composition)
        self.liquid_mixture = m

    @property
    def y(self):
        return self.vapour_mixture.z

    @y.setter
    def y(self, vapour_mixture_composition):
        size = self.input_mixture.compounds.count()
        if len(vapour_mixture_composition) != size:
            raise ValueError('Y must be same size than input_mixture (%d)' % size)

        try:
            self.vapour_mixture.delete()
        except Mixture.DoesNotExist:
            pass

        m = Mixture()
        m.add_many(self.input_mixture.compounds,
                   vapour_mixture_composition)
        self.vapour_mixture = m
