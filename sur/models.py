# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from . import units

DEFAULT_MAX_LENGTH = 255
MAX_DIGITS = 15
DECIMAL_PLACES = 5


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

    def get_absolute_url(self):
        return '#'

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
        ordering = ['weight']


class Alias(models.Model):
    compound = models.ForeignKey('Compound')
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)


class MixtureFraction(models.Model):
    mixture = models.ForeignKey('Mixture')
    compound = models.ForeignKey('Compound')
    fraction = models.DecimalField(decimal_places=4,
                                   max_digits=MAX_DIGITS,
                                   validators=[MinValueValidator(0.),
                                               MaxValueValidator(1.)])

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MixtureFraction, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("mixture", "compound")


class Mixture(models.Model):
    compounds = models.ManyToManyField(Compound, through='MixtureFraction')



    def add(self, compound, fraction):
        if not self.id:
            self.save()
        MixtureFraction.objects.create(mixture=self,
                                       compound=compound,
                                       fraction=fraction)

    def clean(self):
        total = MixtureFraction.objects.filter(mixture=self).\
                        aggregate(total=models.Sum('fraction'))['total']
        if total != Decimal('1.0'):
            raise ValidationError('The mixture fractions should sum 1.0')

