# -*- coding: utf-8 -*-
import quantities as pq

class BaseUnit(object):

    @classmethod
    def sanitize_unit(cls, unit):
        if hasattr(cls, 'VALIDATION_CLASS'):
            return pq.quantity.validate_dimensionality(unit).string

    @classmethod
    def convert(cls, array, original_unit, new_unit):
        return pq.Quantity(array, original_unit).rescale(new_unit).magnitude

    @classmethod
    def reverse(cls, display):
        """return the key unit for a given display value"""
        return dict([(v,k) for k,v in cls.CHOICES]).get(display, None)

class Temperature(BaseUnit):
    CLASS = pq.UnitTemperature

    CELSIUS = 'degC'
    KELVIN = 'K'
    FAHRENHEIT = 'degF'

    CHOICES = ((CELSIUS, u'°C'),
               (KELVIN, 'K'),
               (FAHRENHEIT, u'°F'))
    DEFAULT = KELVIN

    @classmethod
    def convert(cls, array, u_from, u_to):
        if u_from == u_to:
            return array

        if cls.KELVIN not in (u_from, u_to):
            array = cls.convert(array, u_from, cls.KELVIN)
            u_from = cls.KELVIN

        if (u_from, u_to) == (cls.KELVIN, cls.CELSIUS):
            return  array - 273.15
        elif (u_from, u_to) == (cls.CELSIUS, cls.KELVIN):
            return  array + 273.15
        elif (u_from, u_to) == (cls.KELVIN, cls.FAHRENHEIT):
            return  BaseUnit.convert(array, u_from, u_to) - 459.67
        elif (u_from, u_to) == (cls.FAHRENHEIT, cls.KELVIN):
            return  BaseUnit.convert(array + 459.67, u_from, u_to)




class Pressure(BaseUnit):
    VALIDATION_CLASS = pq.UnitQuantity

    PASCAL = 'Pa'
    BAR = 'bar'
    PSI = 'psi'
    MMHG = 'mmHg'
    ATM = 'atm'
    CHOICES = ((BAR, 'bar'),
               (MMHG, 'mmHg'),
               (ATM, 'atm'),
               (PASCAL, 'Pa'),
               (PASCAL, 'psi'))
    DEFAULT = BAR


class DensityVolume(BaseUnit):
    LITER_MOL = 'L/mol'
    MOL_LITER = 'mol/L'
    G_CM3 = 'g/cm**3'
    CHOICES = ((LITER_MOL, 'L/mol'),
               (MOL_LITER, 'mol/L'),
               (G_CM3, 'g/cm3'))
    DEFAULT = G_CM3


TEMPERATURE = 'T'
PRESSURE = 'P'
LLV_COMP_1 = u'X\u2081L1'
LLV_COMP_2 = u'X\u2081L2'
LLV_FRAC_V = u'Y\u2081'
LLV_VOL_DENS_1 = 'Vol/Density L1'
LLV_VOL_DENS_2 = 'Vol/Density L2'
LLV_VOL_DENS_V = 'Vol/Density V'
COMP_X1 = u'X\u2081'
COMP_X2 = u'X\u2082'
COMP_Y1 = u'Y\u2081'
COMP_Y2 = u'Y\u2082'
VOL_DENS = 'Vol/Density'
COMP_Z = 'Z'

ALL_VARS = [TEMPERATURE, PRESSURE, LLV_COMP_1, LLV_COMP_2, LLV_FRAC_V,
            LLV_VOL_DENS_1, LLV_VOL_DENS_2, LLV_VOL_DENS_V, COMP_X1, COMP_X2,
            COMP_Y1, COMP_Y2, VOL_DENS, COMP_Z]

ALL_UNITS = (dict(DensityVolume.CHOICES).keys() +
             dict(Temperature.CHOICES).keys() +
             dict(Pressure.CHOICES).keys()) + ['']


UNITS = {TEMPERATURE: Temperature,
         PRESSURE: Pressure,
         LLV_VOL_DENS_1: DensityVolume,
         LLV_VOL_DENS_2: DensityVolume,
         LLV_VOL_DENS_V: DensityVolume,
         VOL_DENS: DensityVolume,
        }


def default_units(header):
    """
    given a lists of headers, return the default unit for each one
    """
    units = []
    for k in header:
        if k in UNITS:
            units.append(UNITS[k].DEFAULT)
        else:
            units.append('')
    return units


def unit_belongs_to_header(unit, h):
    """
    asserts the unit represents the variable in the header
    """
    if h in UNITS :
        return unit in dict(UNITS[h].CHOICES).keys()
    else:
        return unit == ''

def get_units_display(units):
    u_displays = []
    for u in units:
        if u != '':
            for cls in [Temperature, Pressure, DensityVolume]:
                choices = dict(cls.CHOICES)
                if u in choices:
                    u = choices[u]
                    break
        u_displays.append(u)
    return u_displays


def units_map():
    units_by_header = {}
    for k in ALL_VARS:
        if k in UNITS:
            units_by_header[k] = dict(UNITS[k].CHOICES).values()
    return units_by_header



# tuples means one element of the set is required
PXY_REQUIRED = [PRESSURE, (COMP_X1, COMP_Y1, COMP_X2, COMP_Y2)]
PXY_ALLOWED = [PRESSURE, COMP_X1, COMP_Y1, COMP_X2, COMP_Y2, VOL_DENS]

TXY_REQUIRED = [TEMPERATURE, (COMP_X1, COMP_Y1, COMP_X2, COMP_Y2)]
TXY_ALLOWED = [TEMPERATURE, COMP_X1, COMP_Y1, COMP_X2, COMP_Y2, VOL_DENS]

CRI_REQUIRED = [TEMPERATURE, PRESSURE]
CRI_ALLOWED = [TEMPERATURE, PRESSURE, COMP_Z, VOL_DENS]

ISO_REQUIRED = [TEMPERATURE, PRESSURE]
ISO_ALLOWED = [TEMPERATURE, PRESSURE, VOL_DENS]

LLV_REQUIRED = [(PRESSURE, TEMPERATURE), (LLV_COMP_1, LLV_COMP_2, LLV_FRAC_V)]
LLV_ALLOWED = [PRESSURE, TEMPERATURE, LLV_COMP_1, LLV_COMP_2, LLV_FRAC_V,
               LLV_VOL_DENS_1, LLV_VOL_DENS_2, LLV_VOL_DENS_V]

RHO_REQUIRED = [PRESSURE, VOL_DENS]
RHO_ALLOWED = [PRESSURE, VOL_DENS]


