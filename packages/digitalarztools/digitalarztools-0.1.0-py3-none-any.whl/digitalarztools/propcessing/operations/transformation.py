from math import floor

import numpy as np
from affine import Affine


class TransformationOperations:
    @staticmethod
    def coord_to_utm_srid(long, lat):
        zone = (floor((long + 180) / 6) % 60) + 1
        dir = 6 if lat >= 0 else 7
        return int(f"32{dir}{zone}")

    @staticmethod
    def meter_2_dd(length: float):
        return length / (110 * 1000)

    @staticmethod
    def get_affine_matrix(extent: tuple, img_resolution: tuple):
        """
        Parameters
        :param extent: Map Or Layer extent (minx, miny, maxx, maxy)
        :param img_resolution: tuple of (rows, cols)
        :return: Affine(a, b, xoff, d,e, yoff) (geo transform)
        """
        # scale = 4096
        bounds = (0., 0., img_resolution[1], img_resolution[0])
        (x0, y0, x_max, y_max) = extent
        P = np.array([[x0, x0, x_max], [y0, y_max, y_max], [1, 1, 1]])
        Pd = np.array([[bounds[0], bounds[0], bounds[2]], [bounds[1], bounds[3], bounds[3]], [1, 1, 1]])
        A = np.matmul(P, np.linalg.inv(Pd))
        A = A.reshape(-1)
        # [a, b, d, e, xoff, yoff]
        # a = [A[0], A[1], A[3], A[4], A[2], A[5]]

        return Affine(A[0],A[1],A[2],A[3],A[4],A[5])

    # @classmethod
    # def create_affine_transformation(cls, width, height, bbox):
    #     Istr = '0 %s %s; 0 0 %s; 1 1 1' % (width, width, height)
    #     Imatrix = numpy.matrix(Istr)
    #     Mstr = '%s %s %s;%s %s %s;1 1 1' % (bbox[0], bbox[2], bbox[2], bbox[3], bbox[3], bbox[1])
    #     Mmatrix = numpy.matrix(Mstr)
    #     affine = Imatrix * Mmatrix.getI()
    #     return affine
