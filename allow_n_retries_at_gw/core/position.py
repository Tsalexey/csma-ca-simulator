import numpy


class Position:
    def __init__(self, radius):
        phi = round(numpy.random.uniform(0.0, 2 * numpy.math.pi), 6)
        cos_theta = round(numpy.random.uniform(-1.0, 1.0), 6)
        u = round(numpy.random.uniform(0.0, 1.0), 6)
        theta = numpy.arccos(cos_theta)
        r = radius * numpy.cbrt(u)

        self.x = r * numpy.sin(theta) * numpy.cos(phi)
        self.y = r * numpy.sin(theta) * numpy.sin(phi)
        self.z = r * numpy.cos(theta)
