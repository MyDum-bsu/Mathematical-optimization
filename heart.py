from manim import *
from manim.utils.color.XKCD import PINKY, PINKYRED
from scipy.optimize import fsolve

a = 2
b = 1
h = np.sqrt(a ** 2 - b ** 2)
c = a + b

num_lines = 500

num_radial_curves = 33
max_curve_radius = a * 0.8

angle_step = TAU / num_lines

start_stroke = 3

br_step = 1 / num_lines * 1.2
st_step = start_stroke / num_lines

SECTOR_COLOR = '#1f1c17'
CURVE_COLOR = '#7e4706'
LINES_COLOR = WHITE
MAIN_COLOR = BLACK
heart_scale = 1.8


def find_circle_point(alpha, invert_x):
    discriminant = a ** 2 - b ** 2 * np.sin(alpha) ** 2
    t1 = invert_x * b * np.cos(alpha) - np.sqrt(discriminant)
    t2 = invert_x * b * np.cos(alpha) + np.sqrt(discriminant)
    t = max(t1, t2)
    x, y = t * np.cos(alpha), t * np.sin(alpha)
    return np.array([x, y, 0])


def find_heart_point(alpha, k=heart_scale):
    tan_alpha = np.tan(alpha)

    def equation(x):
        return (1 + tan_alpha ** 2) * x ** 2 - 2 * x ** 1.5 * tan_alpha + x*np.sqrt(k) - k**2

    x_solutions = fsolve(equation, [0.5])

    # x_solutions = [x for x in x_solutions if x >= 0]
    x = x_solutions[0]
    left_point = np.array([-x, x * tan_alpha, 0])
    right_point = np.array([x, x * tan_alpha, 0])

    return left_point, right_point


def draw_right_lines():
    first_lines = VGroup()
    stroke = start_stroke
    brightness = 1

    flag = True
    for alpha in np.arange(PI / 2, -3 * PI / 2, -angle_step):
        left_heart_point, right_heart_point = find_heart_point(alpha)

        left_circle_point = find_circle_point(alpha, -1)
        right_circle_point = find_circle_point(alpha, 1)

        if 0 <= alpha <= PI / 2:
            if flag and right_circle_point[1] < right_heart_point[1]:
                continue
            else:
                flag = False

            first_lines.add(
                Line(right_heart_point, right_circle_point, color=MAIN_COLOR, stroke_width=stroke,
                     stroke_opacity=brightness))

        elif -PI / 2 <= alpha < 0:
            end_x = c * np.cos(alpha)
            end_y = c * np.sin(alpha)
            end_point = np.array([end_x, end_y, 0])
            x, y = 10 * np.cos(alpha), 10 * np.sin(alpha)
            first_lines.add(
                Line(end_point, np.array([x, y, 0]), color=LINES_COLOR, stroke_width=0.7, stroke_opacity=1))
            first_lines.add(
                Line(right_heart_point, end_point, color=MAIN_COLOR, stroke_width=stroke, stroke_opacity=brightness))

        elif -PI <= alpha < - PI / 2:
            end_x = c * np.cos(alpha)
            end_y = c * np.sin(alpha)
            end_point = np.array([end_x, end_y, 0])
            first_lines.add(
                Line(left_circle_point, end_point, color=MAIN_COLOR, stroke_width=stroke, stroke_opacity=brightness))

        brightness -= br_step
        stroke -= st_step
    return first_lines


def draw_left_lines():
    second_lines = VGroup()
    stroke = start_stroke
    brightness = 1

    for alpha in np.arange(-PI / 2, -TAU, -angle_step):
        left_circle_point = find_circle_point(alpha, -1)
        # right_circle_point = find_circle_point(alpha, 1)

        end_x = c * np.cos(alpha)
        end_y = c * np.sin(alpha)
        end_point = np.array([end_x, end_y, 0])

        x, y = 10 * np.cos(alpha), 10 * np.sin(alpha)
        second_lines.add(
            Line(end_point, np.array([x, y, 0]), color=LINES_COLOR, stroke_width=0.7, stroke_opacity=1))

        if -TAU <= alpha < -3 * PI / 2:
            left_heart_point, right_heart_point = find_heart_point(alpha+TAU)
            second_lines.add(
                Line(right_heart_point, end_point, color=MAIN_COLOR, stroke_width=stroke, stroke_opacity=brightness))

        if -3 * PI / 2 <= alpha < -PI:
            left_heart_point, right_heart_point = find_heart_point(3 * PI - alpha)
            second_lines.add(
                Line(left_heart_point, end_point, color=MAIN_COLOR, stroke_width=stroke, stroke_opacity=brightness))

        elif -PI <= alpha < - PI / 2:
            left_heart_point, right_heart_point = find_heart_point(3 * PI - alpha)
            second_lines.add(Line(left_heart_point, left_circle_point, color=MAIN_COLOR, stroke_width=stroke,
                                  stroke_opacity=brightness))
        elif alpha == -PI / 2:
            left_heart_point, right_heart_point = find_heart_point(alpha-PI)
            second_lines.add(Line(right_heart_point, left_circle_point, color=MAIN_COLOR, stroke_width=stroke,
                                  stroke_opacity=brightness))
        brightness -= br_step
        stroke -= st_step

    return second_lines


def draw_lines():
    first_lines = draw_right_lines()
    second_lines = draw_left_lines()

    return [first_lines, second_lines]


def create_heart_shape():
    hearts = VGroup()

    start_color = "#FF69B4"
    end_color = "#8B0000"

    num_steps = int((heart_scale - 0.5) / 0.05)

    for i, k in enumerate(np.arange(heart_scale, 0.5, -0.05)):
        color = interpolate_color(ManimColor(start_color), ManimColor(end_color), i / num_steps)

        heart_shape = VMobject(fill_color=color, fill_opacity=1, stroke_width=0)
        heart_points = []

        for alpha in np.linspace(PI / 2, -PI / 2, num_lines // 2):
            left_heart_point, right_heart_point = find_heart_point(alpha, k)
            heart_points.append(right_heart_point)

        for alpha in np.linspace(-PI / 2, PI / 2, num_lines // 2):
            left_heart_point, right_heart_point = find_heart_point(alpha, k)
            heart_points.append(left_heart_point)

        heart_shape.set_points_smoothly(heart_points)

        hearts.add(heart_shape)

    return hearts


class Heart(Scene):
    def construct(self):
        self.main_art()

    def main_art(self):
        self.add(Circle(radius=c, color=PINKY, fill_opacity=0.5, stroke_width=0))
        self.add(*draw_lines())
        self.add(*create_heart_shape())


if __name__ == '__main__':
    print(find_heart_point(-PI / 2))
