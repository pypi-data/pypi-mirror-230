# point_in_polygon
CPython extension for checking if a polygon contains a given point.
It wraps the PNPOLY point inclusion in polygon test by W. Randolph Franklin
(ref.: https://wrfranklin.org/Research/Short_Notes/pnpoly.html).

The algorithm assumes the polygon to be closed, i.e. that the first and
last point are identical.

## Edge cases
points are considered to be outside the polygon if
they are completely outside the polygon (obviously) or
located on an upper (positive y) or right edge (positive x).
A point on the upper left or lower right corner of a square
would therefore also be considered outside the polygon.

## Example
```python
from point_in_polygon import point_in_polygon
# a simple square
polygon = [(0.1, 0.1), (2., 0.1), (2., 2.), (0.1, 2.), (0.1, 0.1)]
polygon_x, polygon_y = zip(*polygon)
print(point_in_polygon(5, polygon_x, polygon_y, 0.4, 1.7))
>>> True
print(point_in_polygon(5, polygon_x, polygon_y, 0.02, 1.7))
>>> False
```

