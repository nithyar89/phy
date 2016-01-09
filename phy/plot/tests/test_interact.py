# -*- coding: utf-8 -*-

"""Test interact."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

from itertools import product

import numpy as np
from numpy.testing import assert_equal as ae
from numpy.testing import assert_allclose as ac

from ..base import BaseVisual
from ..interact import Grid, Boxed, Stacked
from ..panzoom import PanZoom
from ..transform import NDC


#------------------------------------------------------------------------------
# Fixtures
#------------------------------------------------------------------------------

class MyTestVisual(BaseVisual):
    def __init__(self):
        super(MyTestVisual, self).__init__()
        self.vertex_shader = """
            attribute vec2 a_position;
            void main() {
                gl_Position = transform(a_position);
                gl_PointSize = 2.;
            }
        """
        self.fragment_shader = """
            void main() {
                gl_FragColor = vec4(1, 1, 1, 1);
            }
        """
        self.set_primitive_type('points')

    def set_data(self):
        n = 1000

        coeff = [(1 + i + j) for i, j in product(range(2), range(3))]
        coeff = np.repeat(coeff, n)
        coeff = coeff[:, None]

        position = .1 * coeff * np.random.randn(2 * 3 * n, 2)

        self.program['a_position'] = position.astype(np.float32)


def _create_visual(qtbot, canvas, interact, box_index):
    c = canvas

    # Attach the interact *and* PanZoom. The order matters!
    interact.attach(c)
    PanZoom(aspect=None, constrain_bounds=NDC).attach(c)

    visual = MyTestVisual()
    c.add_visual(visual)
    visual.set_data()

    visual.program['a_box_index'] = box_index.astype(np.float32)

    c.show()
    qtbot.waitForWindowShown(c.native)


#------------------------------------------------------------------------------
# Test grid
#------------------------------------------------------------------------------

def test_grid_1(qtbot, canvas):

    n = 1000

    box_index = [[i, j] for i, j in product(range(2), range(3))]
    box_index = np.repeat(box_index, n, axis=0)

    grid = Grid((2, 3))
    _create_visual(qtbot, canvas, grid, box_index)

    grid.add_boxes(canvas)

    # qtbot.stop()


def test_grid_2(qtbot, canvas):

    n = 1000

    box_index = [[i, j] for i, j in product(range(2), range(3))]
    box_index = np.repeat(box_index, n, axis=0)

    grid = Grid()
    _create_visual(qtbot, canvas, grid, box_index)
    grid.shape = (3, 3)
    assert grid.shape == (3, 3)

    # qtbot.stop()


def test_boxed_1(qtbot, canvas):

    n = 6
    b = np.zeros((n, 4))

    b[:, 0] = b[:, 1] = np.linspace(-1., 1. - 1. / 3., n)
    b[:, 2] = b[:, 3] = np.linspace(-1. + 1. / 3., 1., n)

    n = 1000
    box_index = np.repeat(np.arange(6), n, axis=0)

    boxed = Boxed(box_bounds=b)
    _create_visual(qtbot, canvas, boxed, box_index)

    ae(boxed.box_bounds, b)
    boxed.box_bounds = b

    boxed.update_boxes(boxed.box_pos, boxed.box_size)
    ac(boxed.box_bounds, b)

    # qtbot.stop()


def test_boxed_2(qtbot, canvas):
    """Test setting the box position and size dynamically."""

    n = 1000
    pos = np.c_[np.zeros(6), np.linspace(-1., 1., 6)]
    box_index = np.repeat(np.arange(6), n, axis=0)

    boxed = Boxed(box_pos=pos)
    _create_visual(qtbot, canvas, boxed, box_index)

    boxed.box_pos *= .25
    boxed.box_size = [1, .1]

    idx = boxed.get_closest_box((.5, .25))
    assert idx == 4

    # qtbot.stop()


def test_stacked_1(qtbot, canvas):

    n = 1000
    box_index = np.repeat(np.arange(6), n, axis=0)

    stacked = Stacked(n_boxes=6, margin=-10, origin='upper')
    _create_visual(qtbot, canvas, stacked, box_index)

    # qtbot.stop()
