# multifocus_ellipse

Extending the classical rope-and-pencil ellipse drawing technique to more than 2 foci.
The generic problem is, given a set of 2D points, make a rope loop around them and the tip of a pencil
and draw a convex smooth curve around the points with this pencil while keeping the loop taught.

For 3 non-collinear foci the resulting curve is a smooth combination of 6 ellipse fragments:

![Three-foci ellipse example](examples/three_foci_example.svg "Three-foci ellipse example")

