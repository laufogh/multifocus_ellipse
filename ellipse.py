#!/usr/bin/env python3

# Extending the classical rope-and-pencil ellipse drawing technique to more than 2 foci.
# The generic problem is, given a set of 2D points, make a rope loop around them and the tip of a pencil
# and draw a convex smooth curve around the points with this pencil while keeping the loop taught.
#
# For 3 non-collinear foci the resulting curve is a smooth combination of 6 ellipse fragments.


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

def points_are_clockwise(P1, P2, P3):
    "Detect whether the points are ordered clockwise (1), collinear (0) or counter-clockwise(-1)"
    return  sign((P2[0]-P1[0])*(P3[1]-P1[1])-(P2[1]-P1[1])*(P3[0]-P1[0]))

def draw_ellipsystem(P1, P2, P3, slack=250, show_leftovers=False, show_tickmarks=True, filename="example.svg", canvas_size=(1000,1000), pencil_mark_fraction=None):
    "Draw a system of 6 ellipse fragments that make up the sought-for smooth convex shape"

    dwg             = svgwrite.Drawing(filename=filename, debug=True, size=canvas_size)

    def draw_ellipse_fragment(Pprev, F1, F2, Pnext, d, pencil_mark_fraction=None):
        "Draw an ellipse fragment given two foci, the third point used for cut-off and the length of slack part of the rope attached to the foci"

            # internal absolute measurements of the ellipse (also available to the nested function) :
        c               = distance(F1, F2)/2
        a               = d/2
        b               = math.sqrt( a**2 - c**2 )

        def point_on_the_ellipse(cos_f, focus_sign=-1):
            rho             = b**2 / (a + focus_sign * c * cos_f)
            sin_f           = math.sqrt(1 - cos_f**2)
            x               = rho * cos_f + focus_sign * c
            y               = rho * sin_f
            return (x,y)

            # Translate, rotate and flip the coordinates so that inside the SVG group element
            #  we assume Y grows upwards (a standard mathematical convention),
            #  the ellipse is centered around the origin and the major axis is horizontal:
        tilt_deg        = math.degrees( math.atan2(F2[1]-F1[1], F2[0]-F1[0]) )
        (Cx,Cy)         = midpoint(F1, F2)
        target_group    = dwg.g( stroke=Pnext[2], stroke_width='2', fill='none', transform='translate(%f,%f),rotate(%f,0,0),scale(1,-1)' % (Cx,Cy,tilt_deg) )

            # A and B are start and end points of the ellipse fragment:
        if Pprev:
            cos_for_A       = -three_point_cosine(F2, F1, Pprev)
            cos_for_B       =  three_point_cosine(F1, F2, Pnext)
            clockwise_sign  =  1
        else:
            cos_for_A       = -three_point_cosine(F1, F2, Pnext)
            cos_for_B       =  three_point_cosine(F2, F1, Pnext)
            clockwise_sign  = -1

        (Ax,Ay)     = point_on_the_ellipse( cos_for_A, focus_sign=-clockwise_sign )
        (Bx,By)     = point_on_the_ellipse( cos_for_B, focus_sign= clockwise_sign )

            # visible part of the component ellipse:
        target_group.add( dwg.path( d="M %f,%f A %f,%f 0 0,0 %f,%f" % (Ax, Ay, a, b, Bx, By), stroke_width=4 ) )

            # invisible part of the component ellipse:
        if show_leftovers:
            target_group.add( dwg.path( d="M %f,%f A %f,%f 0 1,1 %f,%f" % (Ax, Ay, a, b, Bx, By), stroke_dasharray='3,7' ) )

        if show_tickmarks:
#            target_group.add( dwg.circle( center=(Ax,Ay), r=12, stroke=F1[2], fill=Pnext[2] ) )    # "from" tick mark
            target_group.add( dwg.circle( center=(Bx,By), r=8,  fill=Pnext[2] ) )     # "to" tick mark

        if pencil_mark_fraction is not None:
                # find the angles relative to F1 in local coordinates:
            gamma   = math.acos( three_point_cosine((c,0), (-c,0), (Ax,Ay)) )
            delta   = math.acos( three_point_cosine((c,0), (-c,0), (Bx,By)) )
                # now we can create any convex combination and map it onto the corresponding ellipse fragment:
            mix     = gamma * (1-pencil_mark_fraction) + delta * pencil_mark_fraction
            (Mx,My) = point_on_the_ellipse( math.cos( mix ) )

            target_group.add( dwg.circle( center=(Mx,My), r=5,     stroke='blue', stroke_width=1, fill='none' ) )    # "mix" tick mark
            target_group.add( dwg.line( start=(-c,0), end=(Mx,My), stroke='blue', stroke_width=1  ) )
            target_group.add( dwg.line( start=( c,0), end=(Mx,My), stroke='blue', stroke_width=1  ) )

        dwg.add( target_group )

    dwg.add( dwg.circle( center=P1[0:2], r=5, stroke=P1[2], stroke_width=2, fill=P1[2] ) )
    dwg.add( dwg.circle( center=P2[0:2], r=5, stroke=P2[2], stroke_width=2, fill=P2[2] ) )
    dwg.add( dwg.circle( center=P3[0:2], r=5, stroke=P3[2], stroke_width=2, fill=P3[2] ) )

    d12             = distance(P1, P2)
    d23             = distance(P2, P3)
    d31             = distance(P3, P1)
    tight_loop      = d12 + d23 + d31

    loop_length     = tight_loop+slack
    draw_ellipse_fragment(P3,   P1, P2, P3, loop_length-d23-d31,  pencil_mark_fraction=pencil_mark_fraction)
    draw_ellipse_fragment(None, P1, P3, P2, loop_length-d31     )
    draw_ellipse_fragment(P1,   P2, P3, P1, loop_length-d12-d31 )
    draw_ellipse_fragment(None, P2, P1, P3, loop_length-d12     )
    draw_ellipse_fragment(P2,   P3, P1, P2, loop_length-d12-d23 )
    draw_ellipse_fragment(None, P3, P2, P1, loop_length-d23     )
    dwg.save()

if __name__ == '__main__':
    P1              = (400, 500, 'red')
    P2              = (600, 400, 'orange')
    P3              = (500, 700, 'green')
    draw_ellipsystem(P1, P2, P3, filename='examples/three_foci_without_leftovers.svg')
    draw_ellipsystem(P1, P2, P3, filename='examples/pencil_mark.svg', pencil_mark_fraction=0.1)
    draw_ellipsystem(P1, P2, P3, show_leftovers=True, filename='examples/three_foci_with_leftovers.svg')
#    draw_ellipsystem(P1, P2, P3, show_tickmarks=False, slacks=[1, 10, 50, 150, 250, 500], filename='examples/three_foci_different_slacks.svg')

