#!/usr/bin/env python3

# Extending the classical rope-and-pencil ellipse drawing technique to more than 2 foci.
# The generic problem is, given a set of 2D points, make a rope loop around them and the tip of a pencil
# and draw a convex smooth curve around the points with this pencil while keeping the loop taught.
#
# For n non-collinear foci the resulting curve is a smooth combination of up to 2*n ellipse fragments.


import math
import svgwrite

def distance(P1, P2):
    "Find the distance between two 2D points"
    return math.sqrt( (P2[0]-P1[0])**2 + (P2[1]-P1[1])**2 )

def midpoint(P1, P2):
    "Find the midpoint of two 2D points"
    return ((P1[0]+P2[0])/2, (P1[1]+P2[1])/2)

def scalar_product(P1, P0, P2):
    "Find the scalar product of P1-P0 and P2-P0 given all the three points (note the order or args)"
    return (P1[0]-P0[0])*(P2[0]-P0[0])+(P1[1]-P0[1])*(P2[1]-P0[1])

def three_point_cosine(P1, P0, P2):
    "Find cosine of the angle between P1-P0 and P2-P0 (note the order of args)"
    return scalar_product(P1, P0, P2)/(distance(P1,P0)*distance(P2,P0))

def sign(x):
    "Amusingly, Python doesn't have a native sign() function"
    return (x>0)-(x<0)

def clockwiseness_of_points(P1, P2, P3):
    "Detect whether the points are ordered clockwise (1), collinear (0) or counter-clockwise(-1)"
    return  sign((P2[0]-P1[0])*(P3[1]-P1[1])-(P2[1]-P1[1])*(P3[0]-P1[0]))

def turn_and_scale(Z, D, cos_f, rho):
    "Relative to centre Z and axis ZD, find the point A in polar coordinates (phi,rho) and map it to Cartesian"

    sin_f       = math.sqrt(abs(1.0 - cos_f**2))    # abs() is needed in the rarest of cases when cos_f *seems* to go over 1.0
    ZD_length   = distance(Z, D)
    U_x         = (D[0]-Z[0])/ZD_length
    U_y         = (D[1]-Z[1])/ZD_length
    A_x         = rho * (  U_x*cos_f + U_y*sin_f ) + Z[0]
    A_y         = rho * ( -U_x*sin_f + U_y*cos_f ) + Z[1]

    return (A_x, A_y)

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

        return math.degrees( math.atan2(self.F2[1]-self.F1[1], self.F2[0]-self.F1[0]) )

    def draw_ellipse_fragment( self, dwg, A, B, tick_parent, show_leftovers=False ):
        "Draw an ellipse fragment given two limits"

        tilt_deg        = self.tilt_deg()

            # visible part of the component ellipse:
        for (stripe_dashoffset, stripe_colour) in ( (10, self.F1[2]), (0, self.F2[2]) ):
            dwg.add( dwg.path( d="M %f,%f A %f,%f %f 0,1 %f,%f" % (A[0], A[1], self.a, self.b, tilt_deg, B[0], B[1]), stroke=stripe_colour, stroke_width=6, stroke_dashoffset=stripe_dashoffset, stroke_dasharray='10,10', fill='none') )

            # remaining, invisible part of the component ellipse:
        if show_leftovers:
            for (stripe_dashoffset, stripe_colour) in ( (0, self.F1[2]), (10, self.F2[2]) ):
                dwg.add( dwg.path( d="M %f,%f A %f,%f %f 1,0 %f,%f" % (A[0], A[1], self.a, self.b, tilt_deg, B[0], B[1]), stroke=stripe_colour, stroke_width=2, stroke_dashoffset=stripe_dashoffset, stroke_dasharray='5,15', fill='none') )

        if tick_parent:
            from_tick   = turn_and_scale(B, tick_parent, 1,  10)
            to_tick     = turn_and_scale(B, tick_parent, 1, -10)
            dwg.add( dwg.line( start=from_tick, end=to_tick, stroke=tick_parent[2], fill=tick_parent[2], stroke_width=6, stroke_linecap='round' ) )

    def draw_a_pencil_mark( self, dwg, A, B, pencil_mark_fraction ):
        "Draw a pencil mark given a fraction 0..1 that defines the convex combination"

            # find the angles relative to ellipse.F1 in local coordinates:
        gamma   = math.acos( three_point_cosine(self.F2, self.F1, (A[0],A[1])) )
        delta   = math.acos( three_point_cosine(self.F2, self.F1, (B[0],B[1])) )
            # now we can create any convex combination and map it onto the corresponding ellipse fragment:
        mix     = gamma * (1-pencil_mark_fraction) + delta * pencil_mark_fraction
        (Mx,My) = point_on_the_ellipse( math.cos( mix ) )

        dwg.add( dwg.circle( center=(Mx,My), r=5,     stroke='blue', stroke_width=1, fill='none' ) )    # "mix" tick mark
        dwg.add( dwg.line( start=self.F1[0:2], end=(Mx,My), stroke='blue', stroke_width=1  ) )
        dwg.add( dwg.line( start=self.F2[0:2], end=(Mx,My), stroke='blue', stroke_width=1  ) )


def draw_ellipsystem(P, slacks=[250], show_leftovers=False, show_tickmarks=True, filename="example.svg", canvas_size=(1000,1000), pencil_mark_fraction=None):
    "Draw a simplified system of 2*len(P) ellipse fragments that make up the sought-for smooth convex shape"

    dwg         = svgwrite.Drawing(filename=filename, debug=True, size=canvas_size)

    dist_2_prev = []
    n           = len(P)
    for i in range(n):
        dwg.add( dwg.circle( center=P[i][0:2], r=5, stroke=P[i][2], stroke_width=2, fill=P[i][2] ) )
        dist_2_prev.append( distance(P[i], P[i-1]) )

    for slack in slacks:
            # find the first proper fragment:
        l       = 0
        l_next  = 1
        r       = 1
        d       = slack
        while True:
            d              += dist_2_prev[r]
            r_next          = (r+1) % n
            ellipse         = Ellipse(P[l], P[r], d)
            cos_for_A       = -three_point_cosine(P[r], P[l], P[l-1])
            A               = ellipse.point_on_the_ellipse( cos_for_A, focus_sign=-1 )
            if clockwiseness_of_points(A, P[r], P[r_next])==1:
                break
            else:
                r   = r_next

            # walk over all the fragments until we attempt to create the first fragment again:
        while l!=0 or l_next!=0:
            ellipse         = Ellipse(P[l], P[r], d)
            l_next          = (l+1) % n
            r_next          = (r+1) % n
            cos_for_B       =  three_point_cosine(P[l], P[r], P[r_next])
            B               = ellipse.point_on_the_ellipse( cos_for_B, focus_sign=1 )
            cos_of_B_rel_F1 =  three_point_cosine(B, P[l], P[r])

            cos_for_A2      =  three_point_cosine(P[r], P[l], P[l_next])
            A2              = ellipse.point_on_the_ellipse( cos_for_A2, focus_sign=-1 )

                # compare two right limit candidates and choose the one with greater angle => smaller cosine:
            if cos_for_A2 < cos_of_B_rel_F1:
                B   = A2
                l   = l_next
                d  -= dist_2_prev[l]
                tick_parent = P[l]
            else:
                tick_parent = P[r]
                r   = r_next
                d  += dist_2_prev[r]

            if not show_tickmarks:
                tick_parent = False

            ellipse.draw_ellipse_fragment( dwg, A, B, tick_parent, show_leftovers=show_leftovers )
            A   = B     # next iteration inherits the current one's right limit for its left

    dwg.save()

if __name__ == '__main__':
    P1              = (400, 500, 'red')
    P2              = (600, 400, 'orange')
    P3              = (600, 700, 'purple')
    P4              = (500, 700, 'green')
    draw_ellipsystem([P1, P2, P4], filename='examples/three_foci_without_leftovers.svg')
    draw_ellipsystem([P1, P2, P4], show_leftovers=True, filename='examples/three_foci_with_leftovers.svg')
    draw_ellipsystem([P1, P2, P3, P4], filename='examples/four_foci_without_leftovers.svg')
    draw_ellipsystem([P1, P2, P3, P4], show_leftovers=True, filename='examples/four_foci_with_leftovers.svg')

    draw_ellipsystem([ (400,400,'red'), (600,400,'orange'), (700,450,'yellow'), (650,520,'green'), (530,620,'cyan'),
                       (450,600,'blue'), (380,520,'purple')
                     ], slacks=[25, 50, 100, 200, 400], show_tickmarks=True, filename='examples/seven_foci_different_slacks.svg')

#    draw_ellipsystem([P1, P2, P4], filename='examples/pencil_mark.svg', pencil_mark_fraction=0.1)

