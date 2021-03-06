import os
import os.path
from glob import glob
from matplotlib import pyplot as plt
from matplotlib.testing.compare import comparable_formats, compare_images
from matplotlib.testing.noseclasses import ImageComparisonFailure
from sur import Mixture, EosSetup, setup_database

setup_database()


def clean():
    Mixture.objects.all().delete()
    EosSetup.objects.all().delete()
    plt.close('all')
    paths = glob(os.path.join(os.path.dirname(__file__),
                 'plots', '*_actual_.*'))

    for p in paths:
        os.remove(p)


def assert_fig(expected, extensions=['png']):
    j = os.path.join
    for extension in extensions:
        if not extension in comparable_formats():
            raise ImageComparisonFailure('Cannot compare %s files '
                                         'on this system' % extension)
        for fignum in plt.get_fignums():
            figure = plt.figure(fignum)
            path = os.path.dirname(__file__)
            actual_fname = j(path, 'plots', expected) + '_actual_.' + extension
            expected_fname = j(path, 'plots', expected) + '.' + extension
            figure.savefig(actual_fname)
            err = compare_images(expected_fname, actual_fname, 13)
            if err:
                raise ImageComparisonFailure(
                    'images not close: %(actual)s vs. %(expected)s '
                    '(RMS %(rms).3f)' % err)


def test_one_critical_point():
    m = Mixture()
    m.add_many("methane co2 n-decane", "0.25 0.50 0.25")
    s = EosSetup.objects.create(eos='RKPR', kij_mode='constants',
                                lij_mode='constants')
    s.set_interaction('kij', 'methane', 'co2', .1)
    s.set_interaction('kij', 'co2', 'n-decane',  0.091)
    env = m.get_envelope(s)
    env.plot()
    assert_fig('one_critical')


def test_no_critical():
    m = Mixture()
    m.add_many("METHANE n-HEXANE n-DECANE", "0.92 0.05 0.03")
    s = EosSetup.objects.create(eos='RKPR', kij_mode='constants', lij_mode='zero')
    s.set_interaction('kij', 'methane', 'n-decane', .1)
    env = m.get_envelope(s)
    env.plot()
    assert_fig('no_critical')


test_one_critical_point.teardown = clean
test_no_critical.teardown = clean
