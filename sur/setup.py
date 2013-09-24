def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('sur', parent_package, top_path)

    config.add_extension('_env', sources=['env.f90'])
    config.add_extension('_cubic', sources=['CubicParam.f90'])
    config.add_subpackage('tests')

    return config
