# multifocus_ellipse

Extending the [classical pins-string-and-pencil ellipse drawing technique](https://www.youtube.com/watch?v=0maahsJQOJE&t=30) to more than 2 foci.
The generic problem is, given a set of 2D points, make a string loop around them and the tip of a pencil
and trace a convex smooth curve around the points with this pencil while keeping the loop taught.

For 3 non-collinear foci the resulting curve is a smooth combination of 6 ellipse fragments:

![Three-foci ellipse example](examples/three_foci_example.svg "Three-foci ellipse example")

