"""
Plot shortcuts utilities
"""

from itertools import cycle


def multiplot(envelopes, experimental_envelopes=None, formats=None,
              critical_point='o', experimental_colors=None,
              experimental_markers=None):
    """merge the plot of multiples envelopes"""

    COLORS = ('red', 'blue', 'green', 'violet', 'black', 'cyan',
              'magenta', 'darkorange', 'GreenYellow', 'SaddleBrown')
    len_envs = len(envelopes)

    if formats is not None and len(formats) != len_envs:
        raise ValueError('If you give formats, should be one for each envelope')
    elif formats is None:
        colors = cycle(COLORS)
        formats = [colors.next() for i in xrange(len_envs)]

    if experimental_envelopes:
        len_experimental_envs = len(experimental_envelopes)

        if experimental_colors and len(experimental_colors) != len_experimental_envs:
            raise ValueError('If you give colors, should be one for each experimental envelope')
        elif experimental_colors is None:
            colors = cycle(COLORS)
            experimental_colors = [colors.next() for i in xrange(len_experimental_envs)]

        if experimental_markers and len(experimental_markers) != len_experimental_envs:
            raise ValueError('If you give markers, should be one for each experimental envelope')
        elif experimental_markers is None:
            experimental_markers = ['s' for i in xrange(len_experimental_envs)]
    else:
        experimental_envelopes, experimental_markers, experimental_colors = [], [], []

    first = envelopes[0].plot(format=formats[0],
                              critical_point=critical_point)
    plot = lambda fig, (env, format): env.plot(fig, format=format,
                                               critical_point=critical_point)
    fig = reduce(plot, zip(envelopes[1:], formats[1:]), first)
    plot_exp = lambda fig, (exp_env, marker, color): exp_env.plot(fig, marker=marker,
                                                                  color=color)
    return reduce(plot_exp, zip(experimental_envelopes, experimental_markers,
                                experimental_colors), fig)
