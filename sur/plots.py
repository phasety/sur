"""
Plot shortcuts utilities
"""

from itertools import cycle


def multiplot(envelopes=None, experimental_envelopes=None, formats=None,
              critical_point='o', experimental_colors=None,
              experimental_markers=None, legends=None):
    """merge the plot of multiples envelopes"""

    COLORS = ('red', 'blue', 'green', 'violet', 'black', 'cyan',
              'magenta', 'darkorange', 'GreenYellow', 'SaddleBrown')

    if not any((envelopes, experimental_envelopes)):
        raise ValueError('No envelopes given')

    envelopes = envelopes or []
    experimental_envelopes = experimental_envelopes or []

    len_envs = len(envelopes)
    len_experimental_envs = len(experimental_envelopes)

    if formats is not None and len(formats) != len_envs:
        raise ValueError('If you give formats, should be one for each envelope')
    elif formats is None:
        colors = cycle(COLORS)
        formats = [colors.next() for i in xrange(len_envs)]

    if experimental_envelopes:

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

    if envelopes:
        first = envelopes[0].plot(format=formats[0],
                              critical_point=critical_point)
        plot = lambda fig, (env, format): env.plot(fig, format=format,
                                               critical_point=critical_point)
        fig = reduce(plot, zip(envelopes[1:], formats[1:]), first)
    else:
        # if only experimentals
        # base is an experimental one
        fig = experimental_envelopes[0].plot(marker=experimental_markers[0],
                                             color=experimental_colors[0])
        experimental_envelopes = experimental_envelopes[1:]
        experimental_markers = experimental_markers[1:]
        experimental_colors = experimental_colors[1:]

    plot_exp = lambda fig, (exp_env, marker, color): exp_env.plot(fig, marker=marker,
                                                                  color=color)

    multi_fig = reduce(plot_exp, zip(experimental_envelopes, experimental_markers,
                       experimental_colors), fig)

    if legends:
        ax = multi_fig.get_axes()[-1]
        ax.legend(loc=legends)

    return multi_fig