#!/usr/bin/env python3

# Extending the classical rope-and-pencil ellipse drawing technique to more than 2 foci.
# The generic problem is, given a set of 2D points, make a rope loop around them and the tip of a pencil
# and draw a convex smooth curve around the points with this pencil while keeping the loop taught.
#
# For n non-collinear foci the resulting curve is a smooth combination of up to 2*n ellipse fragments.


import math
import svgwrite
import re
import os
import numpy as np

class ColouredPoint(np.ndarray):
    "A (numpy) point that has both coordinates and colour"

    def __new__(cls, input_array, colour='grey'):
        coloured_point = np.asarray(input_array).view(cls)
        coloured_point.colour = colour
        return coloured_point

    def __array_finalize__(self, coloured_point):
        if coloured_point is None: return
        self.info = getattr(coloured_point, 'colour', None)

def distance(P1, P2):
    "Find Euclidean distance between two points"
    return np.linalg.norm(P2-P1)

def three_point_cosine(P1, P0, P2):
    "Find cosine of the angle between P1-P0 and P2-P0 (note the order of args)"
    return np.dot(P1-P0, P2-P0)/(distance(P1,P0)*distance(P2,P0))

def clockwiseness_of_points(P1, P2, P3):
    "Detect whether the points are ordered clockwise (1), collinear (0) or counter-clockwise(-1)"
    return  np.sign(np.linalg.norm(np.cross(P2-P1,P3-P1)))

def rintvec(vector):
    "By-component rounding of a vector"
    return map(int, map(round, vector))

def turn_and_scale(Z, D, cos_f, rho):
    "Relative to centre Z and axis ZD, find the point A in polar coordinates (phi,rho) and map it to Cartesian"

    sin_f       = math.sqrt(abs(1.0 - cos_f**2))    # abs() is needed in the rarest of cases when cos_f *seems* to go over 1.0
    U           = (D-Z)/distance(Z, D)              # unit vector in the original direction relative to Z
    A           = rho * np.dot(U , [[cos_f, -sin_f], [sin_f, cos_f]]) + Z
    return A

class Ellipse:
    "Computes and stores parameters of the ellipse and provides some helper geometry methods"

    def __init__(self, F1, F2, d):
        self.F1 = F1
        self.F2 = F2
        self.c  = distance(F1, F2)/2
        self.a  = d/2
        self.b  = math.sqrt( self.a**2 - self.c**2 )

    def point_on_the_ellipse(self, cos_f, focus_sign=-1):
        "Return a Cartesian point on the ellipse given polar cosine; focus_sign==-1|1 means relative to first|second focus"

        rho     = self.b**2 / (self.a + focus_sign * self.c * cos_f)
        (Z, D)  = (self.F1, self.F2) if focus_sign==-1 else (self.F2, self.F1)
        return turn_and_scale(Z, D, cos_f, -focus_sign*rho)

    def tilt_deg(self):
        "Return the tilt of the ellipse in degrees"

        diff = self.F2-self.F1
        return math.degrees( math.atan2(diff[1], diff[0]) )

    def draw_ellipse_fragment( self, dwg, A, B, tick_parent, show_leftovers=False ):
        "Draw an ellipse fragment given two limits"

        tilt_deg        = self.tilt_deg()

            # visible part of the component ellipse:
        for (stripe_dashoffset, stripe_colour) in ( (10, self.F1.colour), (0, self.F2.colour) ):
            dwg.add( dwg.path( d="M %f,%f A %f,%f %f 0,1 %f,%f" % (A[0], A[1], self.a, self.b, tilt_deg, B[0], B[1]), stroke=stripe_colour, stroke_width=6, stroke_dashoffset=stripe_dashoffset, stroke_dasharray='10,10', fill='none') )

            # remaining, invisible part of the component ellipse:
        if show_leftovers:
            for (stripe_dashoffset, stripe_colour) in ( (0, self.F1.colour), (10, self.F2.colour) ):
                dwg.add( dwg.path( d="M %f,%f A %f,%f %f 1,0 %f,%f" % (A[0], A[1], self.a, self.b, tilt_deg, B[0], B[1]), stroke=stripe_colour, stroke_width=2, stroke_dashoffset=stripe_dashoffset, stroke_dasharray='5,15', fill='none') )

        if tick_parent is not None:
            from_tick   = turn_and_scale(B, tick_parent, 1,  10)
            to_tick     = turn_and_scale(B, tick_parent, 1, -10)
            dwg.add( dwg.line( start=rintvec(from_tick), end=rintvec(to_tick), stroke=tick_parent.colour, fill=tick_parent.colour, stroke_width=6, stroke_linecap='round' ) )

    def draw_a_pencil_mark( self, dwg, A, B, pencil_mark_fraction ):
        "Draw a pencil mark given a fraction 0..1 that defines the convex combination"

            # find the angles relative to ellipse.F1 in local coordinates:
        gamma   = math.acos( three_point_cosine(self.F2, self.F1, A) )
        delta   = math.acos( three_point_cosine(self.F2, self.F1, B) )
            # now we can create any convex combination and map it onto the corresponding ellipse fragment:
        mix     = gamma * (1-pencil_mark_fraction) + delta * pencil_mark_fraction
        M       = self.point_on_the_ellipse( math.cos( mix ) )

        dwg.add( dwg.circle( center=M, r=5,     stroke='blue', stroke_width=1, fill='none' ) )    # "mix" tick mark
        dwg.add( dwg.line( start=rintvec(self.F1.tolist()), end=rintvec(M), stroke='blue', stroke_width=1  ) )
        dwg.add( dwg.line( start=rintvec(self.F2.tolist()), end=rintvec(M), stroke='blue', stroke_width=1  ) )


class MultiEllipse:
    "Stores parameters of a MultiEllipse and provides a method to draw it"

    def __init__(self, P, show_leftovers=False, show_tickmarks=True, filename="example.svg", canvas_size=(1000, 1000)):
        self.P              = P
        self.show_leftovers = show_leftovers
        self.show_tickmarks = show_tickmarks
        self.filename       = filename
        self.canvas_size    = canvas_size
        self.dist_2_prev    = []
        self.n              = len(P)
        self.points_on_curve = []  # Add a list to store the computed points
        for i in range(self.n):
            self.dist_2_prev.append( distance(P[i], P[i-1]) )

    def draw_foci(self, fragment_index=0):
        "Create the Drawing object and draw the foci"

        filename    = (self.filename % fragment_index) if re.search('%', self.filename) else self.filename
        self.dwg    = svgwrite.Drawing(filename=filename, size=self.canvas_size, debug=True)

        print("Creating %s ..." % filename)

        for i in range(self.n):
            self.dwg.add( self.dwg.circle( center=self.P[i].tolist(), r=5, stroke=self.P[i].colour, stroke_width=2, fill=self.P[i].colour ) )

    def draw_rest_of_rope(self, l, r):
        "Draw the rest of the rope loop (between P[r] and P[l])"

        for i in range(r-self.n if l<r else r, l):
            self.dwg.add( self.dwg.line( start=rintvec(self.P[i].tolist()), end=rintvec(self.P[i+1].tolist()), stroke='blue', stroke_width=1  ) )

    def draw_with_slack(self, slack, pencil_mark_fragment=-1, pencil_mark_fraction=0.1):
        "Draw a system of 2*len(P) ellipse fragments that make up the sought-for smooth convex shape"

            # find the first proper fragment:
        l       = 0
        l_next  = 1
        r       = 1
        d       = slack
        while True:
            d              += self.dist_2_prev[r]
            r_next          = (r+1) % self.n
            ellipse         = Ellipse(self.P[l], self.P[r], d)
            cos_for_A       = -three_point_cosine(self.P[r], self.P[l], self.P[l-1])
            A               = ellipse.point_on_the_ellipse( cos_for_A, focus_sign=-1 )
            if clockwiseness_of_points(A, self.P[r], self.P[r_next])==1:
                break
            else:
                r   = r_next

        fragments   = 0

            # walk over all the fragments until we attempt to create the first fragment again:
        while l != 0 or l_next != 0:
            if pencil_mark_fragment == fragments:
                self.draw_rest_of_rope(l, r)

            ellipse = Ellipse(self.P[l], self.P[r], d)
            l_next = (l + 1) % self.n
            r_next = (r + 1) % self.n
            cos_for_B = three_point_cosine(self.P[l], self.P[r], self.P[r_next])
            B = ellipse.point_on_the_ellipse(cos_for_B, focus_sign=1)
            cos_of_B_rel_F1 = three_point_cosine(B, self.P[l], self.P[r])

            cos_for_A2 = three_point_cosine(self.P[r], self.P[l], self.P[l_next])
            A2 = ellipse.point_on_the_ellipse(cos_for_A2, focus_sign=-1)

                # compare two right limit candidates and choose the one with greater angle => smaller cosine:
            if cos_for_A2 < cos_of_B_rel_F1:
                B = A2
                l = l_next
                d -= self.dist_2_prev[l]
                tick_parent = self.P[l]
            else:
                tick_parent = self.P[r]
                r = r_next
                d += self.dist_2_prev[r]

            if not self.show_tickmarks:
                tick_parent = None

            # Store the computed points A and B
            self.points_on_curve.append(A.tolist())
            self.points_on_curve.append(B.tolist())

            ellipse.draw_ellipse_fragment(self.dwg, A, B, tick_parent, show_leftovers=self.show_leftovers)
            if pencil_mark_fragment == fragments:
                ellipse.draw_a_pencil_mark(self.dwg, A, B, pencil_mark_fraction)

            fragments += 1
            A = B  # Next iteration inherits the current one's right limit for its left

        return fragments

    def get_points(self):
        "Return the computed points on the curve as a list"
        return self.points_on_curve

    def draw(self, slack=250):

        self.draw_foci()
        self.draw_with_slack(slack=slack)
        self.dwg.save()

    def draw_parallel(self, slacks):

        self.draw_foci()

        for slack in slacks:
            self.draw_with_slack(slack)

        self.dwg.save()

    def draw_with_pencil_marks(self, slack=250):

        self.draw_foci(0)
        fragments = self.draw_with_slack(slack=slack)
        self.dwg.save()

        subfragments    = 10

        for fragment_index in range(fragments):
            for subfragment_index in range(subfragments):
                combined_index = fragment_index * subfragments + subfragment_index + 1
                self.draw_foci(combined_index)
                self.draw_with_slack(slack=slack, pencil_mark_fragment=fragment_index,
                                     pencil_mark_fraction=(subfragment_index+0.5)/subfragments)
                self.dwg.save()


def create_drawings(directory):
    "To recreate all the example drawings manually, run create_drawings('examples')"

    P1              = ColouredPoint( [400, 500], colour='red' )
    P2              = ColouredPoint( [600, 400], colour='orange' )
    P3              = ColouredPoint( [600, 700], colour='purple' )
    P4              = ColouredPoint( [500, 700], colour='green' )

    MultiEllipse([P1, P2, P4], filename=directory+'/three_foci_without_leftovers.svg').draw()
    MultiEllipse([P1, P2, P4], show_leftovers=True, filename=directory+'/three_foci_with_leftovers.svg').draw()
    MultiEllipse([P1, P2, P3, P4], filename=directory+'/four_foci_without_leftovers.svg').draw()
    MultiEllipse([P1, P2, P3, P4], show_leftovers=True, filename=directory+'/four_foci_with_leftovers.svg').draw()
    MultiEllipse([
            ColouredPoint( [400,400], colour='red'),
            ColouredPoint( [600,400], colour='orange'),
            ColouredPoint( [700,450], colour='yellow'),
            ColouredPoint( [650,520], colour='green'),
            ColouredPoint( [530,620], colour='cyan'),
            ColouredPoint( [450,600], colour='blue'),
            ColouredPoint( [380,520], colour='purple')
        ], show_tickmarks=True, filename=directory+'/seven_foci_different_slacks.svg').draw_parallel([25, 50, 100, 200, 400])

    # MultiEllipse([P1, P2, P4], filename='pencil_mark_%02d.svg').draw_with_pencil_marks()
    # os.system('convert -loop 0 -dispose Background -delay 5 pencil_mark_*.svg running_pencil_animation.gif')

