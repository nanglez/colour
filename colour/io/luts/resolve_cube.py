# -*- coding: utf-8 -*-
"""
Resolve .cube LUT Format Input / Output Utilities
=================================================

Defines *Resolve* *.cube* *LUT* Format related input / output utilities
objects.

-   :func:`colour.io.read_LUT_ResolveCube`
-   :func:`colour.io.write_LUT_ResolveCube`

References
----------
-   :cite:`Chamberlain2015` :﻿Chamberlain, P. (2015). LUT documentation
    (to create from another program). Retrieved August 23, 2018, from
    https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=40284#p232952
"""

from __future__ import division, unicode_literals

import numpy as np
import os
import re

from colour.constants import DEFAULT_FLOAT_DTYPE
from colour.io.luts import LUT1D, LUT2D, LUT3D, LUTSequence
from colour.utilities import tstack

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2018 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['read_LUT_ResolveCube', 'write_LUT_ResolveCube']


def read_LUT_ResolveCube(path):
    """
    Reads given *Resolve* *.cube* *LUT* file.

    Parameters
    ----------
    path : unicode
        *LUT* path.

    Returns
    -------
    LUT2D or LUT3D or LUTSequence
        :class:`LUT2D` or :class:`LUT3D` or :class:`LUTSequence` class
        instance.

    References
    ----------
    :cite:`Chamberlain2015`

    Examples
    --------
    Reading a 2D *Resolve* *.cube* *LUT*:

    >>> path = os.path.join(
    ...     os.path.dirname(__file__), 'tests', 'resources', 'resolve_cube',
    ...     'ACES_Proxy_10_to_ACES.cube')
    >>> print(read_LUT_ResolveCube(path))
    LUT2D - ACES Proxy 10 to ACES
    -----------------------------
    <BLANKLINE>
    Dimensions : 2
    Domain     : [[0 0 0]
                  [1 1 1]]
    Size       : (32, 3)

    Reading a 3D *Resolve* *.cube* *LUT*:

    >>> path = os.path.join(
    ...     os.path.dirname(__file__), 'tests', 'resources', 'resolve_cube',
    ...     'ColourCorrect.cube')
    >>> print(read_LUT_ResolveCube(path))
    LUT3D - Generated by Foundry::LUT
    ---------------------------------
    <BLANKLINE>
    Dimensions : 3
    Domain     : [[0 0 0]
                  [1 1 1]]
    Size       : (4, 4, 4, 3)

    Reading a 3D *Resolve* *.cube* *LUT* with comments:

    >>> path = os.path.join(
    ...     os.path.dirname(__file__), 'tests', 'resources', 'resolve_cube',
    ...     'Demo.cube')
    >>> print(read_LUT_ResolveCube(path))
    LUT2D - Demo
    ------------
    <BLANKLINE>
    Dimensions : 2
    Domain     : [[ 0.  0.  0.]
                  [ 3.  3.  3.]]
    Size       : (3, 3)
    Comment 01 : Comments can't go anywhere
    """

    title = re.sub('_|-|\.', ' ', os.path.splitext(os.path.basename(path))[0])
    size2D = 2
    size3D = 2
    table = []
    comments = []
    has_2D, has_3D = False, False

    def _parse_array(array):
        """
        Converts given string array to :class:`ndarray` class.
        """

        return np.array(list(map(DEFAULT_FLOAT_DTYPE, array)))

    with open(path) as cube_file:
        lines = cube_file.readlines()
        LUT = LUTSequence(LUT2D(), LUT3D())
        for line in lines:
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith('#'):
                comments.append(line[1:].strip())
                continue

            tokens = line.split()
            if tokens[0] == 'TITLE':
                title = ' '.join(tokens[1:])[1:-1]
            elif tokens[0] == 'LUT_1D_INPUT_RANGE':
                domain = _parse_array(tokens[1:])
                LUT[0].domain = tstack([domain, domain, domain])
            elif tokens[0] == 'LUT_3D_INPUT_RANGE':
                domain = _parse_array(tokens[1:])
                LUT[1].domain = tstack([domain, domain, domain])
            elif tokens[0] == 'LUT_1D_SIZE':
                has_2D = True
                size2D = np.int_(tokens[1])
            elif tokens[0] == 'LUT_3D_SIZE':
                has_3D = True
                size3D = np.int_(tokens[1])
            else:
                table.append(_parse_array(tokens))

    table = np.asarray(table)
    if has_2D and has_3D:
        LUT[0].name = '{0} - Shaper'.format(title)
        LUT[1].name = '{0} - Cube'.format(title)
        LUT[1].comments = comments
        LUT[0].table = table[:size2D]
        # The lines of table data shall be in ascending index order,
        # with the first component index (Red) changing most rapidly,
        # and the last component index (Blue) changing least rapidly.
        LUT[1].table = table[size2D:].reshape(
            (size3D, size3D, size3D, 3), order='F')
        return LUT
    elif has_2D:
        LUT[0].name = title
        LUT[0].comments = comments
        LUT[0].table = table
        return LUT[0]
    elif has_3D:
        LUT[1].name = title
        LUT[1].comments = comments
        # The lines of table data shall be in ascending index order,
        # with the first component index (Red) changing most rapidly,
        # and the last component index (Blue) changing least rapidly.
        table = table.reshape([size3D, size3D, size3D, 3], order='F')
        LUT[1].table = table
        return LUT[1]


def write_LUT_ResolveCube(LUT, path, decimals=7):
    """
    Writes given *LUT* to given  *Resolve* *.cube* *LUT* file.

    Parameters
    ----------
    LUT : LUT1D or LUT2D or LUT3D or LUTSequence
        :class:`LUT1D`, :class:`LUT2D` or :class:`LUT3D` or
        :class:`LUTSequence` class instance to write at given path.
    path : unicode
        *LUT* path.
    decimals : int, optional
        Formatting decimals.

    Returns
    -------
    bool
        Definition success.

    References
    ----------
    :cite:`Chamberlain2015`

    Examples
    --------
    Writing a 2D *Resolve* *.cube* *LUT*:

   >>> from colour.algebra import spow
    >>> domain = np.array([[-0.1, -0.1, -0.1], [3.0, 3.0, 3.0]])
    >>> LUT = LUT2D(
    ...     spow(LUT2D.linear_table(16, domain), 1 / 2.2),
    ...     'My LUT',
    ...     domain,
    ...     comments=['A first comment.', 'A second comment.'])
    >>> write_LUT_ResolveCube(LUT, 'My_LUT.cube')  # doctest: +SKIP

    Writing a 3D *Iridas* *.cube* *LUT*:

    >>> domain = np.array([[-0.1, -0.1, -0.1], [3.0, 3.0, 3.0]])
    >>> LUT = LUT3D(
    ...     spow(LUT3D.linear_table(16, domain), 1 / 2.2),
    ...     'My LUT',
    ...     domain,
    ...     comments=['A first comment.', 'A second comment.'])
    >>> write_LUT_ResolveCube(LUT, 'My_LUT.cube')  # doctest: +SKIP
    """

    has_3D, has_2D = False, False

    if isinstance(LUT, LUTSequence):
        assert (len(LUT) == 2 and
                (isinstance(LUT[0], LUT1D) or isinstance(LUT[0], LUT2D)) and
                isinstance(LUT[1], LUT3D)), \
                'LUTSequence must be 1D+3D or 2D+3D!'
        has_2D = True
        has_3D = True
        name = LUT[1].name
        if isinstance(LUT[0], LUT1D):
            LUT[0] = LUT[0].as_LUT(LUT2D)

    elif isinstance(LUT, LUT1D):
        name = LUT.name
        LUT = LUTSequence(LUT.as_LUT(LUT2D), LUT3D())
        has_2D = True

    elif isinstance(LUT, LUT2D):
        name = LUT.name
        LUT = LUTSequence(LUT, LUT3D())
        has_2D = True

    elif isinstance(LUT, LUT3D):
        name = LUT.name
        LUT = LUTSequence(LUT2D(), LUT)
        has_3D = True

    else:
        assert False, 'LUT must be 1D, 2D, 3D, 1D+3D or 2D+3D!'

    assert (len(np.unique(LUT[0].domain)) == 2 and
            len(np.unique(LUT[1].domain)) == 2), 'LUT domain must be 1D!'

    if has_2D:
        assert 2 <= LUT[0].size <= 65536, \
            'Shaper size must be in domain [2, 65536]!'
    if has_3D:
        assert 2 <= LUT[1].size <= 256, 'Cube size must be in domain [2, 256]!'

    def _format_array(array):
        """
        Formats given array as a *Resolve* *.cube* data row.
        """

        return '{1:0.{0}f} {2:0.{0}f} {3:0.{0}f}'.format(decimals, *array)

    def _format_tuple(array):
        """
        Formats given array as 2 space separated values to *decimals* precison.
        """

        return '{1:0.{0}f} {2:0.{0}f}'.format(decimals, *array)

    with open(path, 'w') as cube_file:
        cube_file.write('TITLE "{0}"\n'.format(name))

        if LUT[0].comments:
            for comment in LUT[0].comments:
                cube_file.write('# {0}\n'.format(comment))

        if LUT[1].comments:
            for comment in LUT[1].comments:
                cube_file.write('# {0}\n'.format(comment))

        default_domain = np.array([[0, 0, 0], [1, 1, 1]])

        if has_2D:
            cube_file.write('{0} {1}\n'.format('LUT_1D_SIZE',
                            LUT[0].table.shape[0]))
            if not np.array_equal(LUT[0].domain, default_domain):
                cube_file.write('LUT_1D_INPUT_RANGE {0}\n'.format(
                    _format_tuple([LUT[0].domain[0][0], LUT[0].domain[1][0]])))

        if has_3D:
            cube_file.write('{0} {1}\n'.format('LUT_3D_SIZE',
                            LUT[1].table.shape[0]))
            if not np.array_equal(LUT[1].domain, default_domain):
                cube_file.write('LUT_3D_INPUT_RANGE {0}\n'.format(
                    _format_tuple([LUT[1].domain[0][0], LUT[1].domain[1][0]])))

        if has_2D:
            table = LUT[0].table
            for row in table:
                cube_file.write('{0}\n'.format(_format_array(row)))
            cube_file.write('\n')

        if has_3D:
            table = LUT[1].table.reshape([-1, 3], order='F')
            for row in table:
                cube_file.write('{0}\n'.format(_format_array(row)))

    return True
