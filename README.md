# multifocus_ellipse

Extending the [classical pins-string-and-pencil ellipse drawing technique](https://www.youtube.com/watch?v=0maahsJQOJE&t=30) to more than 2 foci.
The generic problem is, given a set of 2D points, make a string loop around them and the tip of a pencil
and trace a convex smooth curve around the points with this pencil while keeping the loop taught.

For 3 non-collinear foci the resulting curve looks like this:
![Three-foci ellipse example](examples/three_foci_without_leftovers.svg "Three-foci ellipse example")

It is in fact a smooth combination of 6 elliptical fragments, each built on just two foci out of three:
![Three-foci ellipse with leftovers](examples/three_foci_with_leftovers.svg "Three-foci ellipse with leftovers")

Animation of a running pencil in a string loop:
![Three-foci pencil animation](examples/running_pencil_animation.gif "Three-foci pencil animation")

For 4 non-collinear foci the resulting curve looks like this:
![Four-foci ellipse example](examples/four_foci_without_leftovers.svg "Four-foci ellipse example")

It is a smooth combination of 8 elliptical fragments, each built on two foci out of four:
![Four-foci ellipse with leftovers](examples/four_foci_with_leftovers.svg "Four-foci ellipse with leftovers")

The following drawing shows the effect of different amount of slack in the loop, ranging from "almost a polygon" to "almost a circle":
![Multi-focus ellipses with different slacks](examples/seven_foci_different_slacks.svg "Multi-focus ellipses with different slacks")

