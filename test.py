from ellipse import ColouredPoint, MultiEllipse

# Define the points
P1 = ColouredPoint([0, 500], colour='red')
P2 = ColouredPoint([0, -500], colour='orange')
P3 = ColouredPoint([-1000, 0], colour='purple')
P4 = ColouredPoint([500, 0], colour='green')

# Generate an ellipse for three points
multi_ellipse_three = MultiEllipse([P1, P2, P3], filename='test.svg')
multi_ellipse_three.draw(slack=250)  # Adjust slack as needed

# Generate an ellipse for four points
multi_ellipse_four = MultiEllipse([P1, P2, P3, P4], filename='test.svg')
multi_ellipse_four.draw(slack=300)  # Adjust slack as needed