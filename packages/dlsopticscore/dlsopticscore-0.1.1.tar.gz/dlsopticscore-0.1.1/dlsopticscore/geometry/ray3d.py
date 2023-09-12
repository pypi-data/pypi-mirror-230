class Ray3D:
    def __init__(self, point, vector):
        self.point = point
        self.vector = vector.toLength(1)

    def __repr__(self):
        return 'Ray3D({}, {})'.format(self.point, self.vector)