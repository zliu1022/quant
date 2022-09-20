#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
********************************
Choosing Colormaps in Matplotlib
********************************

Matplotlib has a number of built-in colormaps accessible via
`.matplotlib.cm.get_cmap`.  There are also external libraries that
have many extra colormaps, which can be viewed in the
`Third-party colormaps`_ section of the Matplotlib documentation.
Here we briefly discuss how to choose between the many options.  For
help on creating your own colormaps, see
:doc:`/tutorials/colors/colormap-manipulation`.

Overview
========

The idea behind choosing a good colormap is to find a good representation in 3D
colorspace for your data set. The best colormap for any given data set depends
on many things including:

- Whether representing form or metric data ([Ware]_)

- Your knowledge of the data set (*e.g.*, is there a critical value
  from which the other values deviate?)

- If there is an intuitive color scheme for the parameter you are plotting

- If there is a standard in the field the audience may be expecting

For many applications, a perceptually uniform colormap is the best choice;
i.e. a colormap in which equal steps in data are perceived as equal
steps in the color space. Researchers have found that the human brain
perceives changes in the lightness parameter as changes in the data
much better than, for example, changes in hue. Therefore, colormaps
which have monotonically increasing lightness through the colormap
will be better interpreted by the viewer. Wonderful examples of
perceptually uniform colormaps can be found in the
`Third-party colormaps`_ section as well.

Color can be represented in 3D space in various ways. One way to represent color
is using CIELAB. In CIELAB, color space is represented by lightness,
:math:`L^*`; red-green, :math:`a^*`; and yellow-blue, :math:`b^*`. The lightness
parameter :math:`L^*` can then be used to learn more about how the matplotlib
colormaps will be perceived by viewers.

An excellent starting resource for learning about human perception of colormaps
is from [IBM]_.


.. _color-colormaps_reference:

Classes of colormaps
====================

Colormaps are often split into several categories based on their function (see,
*e.g.*, [Moreland]_):

1. Sequential: change in lightness and often saturation of color
   incrementally, often using a single hue; should be used for
   representing information that has ordering.

2. Diverging: change in lightness and possibly saturation of two
   different colors that meet in the middle at an unsaturated color;
   should be used when the information being plotted has a critical
   middle value, such as topography or when the data deviates around
   zero.

3. Cyclic: change in lightness of two different colors that meet in
   the middle and beginning/end at an unsaturated color; should be
   used for values that wrap around at the endpoints, such as phase
   angle, wind direction, or time of day.

4. Qualitative: often are miscellaneous colors; should be used to
   represent information which does not have ordering or
   relationships.
"""

# sphinx_gallery_thumbnail_number = 2

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
#from colorspacious import cspace_converter


###############################################################################
#
# First, we'll show the range of each colormap. Note that some seem
# to change more "quickly" than others.

cmaps = {}

gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))


def plot_color_gradients(category, cmap_list):
    # Create figure and adjust figure height to number of colormaps
    nrows = len(cmap_list)
    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
    fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))
    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                        left=0.2, right=0.99)
    axs[0].set_title(f'{category} colormaps', fontsize=14)

    for ax, name in zip(axs, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(name))
        ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                transform=ax.transAxes)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axs:
        ax.set_axis_off()

    # Save colormap list for later.
    cmaps[category] = cmap_list


###############################################################################
# Sequential
# ----------
#
# For the Sequential plots, the lightness value increases monotonically through
# the colormaps. This is good. Some of the :math:`L^*` values in the colormaps
# span from 0 to 100 (binary and the other grayscale), and others start around
# :math:`L^*=20`. Those that have a smaller range of :math:`L^*` will accordingly
# have a smaller perceptual range. Note also that the :math:`L^*` function varies
# amongst the colormaps: some are approximately linear in :math:`L^*` and others
# are more curved.

plot_color_gradients('Perceptually Uniform Sequential',
                     ['viridis', 'plasma', 'inferno', 'magma', 'cividis'])

###############################################################################

plot_color_gradients('Sequential',
                     ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'])

###############################################################################
# Sequential2
# -----------
#
# Many of the :math:`L^*` values from the Sequential2 plots are monotonically
# increasing, but some (autumn, cool, spring, and winter) plateau or even go both
# up and down in :math:`L^*` space. Others (afmhot, copper, gist_heat, and hot)
# have kinks in the :math:`L^*` functions. Data that is being represented in a
# region of the colormap that is at a plateau or kink will lead to a perception of
# banding of the data in those values in the colormap (see [mycarta-banding]_ for
# an excellent example of this).

plot_color_gradients('Sequential (2)',
                     ['binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                      'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                      'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper'])

###############################################################################
# Diverging
# ---------
#
# For the Diverging maps, we want to have monotonically increasing :math:`L^*`
# values up to a maximum, which should be close to :math:`L^*=100`, followed by
# monotonically decreasing :math:`L^*` values. We are looking for approximately
# equal minimum :math:`L^*` values at opposite ends of the colormap. By these
# measures, BrBG and RdBu are good options. coolwarm is a good option, but it
# doesn't span a wide range of :math:`L^*` values (see grayscale section below).

plot_color_gradients('Diverging',
                     ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                      'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'])

###############################################################################
# Cyclic
# ------
#
# For Cyclic maps, we want to start and end on the same color, and meet a
# symmetric center point in the middle. :math:`L^*` should change monotonically
# from start to middle, and inversely from middle to end. It should be symmetric
# on the increasing and decreasing side, and only differ in hue. At the ends and
# middle, :math:`L^*` will reverse direction, which should be smoothed in
# :math:`L^*` space to reduce artifacts. See [kovesi-colormaps]_ for more
# information on the design of cyclic maps.
#
# The often-used HSV colormap is included in this set of colormaps, although it
# is not symmetric to a center point. Additionally, the :math:`L^*` values vary
# widely throughout the colormap, making it a poor choice for representing data
# for viewers to see perceptually. See an extension on this idea at
# [mycarta-jet]_.

plot_color_gradients('Cyclic', ['twilight', 'twilight_shifted', 'hsv'])

###############################################################################
# Qualitative
# -----------
#
# Qualitative colormaps are not aimed at being perceptual maps, but looking at the
# lightness parameter can verify that for us. The :math:`L^*` values move all over
# the place throughout the colormap, and are clearly not monotonically increasing.
# These would not be good options for use as perceptual colormaps.

plot_color_gradients('Qualitative',
                     ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
                      'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
                      'tab20c'])

###############################################################################
# Miscellaneous
# -------------
#
# Some of the miscellaneous colormaps have particular uses for which
# they have been created. For example, gist_earth, ocean, and terrain
# all seem to be created for plotting topography (green/brown) and water
# depths (blue) together. We would expect to see a divergence in these
# colormaps, then, but multiple kinks may not be ideal, such as in
# gist_earth and terrain. CMRmap was created to convert well to
# grayscale, though it does appear to have some small kinks in
# :math:`L^*`.  cubehelix was created to vary smoothly in both lightness
# and hue, but appears to have a small hump in the green hue area. turbo
# was created to display depth and disparity data.
#
# The often-used jet colormap is included in this set of colormaps. We can see
# that the :math:`L^*` values vary widely throughout the colormap, making it a
# poor choice for representing data for viewers to see perceptually. See an
# extension on this idea at [mycarta-jet]_ and [turbo]_.


plot_color_gradients('Miscellaneous',
                     ['flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                      'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
                      'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
                      'turbo', 'nipy_spectral', 'gist_ncar'])

plt.show()

