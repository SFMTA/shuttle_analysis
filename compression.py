class Position:

    def __init__(self, x, y, time, id):
        self.x = x
        self.y = y
        self.time = time
        self.id = id

    def __str__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ','.join([str(self.x),
                      str(self.y),
                      str(self.time), self.id]))

    __repr__ = __str__


class Line:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def distance_to_point(self, point):
        return (abs((self.p2.y - self.p1.y)*point.x
                    - (self.p2.x - self.p1.x)*point.y
                    + self.p2.x * self.p1.y
                    - self.p2.y * self.p1.x)
                / ((self.p2.x - self.p1.x) ** 2
                   + (self.p2.y - self.p1.y) ** 2)) ** 0.5


DEFAULT_DOUGLAS_PEUCKER_EPSILON = 0.5


def douglas_peucker(points, epsilon=DEFAULT_DOUGLAS_PEUCKER_EPSILON):
    """Compress a list of positions based on a characteristic distance

    Parameters
    ----------
    points : List of Positions
        Positions to compress
    epsilon : float
        Characteristic distance with which to compress positions
    """
    start_point = points[0]
    end_point = points[-1]

    line = Line(start_point, end_point)

    max_point = max(points, key=line.distance_to_point)
    max_distance = line.distance_to_point(max_point)
    if max_distance > epsilon:
        furthest_index = points.index(max_point)
        return list(set(douglas_peucker(points[0:furthest_index+1], epsilon)
                        + douglas_peucker(points[furthest_index:], epsilon)))
    else:
        return [start_point, end_point]


class Path:

    def __init__(self, points, compression=douglas_peucker):
        self.points = compression(points)

    def position_at_time(self, time, id):
        pass
