from scipy.interpolate import BSpline
import numpy as np


class Spline2D:
    def __init__(self, cv, degree=3):
        """Create a B-Spline for 2D control points. Only first and last point are matched exactly.
        Range for evaluation will go from first control point to last control point.
        For degree 3 need at least *four* control points.

        Args:
            cv (_type_): Array of control points
            degree (int, optional): Curve degree. Defaults to 3.
        """
        cv = np.asarray(cv)
        self.count = cv.shape[0]
        self.degree = degree

        cx, cy = cv[:, 0], cv[:, 1]

        # Calculate uniform clamped knot vector, curve ends at first and last control points
        kv = np.array(
            [0] * self.degree
            + list(range(self.count - self.degree + 1))
            + [self.count - self.degree] * self.degree,
            dtype="int",
        )

        # Create two BSpline, one for each dimension
        self.bspline_x = BSpline(kv, cx, degree)
        self.bspline_y = BSpline(kv, cy, degree)

        self.bspline_x_derivative = self.bspline_x.derivative(nu=1)
        self.bspline_y_derivative = self.bspline_y.derivative(nu=1)

    def evaluate(self, x):
        # x between [0,1]
        u = x * (self.count - self.degree)
        return self.bspline_x(u), self.bspline_y(u)

    def evaluate_with_tangent(self, x):
        u = x * (self.count - self.degree)
        # return tangent as angle
        angle = np.arctan(self.bspline_y_derivative(u), self.bspline_x_derivative(u))
        return self.bspline_x(u), self.bspline_y(u), angle

    def evaluate_range(self, samples=100):
        # Calculate query range
        u = np.linspace(0, (self.count - self.degree), samples)

        # Evaluate bsplines at query range
        x = self.bspline_x(u)
        y = self.bspline_y(u)

        return x, y
