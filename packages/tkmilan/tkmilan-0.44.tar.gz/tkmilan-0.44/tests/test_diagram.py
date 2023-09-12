# import typing
import unittest
import logging

from tkmilan import diagram as d

logger = logging.getLogger(__name__)


class Test_Diagram_Geometry(unittest.TestCase):
    def test_line(self):
        ln_1 = d.GeometryLine.points(d.XY(0, 0), d.XY(10, 10))
        logger.debug('ln_1: %s', ln_1.equation)
        self.assertEqual(ln_1, d.GeometryLine(1.0, 0.0))
        ln_2 = d.GeometryLine.points(d.XY(0, 0), d.XY(1, -1))
        logger.debug('ln_2: %s', ln_2.equation)
        self.assertEqual(ln_2, d.GeometryLine(-1.0, 0.0))
        # Intersections
        self.assertEqual(ln_1.intersect_line(ln_2), d.XY(0, 0))

    def test_line_intersect(self):
        ln = d.GeometryLine(1, 0)
        logger.debug('ln: %s', ln.equation)
        self.assertEqual(ln.intersect_x(0), d.XY(0, 0))
        self.assertEqual(ln.intersect_x(10), d.XY(10, 10))
        self.assertEqual(ln.intersect_y(10), d.XY(10, 10))
        ln_h = d.GeometryLine(0, 10)
        logger.debug('ln_h: %s', ln_h.equation)
        self.assertEqual(ln_h.intersect_x(10), d.XY(10, 10))
        self.assertIsNone(ln_h.intersect_y(0))   # Parallel
        self.assertIsNone(ln_h.intersect_y(10))  # Coincident
        ln_v = d.GeometryLine(None, 10)
        logger.debug('ln_v: %s', ln_v.equation)
        self.assertIsNone(ln_v.intersect_x(0))   # Parallel
        self.assertIsNone(ln_v.intersect_x(10))  # Coincident
        self.assertEqual(ln_v.intersect_y(10), d.XY(10, 10))
        # Other
        self.assertEqual(ln.intersect_x(ln_v.c0), ln.intersect_line(ln_v))
        self.assertEqual(ln.intersect_y(ln_h.c0), ln.intersect_line(ln_h))

    def test_line_parallel(self):
        ln = d.GeometryLine(2, 0)
        p_i, p_n = d.XY(2, 4), d.XY(4, 2)
        self.assertIn(p_i, ln)  # Point in Line
        self.assertNotIn(p_n, ln)
        p_1 = d.XY(0, 2)
        ln_1 = ln.parallel_point(p_1)
        self.assertEqual(ln_1, d.GeometryLine(2, 2))
        p_2 = d.XY(1, 0)
        ln_2 = ln.parallel_point(p_2)
        self.assertEqual(ln_2, d.GeometryLine(2, -2.0))
        # Line by Point and Slope
        self.assertEqual(ln_2, d.GeometryLine.point_slope(p_2, ln.m))

    def test_line_perpendicular(self):
        ln_1 = d.GeometryLine(2, 20)
        ln_1p = d.GeometryLine(-1.0 / 2, 0)
        pi_1 = ln_1.intersect_line(ln_1p)
        po_1 = d.XY(10, 5)
        ln_1o = d.GeometryLine(ln_1p.m, po_1.y - ln_1p.m * po_1.x)
        self.assertIn(pi_1, ln_1)
        self.assertEqual(ln_1.perpendicular_point(pi_1), ln_1p)
        self.assertEqual(ln_1.perpendicular_point(po_1), ln_1o)
        self.assertEqual(ln_1p.parallel_point(po_1), ln_1o)


if __name__ == '__main__':
    import sys
    logs_lvl = logging.DEBUG if '-v' in sys.argv else logging.INFO
    logging.basicConfig(level=logs_lvl, format='%(levelname)5.5s:%(funcName)s: %(message)s', stream=sys.stderr)
    unittest.main()
