# -*- coding: utf-8 -*-
from decimal import Decimal
from itertools import combinations

from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.utils import IntegrityError

import numpy as np

from . import units

DEFAULT_MAX_LENGTH = 255
MAX_DIGITS = 15
DECIMAL_PLACES = 5


class CompoundManager(models.Manager):

    def find(self, val, exact=False):
        """
        Given an string, looks for compounds matching
        name, formula o aliases.

        If ``exact`` is True, the
        the filter try match the whole val (case insensitive).
        Otherwise, match the as `starts with` (case insensitive).
        """
        if isinstance(val, self.model):
            return self.filter(id=val.id)

        criteria = "iexact" if exact else "istartswith"

        lookup = lambda key: dict((("%s__%s" % (key, criteria), val),))

        q_name = Q(**lookup('name'))
        q_formula = Q(**lookup('formula'))
        q_alias = Q(**lookup('alias__name'))

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
    weight = models.FloatField(editable=False, null=True, blank=True)

    def __unicode__(self):
        return self.name

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

    def save(self, *args, **kwargs):
        self.weight = self.calculate_weight()
        super(Compound, self).save(*args, **kwargs)

    class Meta:
        ordering = ('mixturefraction__position', 'weight')


class Alias(models.Model):
    """
    Some shortchuts to find Compounds.
    Example: 'c5' -> Pentane
    """

    compound = models.ForeignKey('Compound')
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.compound.name)


class InteractionManager(models.Manager):

    def find(self, eos, compound1, compound2=None, mixture=None):
        """
        filter interactions for EOS and compounds
        globally defined on specific for a mixture.
        """
        comps = Compound.objects.find(compound1)
        qs = self.filter(eos=eos, compounds__in=comps)
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

    CHOICES = (('PR', 'PR'), ('SRK', 'SRK'), ('RKPR', 'RKPR'))

    compounds = models.ManyToManyField('Compound')
    eos = models.CharField(max_length=DEFAULT_MAX_LENGTH)
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
        if parameter.compounds.all().count() == 2:
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


class K0InteractionParameter(AbstractInteractionParameter):
    pass


class TstarInteractionParameter(AbstractInteractionParameter):
    pass


class LijInteractionParameter(AbstractInteractionParameter):
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
    compounds = models.ManyToManyField(Compound, through='MixtureFraction')

    @property
    def z(self):
        """
        the :abbr:`Z (Composition array)` as a :class:`numpy.array` instance
        in the same order than ``self.compounds.all()``
        """
        return np.array([float(f.fraction) for f in self.fractions.all()])

    @property
    def total_z(self):
        """
        Return the summatory of z fractions.
        Should sum 1.0 to be a valid mixture
        """
        return MixtureFraction.objects.filter(mixture=self).\
            aggregate(total=models.Sum('fraction'))['total'] or 0

    def _compounds_array_field(self, field, as_array=True):
        """helper to construct an array-like from compound's field"""
        values = [getattr(v, field) for v in self.compounds.all()]
        if as_array:
            values = np.array(values)
        return values

    @property
    def tc(self):
        """
        return the :abbr:`Tc (Critical temperature)` array.

        It is the :abbr:`Tc` of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds.all()``
        """
        return self._compounds_array_field('tc')

    @property
    def pc(self):
        """
        return the :abbr:`Pc (Critical pressure)` array.

        It is the :abbr:`Pc` of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds.all()``
        """
        return self._compounds_array_field('pc')

    @property
    def vc(self):
        """
        return the :abbr:`Vc (Critical volume)` array.

        It is the :abbr:`Vc` of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds.all()``
        """
        return self._compounds_array_field('vc')

    @property
    def acentric_factor(self):
        """
        return the :abbr:`$\omega$ (acentric_factor)` array.

        It is the :abbr:`$\omega$ of each compound in the mixture as a
        :class:`numpy.array` instance in the same order
        than ``self.compounds.all()``
        """
        return self._compounds_array_field('acentric_factor')

    def k0(self, eos):
        """
        return the 2d square matrix of k0 interaction parameters
        """
        compounds = self.compounds.all()
        n = compounds.count()
        m = np.zeros((n, n))
        for ((x, c1), (y, c2)) in combinations(enumerate(compounds), 2):
            try:
                k = K0InteractionParameter.objects.find(eos, c1, c2, self)[0].value
                m[x, y] = k
            except:
                pass

        # 0 1 2    0 0 0
        # 0 0 0 +  1 0 0
        # 0 0 0    2 0 0
        diagonal_mirrored = np.rot90(np.flipud(m), -1)
        return m + diagonal_mirrored

    def sort(self):
        """Sort the mixture by compound's weight"""
        for pos, f in enumerate(self.fractions.all().order_by('compound__weight')):
            f.position = pos
            f.save()

    def add(self, compound, fraction=None):
        """
        Add a compound fraction to the mixture.

        Compound could be a :class:`Compound` instance or
        a string passed to :meth:`Compound.objects.find`


        if fraction is None, it is set to the complement to reach
        ``self.total_z == Decimal('1.0')``
        """

        if not self.id:
            self.save()
        if isinstance(compound, basestring):
            compound = Compound.objects.find(compound, exact=True).get()

        if fraction:
            future_total = Decimal(fraction) + self.total_z
            if future_total > Decimal('1.0'):
                raise ValueError('Add this fraction would exceed 1.0. Max fraction '
                                 'allowed is %s' % (Decimal('1.0') - self.total_z))
        else:
            fraction = Decimal('1.0') - self.total_z

        MixtureFraction.objects.create(mixture=self,
                                       compound=compound,
                                       fraction=fraction)

    def clean(self):

        if self.total_z != Decimal('1.0'):
            raise ValidationError('The mixture fractions should sum 1.0')
