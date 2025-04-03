from ellipse import ColouredPoint, MultiEllipse
import matplotlib.pyplot as plt

# Define the points
# P1 = ColouredPoint([0, 500], colour='red')
# P2 = ColouredPoint([0, -500], colour='orange')
# P3 = ColouredPoint([-500, 0], colour='blue')
# P4 = ColouredPoint([500, 0], colour='green')

# P1              = ColouredPoint( [400, 500], colour='red' )
# P2              = ColouredPoint( [600, 400], colour='orange' )
# P3              = ColouredPoint( [600, 700], colour='purple' )
# P4              = ColouredPoint( [500, 700], colour='green' )

correction_x = 500
correction_y = 500

P1 = ColouredPoint([-200+correction_x, 0+correction_y], colour='red')
P2 = ColouredPoint([200+correction_x, -30+correction_y], colour='orange')
P3 = ColouredPoint([250+correction_x, 0+correction_y], colour='blue')
P4 = ColouredPoint([200+correction_x,90+correction_y],colour='green')

# Generate an ellipse for four points
multi_ellipse_four = MultiEllipse([P1, P2, P3, P4], filename='test.svg')

multi_ellipse_four.draw(slack=10)
points_four = multi_ellipse_four.get_points()  # Get the points as a list

# Plot the points for four foci
x_four, y_four = zip(*points_four)  # Unpack the x and y coordinates
plt.figure(figsize=(8, 8))
plt.plot(x_four, y_four, label="Four Foci", color="green")
plt.scatter([P1[0], P2[0], P3[0], P4[0]], [P1[1], P2[1], P3[1], P4[1]], color=["red", "orange", "blue", "green"], label="Foci")
plt.title("Multi-Focus Ellipse with Four Foci")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)
plt.show()
