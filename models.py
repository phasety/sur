from traits.api import HasTraits, Float, Str, Dict


class Compound(HasTraits):
    name = Str('')
    formula = Str('')
    tc = Float()
    pc = Float()
    vc = Float()
    acentric_factor = Float()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "%s('%s')" % (type(self).__name__), unicode(self))


class System(HasTraits):
    compounds = Dict(key_trait=Compound, value_trait=Float)
