from optics.geometry import Ray3D


class Plane:
    def __init__(self, *args):
        if len(args) == 2:
            # assume we have a point and vector
            self.point = args[0]
            self.normal = args[1]
        elif len(args) == 3:
            # assume we have 3 points
            v1 = args[2] - args[1]
            v2 = args[1] - args[0]
            normal = v1.cross(v2)
            self.point = args[0]
            self.normal = normal.toLength(1)

        self.d = -(self.normal.dot(self.point))

        # if self.d < 0:
        #     self.normal *= -1

    def intersect(self, other):
        if isinstance(other, Ray3D):
            # https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python
            epsilon = 1e-6
            ndotu = self.normal.dot(other.vector)

            if abs(ndotu) < epsilon:
                raise RuntimeError("no intersection or line is within plane")

            w = other.point - self.point
            si = -self.normal.dot(w) / ndotu
            Psi = w + si * other.vector + self.point
            return Psi

    def __repr__(self):
        return 'Plane({}, {})'.format(self.point, self.normal)
