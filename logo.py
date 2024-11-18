from manim import *
import numpy as np

a = 2.4
b = 1.2
h = np.sqrt(a ** 2 - b ** 2)
#
c = a + b

num_lines = 150

num_radial_curves = 33
max_curve_radius = a * 0.8

angle_step = TAU / num_lines

start_stroke = 7

br_step = 1 / num_lines * 1.3
st_step = start_stroke / num_lines

SECTOR_COLOR = '#1f1c17'
LINES_COLOR = '#9a5a18'
CURVE_COLOR = '#7e4706'


def get_center_curves():
    curves = VGroup()
    angle_step = TAU / num_radial_curves
    for i in range(num_radial_curves):
        angle = i * angle_step

        def radial_curve(t):
            start_radius = max_curve_radius * 0.2
            end_radius = max_curve_radius
            radius = interpolate(start_radius, end_radius, t)

            x = radius * np.cos(angle + 0.3 * np.sin(3 * np.pi * t))
            y = radius * np.sin(angle + 0.3 * np.sin(3 * np.pi * t))
            return np.array([x, y, 0])

        curve = ParametricFunction(
            radial_curve,
            t_range=np.array([0, 1]),
            color=CURVE_COLOR,
            stroke_width=1
        )
        curves.add(curve)
    return curves


def find_point(alpha, invert_x):
    discriminant = a ** 2 - b ** 2 * np.sin(alpha) ** 2
    t1 = invert_x * b * np.cos(alpha) - np.sqrt(discriminant)
    t2 = invert_x * b * np.cos(alpha) + np.sqrt(discriminant)
    t = max(t1, t2)
    x, y = t * np.cos(alpha), t * np.sin(alpha)
    return np.array([x, y, 0])


def draw_right_lines():
    first_lines = VGroup()
    stroke = start_stroke
    brightness = 1
    for alpha in np.arange(PI / 2, -3 * PI / 2, -angle_step):
        left_circle_point = find_point(alpha, -1)
        right_circle_point = find_point(alpha, 1)

        if 0 <= alpha < PI / 2:
            first_lines.add(
                Line(left_circle_point, right_circle_point, color=GRAY, stroke_width=stroke,
                     stroke_opacity=brightness))

        elif -PI <= alpha < - PI / 2:
            end_x = c * np.cos(alpha)
            end_y = c * np.sin(alpha)
            end_point = np.array([end_x, end_y, 0])
            first_lines.add(
                Line(left_circle_point, end_point, color=GRAY, stroke_width=stroke, stroke_opacity=brightness))

        elif -PI / 2 <= alpha < 0:
            start_point = left_circle_point
            end_x = c * np.cos(alpha)
            end_y = c * np.sin(alpha)
            end_point = np.array([end_x, end_y, 0])
            x, y = 10 * np.cos(alpha), 10 * np.sin(alpha)
            first_lines.add(
                Line(end_point, np.array([x, y, 0]), color=LINES_COLOR, stroke_width=0.7, stroke_opacity=0.5))
            first_lines.add(Line(start_point, end_point, color=GRAY, stroke_width=stroke, stroke_opacity=brightness))

        brightness -= br_step
        stroke -= st_step
    return first_lines


def draw_left_lines():
    second_lines = VGroup()
    stroke = start_stroke
    brightness = 1

    for alpha in np.arange(-PI / 2, -TAU, -angle_step):
        left_circle_point = find_point(alpha, -1)
        right_circle_point = find_point(alpha, 1)

        end_x = c * np.cos(alpha)
        end_y = c * np.sin(alpha)
        end_point = np.array([end_x, end_y, 0])

        x, y = 10 * np.cos(alpha), 10 * np.sin(alpha)
        second_lines.add(
            Line(end_point, np.array([x, y, 0]), color=LINES_COLOR, stroke_width=0.7, stroke_opacity=0.5))

        if -TAU <= alpha < -3 * PI / 2 or -3 * PI / 2 <= alpha < -PI:

            second_lines.add(
                Line(right_circle_point, end_point, color=GRAY, stroke_width=stroke, stroke_opacity=brightness))

        elif -PI <= alpha < - PI / 2:
            second_lines.add(Line(right_circle_point, left_circle_point, color=GRAY, stroke_width=stroke,
                                  stroke_opacity=brightness))

        brightness -= br_step
        stroke -= st_step

    return second_lines


def draw_lines():
    first_lines = draw_right_lines()
    second_lines = draw_left_lines()

    return [first_lines, second_lines]


class Logo(Scene):
    def construct(self):
        self.draw_center()
        self.main_art()

    def main_art(self):
        self.add(*draw_lines())

    def draw_center(self):
        curves = get_center_curves()
        circle1 = Circle(radius=a).move_to(LEFT * b)
        circle2 = Circle(radius=a).move_to(RIGHT * b)
        intersection_area = (
            Intersection(circle1, circle2, fill_opacity=0.6).set_color(BLACK).set_stroke(color=CURVE_COLOR, width=2,
                                                                                         opacity=0.35)
            .scale(
                0.93))
        self.add(intersection_area)
        self.add(curves.scale(0.5))
        self.add(*[Circle(radius=i * a, color=BLACK) for i in np.arange(0.1, 0.357, 0.0225)])
        self.add(Circle(radius=0.388 * a, color=BLACK))
        # ManimColor('#000044')
        self.add(Circle(radius=0.055 * a, color=DARKER_GRAY, fill_opacity=1))
