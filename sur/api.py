from .database import Compound


class System(list):
    def __setitem__(self, key, item):
        if not isinstance(item, (Compound, basestring)):
            raise ValueError('System can be defined only by compounds')

        if isinstance(item, basestring):
            try h

        self[key] = item

class Mixture(HasTraits):
    system = Instance(System)
    z = Array()

