import random
import numpy as np

HORIZONTAL, VERTICAL = True, False

class Mondrian:

    # Fill colours for boxes, and their cumulative probability distribution
    colours = ['blue', 'red', 'yellow', 'white']
    colours_cdf = [0.15, 0.3, 0.45, 1.0]

    def __init__(self, config={}, seed=None):
    
        random.seed(seed)

        self.config = {'width': 800, 'height': 600,
                        # Don't let parallel lines get closer the following
                        # number of pixels
                       'padding': 20,
                       'nlines': 25
                      }

        self.config.update(config)
        self.width, self.height = self.config['width'], self.config['height']
        self.nlines = self.config['nlines']
        self.padding = self.config['padding']
        self.tol = {HORIZONTAL: self.padding/self.width,
                    VERTICAL: self.padding / self.height}
        # Dictionary of lines horizontal and vertical lines: given as
        # (y, (x1, x2)) and (x, (y1, y2)) values respectively.
        self.lines = {
                      HORIZONTAL: [(0, (0,1)), (1, (0,1))],
                      VERTICAL: [(0, (0,1)), (1, (0,1))]
                     }


    def get_colour(self):
        """
        Pick a colour at random using the cumulative probability distribution
        colours_cdf.

        """

        cprob = random.random()
        i = 0
        while self.colours_cdf[i] < cprob:
            i += 1
        return self.colours[i]

    def too_close(self, parpos, parlines, orientation):
        """
        Return True if the proposed partition is too close to any parallel
        line.

        """

        return any([abs(parpos-line[0]) < self.tol[orientation]
                                            for line in parlines])

    def choose_endpoints(self, parpos, perplines):
        """
        Randomly pick two points on the perpendicular line set to start and
        end our new line on.

        """

        intersecting_lines = [line for line in perplines
                                if line[1][0] < parpos < line[1][1] ]
        endpoints = sorted(random.sample(
                [line[0] for line in intersecting_lines], 2))
        return endpoints

    def get_orientation(self):
        """
        Get a random orientation (HORIZONTAL or VERTICAL) for the next line.
        But if the previous two lines have the same orientation, change it
        for this next line.

        """

        if (len(self.orientations) > 1 and
                self.orientations[-1]==self.orientations[-2]): 
            orientation = not self.orientations[-1]
        else:
            orientation = random.choice((HORIZONTAL, VERTICAL))
        self.orientations.append(orientation)
        return orientation

    def add_lines(self):
        """
        Add self.nlines lines to the picture, in random orientations.

        """

        self.orientations = []
        for line in range(self.nlines):
            orientation = self.get_orientation()
            perp_orientation = not orientation
            while True:
                parpos = random.random()
                if not self.too_close(parpos, self.lines[orientation],
                            orientation):
                    break
            # Randomly choose endpoints from available perpendicular lines
            endpoints = self.choose_endpoints(parpos,
                                            self.lines[perp_orientation])
            self.lines[orientation].append((parpos, endpoints))

        self.lines[HORIZONTAL].sort()
        self.lines[VERTICAL].sort()

    def get_boxes(self):
        """
        Find the "boxes" delimited by our lines. Each box is defined by the
        four coordinates (bx1, by1, bx2, by2) where (bx1, by1) is the lower
        lefthand corner and (bx2, by2) is the upper righthand corner.

        """

        self.boxes = []
        # Loop over the horizontal lines (up to the second from the top)
        for i, (y, (x1, x2)) in enumerate(self.lines[HORIZONTAL][:-1]):
            by1 = y
            # Find the vertical lines which intersect this horizontal line
            for j, (x, (y1, y2)) in enumerate(self.lines[VERTICAL][:-1]):
                if x >= x2:
                    # All subsequent lines are beyond the end of our
                    #mhorizontal line
                    break
                if x < x1 or y1 > y or y2 <= y:
                    # The intersecting line must have its upper end (y2)
                    # beyond y
                    continue
                bx1 = x
                # Find the right hand vertical side of the box
                for (xr1, (yr1, yr2)) in self.lines[VERTICAL][j+1:]:
                    if yr1 <= y < yr2:
                        # Success: the vertical line intersects and extends
                        # "higher" than y
                        break
                bx2 = xr1

                # Finally, find the upper horizontal edge of the box: this
                # isn't necessarily the next horizontal line in the list!
                for (yu, (xu1, xu2)) in self.lines[HORIZONTAL][i+1:]:
                    if xu1 <= bx1 and xu2 >= bx2:
                        by2 = yu
                        break
                
                self.boxes.append((bx1, by1, bx2, by2))

    def make_svg(self):
        svg = ['<?xml version="1.0" encoding="utf-8"?>',
               '<svg xmlns="http://www.w3.org/2000/svg"',
               ' xmlns:xlink="http://www.w3.org/1999/xlink" width="{}"'
               ' height="{}" >'.format(self.width, self.height),
               '<defs>',
               '    <style type="text/css"><![CDATA[',
               '        line {',
               '        stroke: #000;',
               '        stroke-width: 5px;',
               '        }',
               '    ]]></style>'
               '</defs>']

        # First add the boxes
        for box in self.boxes:
            x1, x2 = box[0]*self.width, box[2]*self.width
            y1, y2 = box[1]*self.height, box[3]*self.height

            box_width, box_height = x2 - x1, y2 - y1
            colour = self.get_colour()
            svg.append('<rect x="{}" y="{}" width="{}" height="{}"'
                       ' style="fill: {}"/>'.format(x1, y1, box_width,
                                                   box_height, colour)
                      )

        # Draw the lines over the boxes
        for orientation in (HORIZONTAL, VERTICAL):
            # NB miss off the outside border
            for line in self.lines[orientation][1:-1]:
                y1 = y2 = line[0]
                x1, x2 = line[1]
                if orientation == VERTICAL:
                    x1,x2, y1,y2 = y1,y2, x1,x2
                x1, x2 = x1*self.width, x2*self.width
                y1, y2 = y1*self.height, y2*self.height
                svg.append('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                                .format(x1,y1,x2,y2))

        svg.append('</svg>')
        return '\n'.join(svg)

    def write_svg(self, filename):
        svg = self.make_svg()
        with open(filename, 'w') as fo:
            fo.write(svg)

    def make_painting(self):
        self.add_lines()
        self.get_boxes()
