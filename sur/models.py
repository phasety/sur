# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from itertools import combinations
# from functools import partial
from StringIO import StringIO
from django.db import models
from django.db.models import Q
# from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict
from picklefield.fields import PickledObjectField
import numpy as np
from matplotlib import pyplot as plt

from envelope_sp import (envelope as envelope_routine, flash as flash_routine,
                         write_input)
from eos import get_eos
from . import units
from . import eos


DEFAULT_MAX_LENGTH = 255
MAX_DIGITS = 15
DECIMAL_PLACES = 6


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

        return self.filter(tc__gt=0, pc__gt=0).\
            filter(q_name | q_formula | q_alias).distinct()


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
    vc = models.FloatField(verbose_name='Critical Volume', null=True, blank=True)
    vc_unit = v_unit()
    acentric_factor = models.FloatField(null=True, blank=True)
    a = models.FloatField(null=True, blank=True)
    b = models.FloatField(null=True, blank=True)
    c = models.FloatField(null=True, blank=True)
    d = models.FloatField(null=True, blank=True)
    delta1 = models.FloatField(null=True, blank=True)
    weight = models.FloatField(editable=False, null=True, blank=True)

    @staticmethod
    def from_str(key):
        if isinstance(key, basestring):
            try:
                key = Compound.objects.find(key, exact=True).get()
            except Compound.DoesNotExist:
                raise KeyError('%s is an unknown compound' % key)
        return key

    def __init__(self, *args, **kwargs):
        self._eos_params = {}       # cache
        super(Compound, self).__init__(*args, **kwargs)

    def _get_eos_params(self, model, exclude=[], update_vc=False):
        model = get_eos(model)
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
                    constants, params = eos.RKPR.from_constants(self.tc, self.pc,
                                                                self.acentric_factor,
                                                                del1=self.delta1)
                else:
                    # use a default zrat = 1.16
                    Vcrat = 1.16
                    constants, params = eos.RKPR.from_constants(self.tc, self.pc,
                                                                self.acentric_factor,
                                                                vc=self.vc * Vcrat)
            else:
                constants, params = model.from_constants(self.tc, self.pc,
                                                         self.acentric_factor)

            if update_vc:
                vc = constants[-1]
                self.vc = vc
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

    def create_alias(self, alias):
        """
        Create an alias for this compound.
        """
        a = Alias(compound=self, name=alias)
        a.save()

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


class EosSetup(models.Model):
    T_DEP = 't_dep'
    CONSTANTS = 'constants'
    ZERO = 'zero'

    KIJ_MODE_CHOICES = ((T_DEP, 'Kij is temperature dependent'),
                        (CONSTANTS, 'kij is a constant for each binary interaction'))
    LIJ_MODE_CHOICES = ((ZERO, 'Lij is zero for each binary interaction'),
                        (CONSTANTS, 'Lij is a constant of each binary interaction'))

    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, null=True, blank=True,
                            help_text=u"A short indentification for this "
                                      u"EOS configuration")

    eos = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                           choices=eos.CHOICES,
                           default='RKPR')
    user = models.ForeignKey(User, null=True, editable=False)
    kij_mode = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                                choices=KIJ_MODE_CHOICES,
                                default='constants')
    lij_mode = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                                choices=LIJ_MODE_CHOICES,
                                default='zero')

    def __unicode__(self):
        d = {'eos': self.eos, 'kij_mode': self.kij_mode, 'lij_mode': self.lij_mode}
        mode = u"%(eos)s - kij %(kij_mode)s - lij %(lij_mode)s" % d
        if self.name:
            return u"%s %s" % (self.name, mode)
        return mode

    def set_interaction(self, kind, compound1, compound2, value):
        """create or update an interaction parameter"""
        return set_interaction(kind, compound1, compound2, value,
                               setup=self, user=self.user)

    def set_interaction_matrix(self, kind, mixture, matrix):
        """set a matrix as the one returned by
        setup.kij(mixture) or analogs methods.

        kind -- 'lij', 'k0', 'tstar', 'kij'
        mixture -- the Mixture
        matrix -- could be a string (multiline) or a N x N array
        """
        if not isinstance(matrix, np.ndarray):
            matrix = np.loadtxt(StringIO(matrix.replace(',', '.')))
        size = len(mixture)
        if matrix.shape != (size, size):
            raise ValueError('matrix must be same size than mixture')
        for ((x, c1), (y, c2)) in combinations(enumerate(mixture.compounds), 2):
            try:
                self.set_interaction(kind, c1, c2, matrix[x, y])
            except:
                pass

    def _get_interaction_matrix(self, model_class, mixture, **kwargs):
        """
        return the 2d square matrix of the Model interaction parameters
        for a mixture
        """
        compounds = mixture.compounds
        n = len(mixture)
        m = np.zeros((n, n))
        for ((x, c1), (y, c2)) in combinations(enumerate(compounds), 2):
            try:
                k = model_class.objects.find(c1, c2, setup=self)[0].value
                m[x, y] = k
            except:
                if model_class == TstarInteractionParameter:
                    m[x, y] = min((c1, c2)).tc

        # 0 1 2    0 0 0
        # 0 0 0 +  1 0 0
        # 0 0 0    2 0 0

        diagonal_mirrored = np.rot90(np.flipud(m), -1)
        return m + diagonal_mirrored

    # interaction matrices
    def k0(self, mixture):
        return self._get_interaction_matrix(K0InteractionParameter, mixture)

    def tstar(self, mixture):
        return self._get_interaction_matrix(TstarInteractionParameter, mixture)

    def kij(self, mixture):
        return self._get_interaction_matrix(KijInteractionParameter, mixture)

    def lij(self, mixture):
        return self._get_interaction_matrix(LijInteractionParameter, mixture)

    def get_interactions(self, mixture):
        """returns a sorted dict with the interactions matrix for a given
        mode and mixture"""

        interactions = SortedDict([])

        if self.kij_mode == EosSetup.CONSTANTS:
            interactions['kij'] = self.kij(mixture)
        else:
            interactions['k0'] = self.k0(mixture)
            interactions['tstar'] = self.tstar(mixture)

        if self.lij_mode == EosSetup.CONSTANTS:
            interactions['lij'] = self.lij(mixture)
        else:
            n = len(mixture)
            interactions['lij'] = np.zeros((n, n))
        return interactions


class InteractionManager(models.Manager):

    def find(self, compound1, compound2=None, setup=None, eos=None, user=None):
        """
        filter interactions for EOS and compounds
         defined globally, for an user or for specific mixture.
        """
        if setup:
            eos = setup.eos
        elif eos:
            eos = get_eos(eos).MODEL_NAME
        else:
            raise ValidationError('Setup or eos must be given')

        comps = Compound.objects.find(compound1)
        qs = self.filter(eos=eos, compounds__in=comps)
        if compound2:
            comps = Compound.objects.find(compound2)
            qs = qs.filter(compounds__in=comps)
        # only global or mixture
        user_q = Q(user__isnull=True)
        if user:
            user_q |= Q(user=user)
        elif setup and setup.user:
            user_q |= Q(user=setup.user)

        qs = qs.filter(user_q)

        setup_q = Q(setup__isnull=True)
        if setup:
            setup_q |= Q(setup=setup)
        qs = qs.filter(setup_q)
        return qs


class AbstractInteractionParameter(models.Model):
    class Meta:
        abstract = True
        ordering = ['-setup', '-user']

    objects = InteractionManager()

    compounds = models.ManyToManyField('Compound')
    eos = models.CharField(max_length=DEFAULT_MAX_LENGTH,
                           choices=eos.CHOICES)
    value = models.FloatField()
    setup = models.ForeignKey('EosSetup', null=True)
    user = models.ForeignKey(User, null=True)

    def clean(self):
        if self.setup and self.setup.eos != self.eos:
            raise ValidationError("The EOS for the interaction doesn't "
                                  "match with the EosSetup's one")

        if self.setup and self.setup.eos != self.eos:
            raise ValidationError("The user for the interaction doesn't "
                                  "match with the EosSetup's one")

    def save(self, *args, **kwargs):
        if self.setup and not self.eos:
            self.eos = self.setup.eos
        if self.setup and self.setup.user and not self.user:
            self.user = self.setup.user
        self.clean()
        super(AbstractInteractionParameter, self).save(*args, **kwargs)


@receiver(m2m_changed)
def verify_parameter_uniquesness(sender, **kwargs):
    parameter = kwargs.get('instance', None)
    if not isinstance(parameter, AbstractInteractionParameter):
        return
    cls = type(parameter)
    compounds_set = kwargs.get('pk_set', None)
    action = kwargs.get('action', None)
    if action == 'pre_add':
        if parameter.compounds.all().distinct().count() == 2:
            raise IntegrityError('This interaction parameter has its compounds '
                                 'already defined')
        qs = cls.objects.filter(compounds__in=parameter.compounds.all()).\
            filter(compounds__id__in=compounds_set, eos=parameter.eos)

        if parameter.setup:
            qs = qs.filter(setup=parameter.setup)
        else:
            qs = qs.filter(setup__isnull=True)

        if parameter.user:
            qs = qs.filter(user=parameter.user)
        else:
            qs = qs.filter(user__isnull=True)

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


def set_interaction(kind, compound1, compound2, value,
                    setup=None, eos=None, user=None):
    """create or update an interaction parameter"""

    if setup:
        eos = setup.eos
    elif eos:
        eos = get_eos(eos).MODEL_NAME
    else:
        raise ValidationError('Setup or eos must be given')

    KModel = {'kij': KijInteractionParameter,
              'k0': K0InteractionParameter,
              'tstar': TstarInteractionParameter,
              'lij': LijInteractionParameter}[kind.lower()]

    compound1 = Compound.from_str(compound1)
    compound2 = Compound.from_str(compound2)

    base = KModel.objects.filter(eos=eos).\
        filter(compounds=compound1).filter(compounds=compound2)
    if setup:
        base = base.filter(setup=setup)
    else:
        base = base.filter(setup__isnull=True)

    if user:
        base = base.filter(user=user)
    else:
        base = base.filter(user__isnull=True)

    if base.exists():
        interaction = base.get()
        interaction.value = value
        interaction.save(update_fields=('value',))
    else:
        interaction = KModel.objects.create(eos=eos, setup=setup,
                                            user=user, value=value)
        interaction.compounds.add(compound1)
        interaction.compounds.add(compound2)
    return interaction


class MixtureFraction(models.Model):
    mixture = models.ForeignKey('Mixture', related_name='fractions')
    compound = models.ForeignKey('Compound')
    fraction = models.DecimalField(decimal_places=DECIMAL_PLACES,
                                   max_digits=MAX_DIGITS)
                                   # validators=[MinValueValidator(0.),
                                   #            MaxValueValidator(1.)])
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
    user = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, null=True,
                            help_text=u"A short indentification for this fluid/case")

    def __unicode__(self):
        return self.name

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
        return Compound.from_str(key)

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
                # TO DO test it
                if future_total - Decimal('1.0') < Decimal('0.01'):
                    fraction = None
                else:
                    raise ValueError('Add this fraction would exceed 1.0. Max fraction '
                                     'allowed is %s' % (Decimal('1.0') - self.total_z))

        if fraction is None:
            fraction = Decimal('1.0') - self.total_z + actual_fraction

        MixtureFraction.objects.create(mixture=self,
                                       compound=compound,
                                       fraction=str(fraction))

    def clean(self):
        if abs(self.total_z - Decimal('1.0')) > Decimal('.0001'):
            raise ValidationError('The mixture fractions should sum 1.0')

    def get_envelope(self, setup, label=None):
        """Get the envelope object for this mixture, calculated using
        the setup EOS with its selected interaction parameters
        mode.
        """
        return EosEnvelope.objects.get_or_create(mixture=self,
                                                 setup=setup,
                                                 label=label)[0]

    def experimental_envelope(self, t, p,
                              rho=None, t_cri=None, p_cri=None, rho_cri=None,
                              label=None):
        """Create an associated :class:`ExperimentalEnvelope`
           associated to this mixture

        :type t, p, rho: str or sequences of float

        """
        def sanitize(var):
            if isinstance(var, basestring):
                var = var.replace(',', '.').split()
            if var is not None:
                var = np.array(var)
            return var
        arguments = t, p, rho, t_cri, p_cri, rho_cri
        t, p, rho, t_cri, p_cri, rho_cri = map(sanitize, arguments)
        return ExperimentalEnvelope.objects.create(mixture=self,
                                                   t=t, p=p, rho=rho,
                                                   p_cri=p_cri,
                                                   t_cri=t_cri,
                                                   rho_cri=rho_cri,
                                                   label=label)

    def get_flash(self, setup, t, p=None, v=None):
        """
        Get the flash on (t, p) or (t,v) for this mixture, calculated using
        the setup EOS with its selected interaction parameters
        mode.
        """
        return EosFlash.objects.get_or_create(t=t,
                                              p=p,
                                              v=v,
                                              mixture=self,
                                              setup=setup)[0]


class Envelope(models.Model):
    """
    A base object for envelopes.
    """
    class Meta:
        abstract = True

    mixture = models.ForeignKey('Mixture', related_name='%(class)ss')
    p = PickledObjectField(editable=False,
                           help_text=u'Presure array of the envelope P-T')
    t = PickledObjectField(editable=False,
                           help_text=u'Temperature array of the envelope P-T')
    rho = PickledObjectField(editable=False, null=True,
                             help_text=u'Density array of the envelope P-T')

    p_cri = PickledObjectField(editable=False,
                               null=True,
                               help_text=u'Presure coordenates of critical points')
    t_cri = PickledObjectField(editable=False,
                               null=True,
                               help_text=u'Temperature coordenates of critical points')
    rho_cri = PickledObjectField(editable=False,
                                 null=True,
                                 help_text=u'Density coordenates of critical points')
    index_cri = PickledObjectField(editable=False,
                                   null=True)
    label = models.CharField(max_length=100, null=True, blank=True,
                             default='__nolengend__')

    def plot(self, fig=None, critical_point='o', format=None, legends=None):
        """
        Plot the envelope in a T vs P figure.

        :param figure: If it'ss given, the envelope will be plotted
                       in its last axes. Otherwise a new figure will be created.
                       This is useful to chain multiples plots in the same figure.
        :type figure: :class:`Figure` instance or None
        :param format: if given, the whole envelope will use this format
                       if it's None, each segment of the envelope
                       will be ploted in a different color.
        :type format: str or None
        :param critical_point: Define the marker for the critical point. If it's
                               None, the point won't be plotted.
        :type critical_point: str or None
        :lengends: show legends.
                   See http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.legend

        :returns: a :class:`Figure` instance

        """

        if fig is None:
            fig, ax = plt.subplots()
        else:
            ax = fig.get_axes()[-1]

        if format:
            ax.plot(self.t, self.p, format, label=self.label)
        else:
            colors = ('red', 'blue', 'violet', 'black', 'yellow')
            start = 0
            for i, (index, color) in enumerate(zip(self.index_cri, colors)):
                p = self.p[start:index]
                t = self.t[start:index]
                ax.plot(t, p, color=color, label=self.label)
                start = index

                # extra segments
                # plot last point of a segment to the critical point
                # and the first of the next to the critical point
                if self.index_cri.size > 1:
                    seg = 0 if i % self.index_cri.size != 0 else -1
                    ax.plot([t[seg], self.t_cri[i / 2]],
                            [p[seg], self.p_cri[i / 2]], color=color)

        if critical_point and self.index_cri.size > 1:
            ax.scatter(self.t_cri, self.p_cri, marker=critical_point)

        ax.grid(True)
        ax.set_xlabel("Temperature [K]")
        ax.set_ylabel("Pressure [bar]")
        if legends:
            ax.legend(loc=legends)
        fig.frameon = False
        return fig

    def as_json(self):
        cols = [map(str, c) for c in zip(self.p, self.t)]   # self.rho)]
        return json.dumps(cols)

    def cri_as_json(self):
        cols = [map(str, c) for c in zip(self.p_cri, self.t_cri)]   # self.rho_cri)]
        return json.dumps(cols)


class ExperimentalEnvelope(Envelope):

    def plot(self, fig=None, critical_point=None, marker='s', color='k'):
        """
        Plot the envelope in a T vs P as a scatter figure

        :param figure: If it'ss given, the envelope will be plotted
                       in its last axes. Otherwise a new figure will be created.
                       This is useful to chain multiples plots in the same figure.
        :type figure: :class:`Figure` instance or None
        :param critical_point: Define the marker for the critical point. If it's
                               None, the point won't be plotted.
        :type critical_point: str or None
        :param marker: Define the marker for each experimental point in the envelope.
                       A square by default
        :type marker: str or None
        :param color: define the color of the points
        :type color: color str
        :returns: a :class:`Figure` instance
        """

        if fig is None:
            fig, ax = plt.subplots()
        else:
            ax = fig.get_axes()[-1]

        ax.scatter(self.t, self.p, c=color, marker=marker, label=self.label)
        if critical_point and self.index_cri.size > 1:
            ax.scatter(self.t_cri, self.p_cri, marker=critical_point)

        ax.grid()
        ax.set_xlabel("Temperature [K]")
        ax.set_ylabel("Pressure [bar]")
        fig.frameon = False
        return fig


class EosEnvelope(Envelope):
    setup = models.ForeignKey('EosSetup')

    input_txt = models.TextField(editable=False, null=True)
    output_txt = models.TextField(editable=False, null=True)

    # class Meta:
    #    unique_together = (('mixture', 'eos', 'mode'),)

    def __repr__(self):
        return '<%(class)s: %(setup)s>' % {'class': self.__class__.__name__,
                                           'setup': self.setup}

    def get_txt(self):
        return write_input(self.mixture, self.eos, as_data=True)

    def _calc(self):
        """
        calculate the envelope based on the given parameters
        ``mixture``, ``eos``, ``mode``.

        """
        m = self.mixture  # just in sake of brevity
        m.clean()
        """
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
        """
        env_result = envelope_routine(self)
        self.t, self.p, self.rho = env_result[0]
        self.t_cri, self.p_cri, self.rho_cri, self.index_cri = env_result[1]
        if self.index_cri is not None:
            self.index_cri = self.index_cri.astype(int)
        else:
            self.index_cri = np.array([], dtype=int)
        self.index_cri = np.append(self.index_cri, self.p.size)

    def save(self, *args, **kwargs):
        if not self.id:
            self._calc()

        super(Envelope, self).save(*args, **kwargs)

    @property
    def interactions(self):
        return self.setup.get_interactions(self.mixture)


class Flash(models.Model):

    class Meta:
        abstract = True

    mixture = models.ForeignKey('Mixture', related_name='%(class)ses')
    t = models.FloatField(verbose_name='Temperature of the flash')
    p = models.FloatField(verbose_name='Pressure of the flash', null=True)
    v = models.FloatField(verbose_name='Volume of the flash', null=True)

    rho_l = models.FloatField(verbose_name='Density of liquid', null=True)  # remove null
    rho_v = models.FloatField(verbose_name='Density of vapour', null=True)  # remove null
    beta_mol = models.FloatField(verbose_name='Vapour phase mol fraction', null=True)     # remove null
    beta_vol = models.FloatField(verbose_name='Vapour phase volume fraction', null=True)     # remove null

                             # validators=[MinValueValidator(0.),
                             #            MaxValueValidator(1.)])


class ExperimentalFlash(Flash):
    vapour_mixture = models.ForeignKey('Mixture', null=True,
                                       related_name='experimental_flashes_as_gas')
    liquid_mixture = models.ForeignKey('Mixture', null=True,
                                       related_name='experimental_flashes_as_liquid')


class EosFlash(Flash):
    setup = models.ForeignKey('EosSetup')
    vapour_mixture = models.ForeignKey('Mixture', null=True,  # remove null
                                       related_name='eos_flashes_as_gas')
    liquid_mixture = models.ForeignKey('Mixture', null=True,    # remove null
                                       related_name='eos_flashes_as_liquid')

    input_txt = models.TextField(editable=False, null=True)
    output_txt = models.TextField(editable=False, null=True)




    # TO DO: refactor with this constraint enabled
    # class Meta:
    #    unique_together = (('t', 'p', 'mixture', 'eos', 'mode'),)

    def clean(self):
        z_calculated = self.y * self.beta_mol + self.x * (1 - self.beta_mol)
        if not np.allclose(self.mixture.z, z_calculated):
            raise ValidationError('Not all Zi != Yi*beta_mol + Xi*(1 - beta_mol)')

    def get_eos(self):
        return get_eos(self.eos)

    def get_txt(self):
        return write_input(self.mixture, self.eos, self.t, self.p, as_data=True)

    def as_json(self):
        cols = [[m.name, str(x_), str(y_)] for (m, x_, y_) in
                zip(self.mixture.compounds, self.x, self.y)]
        return json.dumps(cols)

    def _calc(self):
        """
        Calculate the flash for the given t and p
        """
        m = self.mixture  # just in sake of brevity
        m.clean()
        """
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
        """
        self.x, self.y, self.rho_l, self.rho_v, self.beta_mol, self.beta_vol, p, v = flash_routine(self)
        if self.p:
            self.v = v
        elif self.v:
            self.p = p

    def save(self, *args, **kwargs):
        if not self.id:
            # calculate the first time
            self._calc()
            # pass
        super(Flash, self).save(*args, **kwargs)

    @property
    def interactions(self):
        return self.setup.get_interactions(self.mixture)

    @property
    def x(self):
        return self.liquid_mixture.z

    @x.setter
    def x(self, liquid_mixture_composition):
        size = self.mixture.compounds.count()
        if len(liquid_mixture_composition) != size:
            raise ValueError('X must be same size than mixture (%d)' % size)

        try:
            if self.liquid_mixture:
                self.liquid_mixture.delete()
        except Mixture.DoesNotExist:
            pass
        m = Mixture()
        m.add_many(self.mixture.compounds, liquid_mixture_composition)
        self.liquid_mixture = m

    @property
    def y(self):
        return self.vapour_mixture.z

    @y.setter
    def y(self, vapour_mixture_composition):
        size = self.mixture.compounds.count()
        if len(vapour_mixture_composition) != size:
            raise ValueError('Y must be same size than mixture (%d)' % size)

        try:
            if self.vapour_mixture:
                self.vapour_mixture.delete()
        except Mixture.DoesNotExist:
            pass

        m = Mixture()
        m.add_many(self.mixture.compounds,
                   vapour_mixture_composition)
        self.vapour_mixture = m
