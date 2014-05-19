import numpy
import envelope_sp as envelope

comp = numpy.ones(10)
tc = numpy.random.random((10,))
pc = numpy.random.random((10,))
tc = numpy.random.random((10,))
ohm = numpy.random.random((10,))
ac = numpy.random.random((10,))
b = numpy.random.random((10,))
del_ = numpy.random.random((10,))
k = numpy.random.random((10,))
Kij0 = numpy.random.random((10,10))
Kij1 = numpy.random.random((10,10))
Lij = numpy.random.random((10,10))

envelope, critical = envelope.rkpr(comp, tc, pc, ohm, ac, b, del_, k)

print envelope, critical
