// CPython extension for checking wether or not a point (x, y)
//  located within a polygon.
// source: https://wrfranklin.org/Research/Short_Notes/pnpoly.html
// with slight modification.

#include <Python.h>
#include <vector>
#include <string>


#ifdef __cplusplus
extern "C" {
#endif


bool point_in_polygon_single(std::vector<double> polygon_x,
                             std::vector<double> polygon_y,
                             double test_x, double test_y)
{
    int n_vert = polygon_x.size();
    int i, j, c = 0;
    for (i = 0, j = n_vert-1; i < n_vert; j = i++) {
        if ( ((polygon_y.at(i)>test_y) != (polygon_y.at(j)>test_y)) &&
    	     (test_x < (polygon_x.at(j)-polygon_x.at(i)) * (test_y-polygon_y.at(i)) / (polygon_y.at(j)-polygon_y.at(i)) + polygon_x.at(i)) )
            c = !c;
    }
    return (bool) c;
}


static PyObject* point_in_polygon(PyObject* self, PyObject* args)
{
    int py_n_vert;
    PyObject *py_polygon_x;
    PyObject *py_polygon_y;
    double test_x, test_y;
   /* Parse the input tuple */
    if (!PyArg_ParseTuple(args, "iOOdd", &py_n_vert, &py_polygon_x, &py_polygon_y, &test_x, &test_y))
        return NULL;
    PyObject *iterator_polygon_x = PyObject_GetIter(py_polygon_x);
    if (!iterator_polygon_x)
        return NULL;
    PyObject *iterator_polygon_y = PyObject_GetIter(py_polygon_y);
    if (!iterator_polygon_y)
        return NULL;

    size_t n_vert = (size_t)py_n_vert;
    std::vector<double> polygon_x, polygon_y;

    for (size_t idx = 0; idx < n_vert; ++idx) {
        polygon_x.push_back(PyFloat_AsDouble(PyIter_Next(iterator_polygon_x)));
        polygon_y.push_back(PyFloat_AsDouble(PyIter_Next(iterator_polygon_y)));
    }

    if (polygon_x.at(0) != polygon_x.at(n_vert-1)) {
        PyErr_SetString(PyExc_ValueError, "Polygon is not closed.");
        return NULL;
    }
    if (polygon_y.at(0) != polygon_y.at(n_vert-1)) {
        PyErr_SetString(PyExc_ValueError, "Polygon is not closed.");
        return NULL;
    }

    bool c = point_in_polygon_single(polygon_x, polygon_y, test_x, test_y);

    return c ? Py_True: Py_False;
}


static PyMethodDef pcp_methods[] = {
    { "point_in_polygon", point_in_polygon, METH_VARARGS,
    "Checks if a point is located within a polygon.\n"
    "The polygon must be closed, i.e. the last point must be identical to the\n"
    "first point. polygon_x[0] == polygon_x[-1] and polygon_y[0] == polygon_y[-1]."
    "\n"
    "Parameters\n"
    "----------\n"
    "length : int\n"
    "    Number of vertices in the polygon.\n"
    "polygon_x : list\n"
    "    List of x coordinates of the polygon vertices. Must have length 'length'.\n"
    "polygon_y : list\n"
    "    As polygon_x, but for the y coordinates.\n"
    "test_x : float\n"
    "    X coordinate of the test point.\n"
    "test_y : float\n"
    "    Y coordinate of the test point.\n"
    "\nReturns\n"
    "-------\n"
    "is_contained : bool\n"
    "    True if the polygon contains the test point.\n"
    "\n"
    "Edge Cases\n"
    "----------\n"
    "    Points on a right or upwards facing edges are considered\n"
    "    outside the polygon, points on left or downards facing\n"
    "    edges are considered inside.\n"
    "    Vertices which are on the top-left \n"
    "\n"
    "Raises\n"
    "------\n"
    "ValueError\n"
    "    If the polygon is not closed.\n"
    "\n" },
    { NULL, NULL, 0, NULL }
};
// Edge Cases
//     ----------
//     Left edge: INSIDE
//     Top edge: OUTSIDE
//     Right edge: OUTSIDE
//     Bottom edge: INSIDE
// Our Module Definition struct
static struct PyModuleDef pcp_module = {
    PyModuleDef_HEAD_INIT,
    "polygon_contains_point",
    NULL,
    -1,
    pcp_methods
};


PyMODINIT_FUNC PyInit_polygon_contains_point(void)
{
    return PyModule_Create(&pcp_module);
}

#ifdef __cplusplus
}  // closes extern "C"
#endif
