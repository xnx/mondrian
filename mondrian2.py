# mondrian2.py

import random

# A very small number for comparing floats properly
EPS = 1.e-12

class Vector:
    """ A lightweight vector class in two-dimensions. """

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, lam):
        """ Multiply the vector by a scalar, lam. """
        return Vector(lam * self.x, lam * self.y)
    def __rmul__(self, lam):
        return self.__mul__(lam)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __neq__(self, other):
        return not self == other
    def __hash__(self):
        """ To keep Vector hashable when we define __eq__, define __hash__. """
        return self.x, self.y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def dot(self, other):
        """ Dot product, a.b = ax.bx + ay.by. """
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        """ z-component of vector cross product, a x b = ax.by - ay.bx. """
        return self.x * other.y - self.y * other.x

class Line:
    """ A simple class representing a line segment between two points in 2D. """
    
    def __init__(self, p, r):
        """
        p is the start point vector, r is the vector from this start point
        to the end point.

        """

        self.p, self.r = p, r

    @classmethod
    def from_endpoints(self, p, q):
        """ Create and return the Line object between points p and q. """

        return Line(p, q-p)

    def __str__(self):
        return '{} -> {}'.format(self.p, (self.p + self.r))

    def intersection(self, other):
        """
        Return the vector to the intersection point between two line segments
        self and other, or None if the lines do not intersect.

        """

        p, r = self.p, self.r
        q, s = other.p, other.r

        rxs = r.cross(s)
        if rxs == 0:
            # Line segments are parallel: no intersection
            return None
        u = (q - p).cross(r) / rxs
        t = (q - p).cross(s) / rxs

        if -EPS <= t <= 1+EPS and -EPS <= u <= 1+EPS:
            # We have an intersection!
            return p + t * r

        # Line segments are not parallel but don't intersect
        return None

    def get_point_on_line(self, u):
        """ Return the vector to the point on the line defined by p + ur. """
        return self.p + u * self.r

    def is_parallel(self, other):
        """ Are the lines self and other parallel? """

        return abs(self.r.cross(other.r)) < EPS

    def is_colinear(self, other):
        """
        Are the lines colinear (have the same start and end points, in either
        order)? """

        return (self.is_parallel(other) and
                abs((self.p - other.p).cross(self.r)) < EPS)

class Polygon:
    """ A small class to represent a polygon in two dimensions. """

    def __init__(self, vertices):
        """
        Define the polygon from an ordered sequence of vertices and get its
        area and edges (as Line objects).

        """

        self.vertices = vertices
        self.n = len(self.vertices)
        self.area = self.get_area()
        self.edges = self.get_edges()

    def get_area(self):
        """ Calculate and return the area of the polygon."""

        # We use the "shoelace" algorithm to calculate the area, since the
        # polygon has no holes or self-intersections.
        s1 = s2 = 0
        for i in range(self.n):
            j = (i+1) % self.n
            s1 += self.vertices[i].x * self.vertices[j].y
            s2 += self.vertices[i].y * self.vertices[j].x
        return abs(s1 - s2) / 2

    def get_edges(self):
        """
        Determine an ordered sequence of edges for the polygon from its
        vertices as a list of Line objects.

        """

        edges = []
        # Indexes of edge endpoints in self.vertices: (0,1), (1,2), ...,
        # (n-2, n-1), (n-1, 0)
        vertex_pair_indices = [(i,(i+1) % self.n) for i in range(self.n)]
        for (i1, i2) in vertex_pair_indices:
            v1, v2 = self.vertices[i1], self.vertices[i2]
            edges.append(Line.from_endpoints(v1, v2))
        return edges

    def split(self, intersections):
        """ Return the two polygons created by splitting this polygon.

        Split the polygon into two polygons at the points given by
        intersections = (i1, p1), (i2, p2)
        where each tuple contains the index of an edge, i, intersected at the
        point, p, by a new line.

        Returns: a list of the new Polygon objects formed.

        """

        (i1, p1), (i2, p2) = intersections
        vertices1 = ([edge.p + edge.r for edge in self.edges[:i1]] +
                     [p1, p2] +
                     [edge.p + edge.r for edge in self.edges[i2:]])
        polygon1 = Polygon(vertices1)
        vertices2 = ([edge.p + edge.r for edge in self.edges[i1:i2]] +
                     [p2, p1])
        polygon2 = Polygon(vertices2)
        return [polygon1, polygon2]

    def __str__(self):
        return ', '.join([str(v) for v in self.vertices])

class Canvas:

    # Fill colours for polygons, and their cumulative probability distribution
    colours = ['blue', 'red', 'yellow', 'white']
    colours_cdf = [0.15, 0.3, 0.45, 1.0]
    def get_colour(self):
        """
        Pick a colour at random using the cumulative probability distribution
        colours_cdf.

        """

        cprob = random.random()
        i = 0
        while Canvas.colours_cdf[i] < cprob:
            i += 1
        return Canvas.colours[i]

    def __init__(self, width, height):
        """ Initialize the canvas with a border around the outside. """

        self.width, self.height = width, height
        self.lines = []

        corners = Vector(0,0), Vector(0,1), Vector(1,1), Vector(1,0)
        self.add_line(Line(corners[0], Vector(0,1)))
        self.add_line(Line(corners[1], Vector(1,0)))
        self.add_line(Line(corners[2], Vector(0,-1)))
        self.add_line(Line(corners[3], Vector(-1,0)))

        self.polygons = {Polygon(corners)}

    def add_line(self, new_line):
        """ Add new_line to the list of Line objects. """
        self.lines.append(new_line)

    def split_polygons(self, new_line):
        """
        Split any Polygons which are intersected exactly twice by new_line.

        Returns the set of "old" Polygons split and a list of the "new"
        Polygons thus formed.

        """
        new_polygons = []
        old_polygons = set()
        for polygon in self.polygons:
            intersections = []
            for i, edge in enumerate(polygon.edges):
                p = new_line.intersection(edge)
                if p:
                    intersections.append((i, p))
            if len(intersections) == 2:
                # this polygon is split into two by the new line
                new_polygons.extend(polygon.split(intersections))
                old_polygons.add(polygon)

        return old_polygons, new_polygons

    def update_polygons(self, old_polygons, new_polygons):
        """
        Update the set of Polygon objects by removing old_polygons and adding
        new_polygons to self.polygons.

        """
        
        self.polygons -= old_polygons
        self.polygons.update(new_polygons)

    def get_new_line(self):
        """ Return a random new line with endpoints on two existing lines. """

        # Get a random point on each of any two different existing lines.
        line1, line2 = random.sample(self.lines, 2)
        start = line1.get_point_on_line(random.random())
        end = line2.get_point_on_line(random.random())
        # Create and return a new line between the points
        return Line.from_endpoints(start, end)

    def get_new_orthogonal_line(self):
        """
        Return a new horizontal or vertical line between two existing lines.

        """

        line1 = random.choice(self.lines)

        def get_xy(line):
            """ Return 'x' for horizontal line or 'y' for vertical line. """
            return 'x' if abs(line.r.y) < EPS else 'y'
        def get_other_xy(xy):
            """ Passed 'x' or 'y', return 'y' or 'x'. """
            return 'y' if xy == 'x' else 'x'

        # Is this a line in parallel to the x-axis or the y-axis?
        xy = get_xy(line1)
        other_xy = get_other_xy(xy)

        start = line1.get_point_on_line(random.random())
        c = getattr(start, xy)
        parallel_lines = []
        for line in self.lines:
            if line.is_colinear(line1):
                continue
            if get_xy(line) != xy:
                # This line is perpendicular to our choice
                continue
            c1, c2 = sorted([getattr(line.p, xy), getattr(line.p+line.r, xy)])
            if not c1 <= c <= c2:
                continue
            parallel_lines.append(line)
        line2 = random.choice(parallel_lines)

        end = Vector(None, None)
        setattr(end, xy, getattr(start, xy))
        setattr(end, other_xy, getattr(line2.p, other_xy))

        return Line.from_endpoints(start, end)

    def make_painting(self, nlines, minarea=None, orthogonal=False):
        """
        Make the "painting" by adding nlines randomly, such that no polygon
        is formed with an area less than minarea. If orthogonal is True,
        only horizontal and vertical lines are used.

        """

        for i in range(nlines):
            while True:
                # Create a new line and split any polygons it intersects
                if orthogonal:
                    new_line = self.get_new_orthogonal_line()
                else:
                    new_line = self.get_new_line()
                old_polygons, new_polygons = self.split_polygons(new_line)

                # If required, ensure that the smallest polygon is at least
                # minarea in area, and go back around if not
                if minarea:
                    smallest_polygon_area = min(polygon.area
                                                for polygon in new_polygons)
                    if smallest_polygon_area >= minarea:
                        break
                else:
                    break

            self.update_polygons(old_polygons, new_polygons)
            self.add_line(new_line)

    def write_svg(self, filename):
        """ Write the image as an SVG file to filename. """

        with open(filename, 'w') as fo:
            print('<?xml version="1.0" encoding="utf-8"?>', file=fo)
            print('<svg xmlns="http://www.w3.org/2000/svg"\n'
                  '    xmlns:xlink="http://www.w3.org/1999/xlink" width="{}"'
                  ' height="{}" >'.format(self.width, self.height), file=fo)
            print("""<defs>

<style type="text/css"><![CDATA[

line {
    stroke: #000;
    stroke-width: 5px;
    fill: none;
}


]]></style>
</defs>""", file=fo)

            for polygon in self.polygons:
                path = []
                for vertex in polygon.vertices:
                    path.append((vertex.x*self.width, vertex.y*self.height))
                s = 'M{},{} '.format(*path[0])
                s += ' '.join(['L{},{}'.format(*path[i])
                                        for i in range(polygon.n)])
                colour = self.get_colour()
                print('<path d="{}" style="fill: {}"/>'.format(s, colour),
                      file=fo)
                    
            for line in self.lines[4:]:
                x1, y1 = line.p.x * self.width, line.p.y * self.height
                x2, y2 = ((line.p + line.r).x * self.width,
                          (line.p + line.r).y * self.height)

                print('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                                        .format(x1,y1,x2,y2), file=fo)

            print('</svg>', file=fo)
