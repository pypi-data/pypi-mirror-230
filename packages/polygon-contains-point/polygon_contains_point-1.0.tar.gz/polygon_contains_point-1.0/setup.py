from distutils.core import setup, Extension

polygon_module = Extension('polygon_contains_point',
                           sources = ['src/point_in_polygon/point_in_polygon.cpp'])

long_description = """A CPython extension which wraps the PNPOLY
point inclusion in polygon test by W. Randolph Franklin
(ref.: https://wrfranklin.org/Research/Short_Notes/pnpoly.html).
"""

setup (name = 'polygon_contains_point',
       version = '1.0',
       description = 'CPython extension for checking if a polygon contains a given point.',
       url = 'https://github.com/sgaebel/point_in_polygon',
       author = 'Dr. Sebastian M. Gaebel',
       author_email = 'gaebel.sebastian@gmail.com',
       license = 'MIT',
       ext_modules = [polygon_module],
       long_description = long_description,
       classifiers = [
              'Development Status :: 5 - Production/Stable',
              'Intended Audience :: Developers',
              'Topic :: Scientific/Engineering :: Mathematics',
              'License :: OSI Approved :: MIT License',
              'Programming Language :: Python :: 3.10'],
       keywords = 'geometry polygon',
       python_requires = '>=3.10')
