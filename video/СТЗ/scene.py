import math
from graph_config import *


def add_costs_and_bandwidth(arrow, bandwidth, cost=None):
    arrow_direction = arrow.get_unit_vector()
    normal_direction = np.array([-arrow_direction[1], arrow_direction[0], 0])
    angle = arrow.get_angle()

    bandwidth_text = Tex(f"{bandwidth}", font_size=28, color=BANDWIDTH_COLOR)
    bandwidth_text.move_to(
        arrow.get_center() + normal_direction * 0.25 + arrow_direction * (0.2 if cost else 0)).rotate(angle)
    cost_text = Tex("")
    if cost:
        cost_text = Tex(f"{cost}", font_size=28, color=COST_COLOR)
        cost_text.move_to(
            arrow.get_center() + normal_direction * 0.25 - arrow_direction * 0.2).rotate(angle)

    return cost_text, bandwidth_text


class Graph(Scene):
    def __init__(
            self,
            renderer=None,
            camera_class=Camera,
            always_update_mobjects=False,
            random_seed=None,
            skip_animations=False,
    ):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.criteria_text = None
        self.potential_texts = []
        self.sign_texts = {}
        self.delta_texts = {}
        self.cycle_edges = []
        self.potential_text = None
        self.text = Tex("")
        self.labels = {}
        self.bandwidth_texts = {}
        self.costs_texts = {}
        self.circles = {}
        self.arrows = {}

        self.basis = initial_basis
        self.nonbasis = initial_nonbasis

        self.flow = {a: b for a, b in zip(edges, initial_flow)}
        self.potentials = {1: 0}
        self.deltas = {}
        self.signs = {}

        self.bad_edge = None

        self.flows_text = {}
        self.flows_rects = {}

    def construct(self):
        self.build_graph()

        self.add_flow()
        self.add_basis()

        text = Tex("Calculate potentials", font_size=50, color=POTENTIAL_COLOR).to_edge(LEFT + DOWN * 0.7)
        self.play(FadeIn(text))

        self.add_potentials()

        self.play(FadeOut(text))

        text = Tex("Check criteria", font_size=50, color=CRITERIA_COLOR).to_edge(LEFT + DOWN * 0.7)
        self.play(FadeIn(text))

        self.add_criteria()
        self.play(FadeOut(text))

        self.add_cycle()

        self.update_flow()
        # self.add_basis()

        self.add_potentials()
        self.add_criteria()
        self.wait(1.3)

    def build_graph(self):
        vertices = {
            1: [-6, 0, 0],
            2: [-2, 2, 0],
            5: [-2, -2, 0],
            6: [2, -2, 0],
            3: [2, 2, 0],
            4: [6, 0, 0],
        }

        self.circles = {
            num: Circle(radius=0.4, color=GRAPH_COLOR, stroke_width=2).move_to(pos)
            for num, pos in vertices.items()
        }

        self.labels = {
            num: Tex(str(num), font_size=32, color=LABEL_COLOR).move_to(pos)
            for num, pos in vertices.items()
        }

        vertex_group = VGroup(*[self.circles[num] for num in self.circles] + [self.labels[num] for num in self.labels])
        self.play(FadeIn(vertex_group))

        self.build_arrows()

        arrow_animations = []
        cost_text_animations = []
        bandwidth_text_animations = []

        arrow_data = [
            (1, RIGHT, self.add_in_arrow),
            (2, DOWN, self.add_in_arrow),
            (6, (DOWN + RIGHT) / math.sqrt(2), self.add_out_arrow),
            (3, (UP + RIGHT) / math.sqrt(2), self.add_out_arrow),
            (4, RIGHT, self.add_out_arrow)
        ]

        for node, direction, add_arrow in arrow_data:
            arrow_anim, cost_anim, bandwidth_anim = add_arrow(node, direction)
            arrow_animations.append(arrow_anim)
            cost_text_animations.append(cost_anim)
            bandwidth_text_animations.append(bandwidth_anim)

        self.play(
            *arrow_animations,
            *cost_text_animations,
            *bandwidth_text_animations,
            run_time=2
        )
        self.wait(1.5)

        self.animate_graph()

        self.wait(1)

        self.text = Tex("Let's choose initial flow", font_size=50, color=TEXT_COLOR)
        self.text.to_edge(LEFT + DOWN * 0.7)
        self.play(Write(self.text))
        self.wait(1.3)

    def animate_graph(self):
        graph_group = VGroup(*self.circles.values(), *self.labels.values(), *self.arrows.values(),
                             *self.costs_texts.values(),
                             *self.bandwidth_texts.values())

        self.play(
            graph_group.animate.scale(0.8).shift(UP + LEFT * 1.5),
            run_time=2
        )

    def add_out_arrow(self, node, pos):
        short_arrow = Arrow(
            start=self.circles[node].get_center(),
            end=self.circles[node].get_center() + pos * out_arrow_len_coef,
            color=GRAPH_COLOR,
            buff=0.4,
            stroke_width=2,
            tip_length=0.2
        )
        self.arrows[node] = short_arrow
        cost_text, bandwidth_text = add_costs_and_bandwidth(short_arrow, stock[node])
        bandwidth_text.set_color(OUT_COLOR)
        self.costs_texts[node] = cost_text
        self.bandwidth_texts[node] = bandwidth_text

        arrow_animation = GrowArrow(short_arrow)
        bandwidth_animation = FadeIn(bandwidth_text)
        cost_animation = FadeIn(cost_text)
        return arrow_animation, cost_animation, bandwidth_animation

    def add_in_arrow(self, node, pos):
        short_arrow = Arrow(
            start=self.circles[node].get_center() - pos * out_arrow_len_coef,
            end=self.circles[node].get_center(),
            color=GRAPH_COLOR,
            buff=0.4,
            stroke_width=2,
            tip_length=0.2
        )
        self.arrows[node] = short_arrow

        arrow_animation = GrowArrow(short_arrow)
        cost_text, bandwidth_text = add_costs_and_bandwidth(short_arrow, source[node])
        bandwidth_text.set_color(IN_COLOR)
        self.costs_texts[node] = cost_text
        self.bandwidth_texts[node] = bandwidth_text

        cost_animation = FadeIn(cost_text)
        bandwidth_animation = FadeIn(bandwidth_text)

        return arrow_animation, cost_animation, bandwidth_animation

    def build_arrows(self):
        self.arrows = {}
        arrow_animations = []
        cost_text_animations = []
        bandwidth_text_animations = []
        for i, edge in enumerate(edges):
            start, end = edge
            arrow = Arrow(
                start=self.circles[start].get_center(),
                end=self.circles[end].get_center(),
                buff=0.4,
                color=GRAPH_COLOR,
                stroke_width=2,
                tip_length=0.2
            )
            self.arrows[(start, end)] = arrow
            cost_text, bandwidth_text = add_costs_and_bandwidth(arrow, bandwidth[(start, end)],
                                                                costs[(start, end)])
            self.costs_texts[(start, end)] = cost_text
            self.bandwidth_texts[(start, end)] = bandwidth_text
            arrow_animations.append(GrowArrow(arrow))

            cost_text_animations.append(FadeIn(cost_text))
            bandwidth_text_animations.append(FadeIn(bandwidth_text))

        self.play(*arrow_animations, run_time=2)

        self.play(*cost_text_animations, run_time=1.5)
        self.play(*bandwidth_text_animations, run_time=1.5)

    def add_flow(self):
        if hasattr(self, 'flows_text') and self.flows_text:
            elements_to_fade = self.get_elements_to_fade()
            self.play(*[FadeOut(element) for element in elements_to_fade])

        self.flows_text = {}
        self.flows_rects = {}
        self.delta_texts = {}

        for i, edge in enumerate(edges):
            start, end = edge
            arrow = self.arrows[(start, end)]
            arrow_direction = arrow.get_unit_vector()
            normal_direction = np.array([-arrow_direction[1], arrow_direction[0], 0])
            angle = arrow.get_angle()

            if self.flow[(start, end)] != bandwidth[(start, end)]:
                initial_flow_text = Tex(f"{self.flow[(start, end)]}", font_size=22, color=FLOW_COLOR)
                initial_flow_text.move_to(
                    arrow.get_center() - normal_direction * 0.2).rotate(angle)
                self.flows_text[edge] = initial_flow_text

            else:
                rect = SurroundingRectangle(self.bandwidth_texts[(start, end)], buff=0.05, stroke_width=1,
                                            color=FLOW_COLOR).rotate(angle)
                self.flows_rects[edge] = rect

        self.play(*[Write(text) for text in self.flows_text.values()],
                  *[Create(rect) for rect in self.flows_rects.values()], run_time=1)
        self.wait(1.5)

    def add_basis(self):
        new_text = Tex(" and basis", font_size=50, color=BASIS_COLOR).next_to(self.text, RIGHT)
        card_text = Tex("$|U_b|=n-1$", font_size=30, color=BASIS_COLOR).move_to(
            DOWN * 1 + RIGHT * 4)
        self.play(Write(new_text), Write(card_text))

        for start, end in self.basis:
            new_arrow = Arrow(
                start=self.circles[start].get_center(),
                end=self.circles[end].get_center(),
                buff=0.32,
                color=BASIS_COLOR,
                stroke_width=3,
                tip_length=0.2
            )
            old_arrow = self.arrows[(start, end)]
            self.play(Transform(old_arrow, new_arrow))

        # arrow_animations = [arrow.animate.set_stroke(width=3) for arrow in basis_arrows]
        # self.play(*arrow_animations, run_time=1)
        self.wait(2)
        self.play(FadeOut(new_text), FadeOut(self.text))
        # self.play(FadeOut(card_text))

    def add_potentials(self):
        self.potentials = {self.basis[0][0]: 0}
        for start, end in self.basis:
            if start in self.potentials.keys():
                self.potentials[end] = self.potentials[start] + costs[(start, end)]
            else:
                self.potentials[start] = self.potentials[end] - costs[(start, end)]
        self.potential_text = Tex(r"$u_j - u_i = c_{ij}, \forall (i,j)\in U_{b}$", font_size=30,
                                  color=POTENTIAL_COLOR).move_to(
            DOWN * 1.5 + RIGHT * 4)
        self.play(Write(self.potential_text))
        for vertex, potential in self.potentials.items():
            potential_label = Tex(f"{potential}", font_size=28, color=POTENTIAL_COLOR)
            if vertex in [1, 3, 4]:
                potential_label.next_to(self.circles[vertex], UP)
            elif vertex in [5, 6]:
                potential_label.next_to(self.circles[vertex], DOWN)
            elif vertex == 2:
                potential_label.next_to(self.circles[vertex], (UP + LEFT) * 0.5)
            self.potential_texts.append(potential_label)
            self.play(FadeIn(potential_label), run_time=1.5)

            if vertex == self.basis[0][0]:
                zero_meaning = Tex("for convenience", font_size=28, color=LABEL_COLOR).next_to(
                    potential_label, 2.2 * UP + 0.2 * RIGHT if vertex == 1 else 2.2 * DOWN)

                buffer_circle = Circle(radius=0.5, color=BLACK, fill_opacity=0).move_to(potential_label.get_center())
                link = Arrow(
                    start=zero_meaning.get_center(),
                    end=buffer_circle.get_center(),
                    color=GRAPH_COLOR,
                    stroke_width=1,
                    tip_length=0.1
                )
                self.play(Write(zero_meaning), FadeIn(link))
                self.wait(1)
                self.play(FadeOut(zero_meaning), FadeOut(link))

        self.wait(1.3)

    def add_criteria(self):
        self.criteria_text = Tex(r"$\Delta_{ij}= u_j - u_i - c_{ij}, \forall (i,j)\in U_{n}$", font_size=30,
                                 color=CRITERIA_COLOR).next_to(self.potential_text, DOWN)
        self.play(Write(self.criteria_text), run_time=1.5)
        self.wait(1.3)
        self.deltas = {}
        for start, end in self.nonbasis:
            self.deltas[(start, end)] = self.potentials[end] - self.potentials[start] - costs[(start, end)]

        for edge in self.nonbasis:
            v = self.deltas[edge]
            arrow = self.arrows[edge]
            arrow_direction = arrow.get_unit_vector()
            normal_direction = np.array([-arrow_direction[1], arrow_direction[0], 0])
            angle = arrow.get_angle()

            criteria_text = Tex(f"{v}", font_size=22, color=CRITERIA_COLOR).move_to(
                arrow.get_center() - normal_direction * 0.2).rotate(angle)
            self.delta_texts[edge] = criteria_text

            self.play(Write(criteria_text), run_time=1.5)

        err = Tex("Criteria is fulfilled!", font_size=35, color=GREEN)
        flag = False
        for start, end in self.nonbasis:
            if (self.flow[(start, end)] == bandwidth[(start, end)] and self.deltas[(start, end)] < 0 or
                    self.flow[(start, end)] == 0 and self.deltas[(start, end)] > 0):
                flag = True
                err = Tex(fr"$(i_0,j_0)=({start},{end})$", font_size=35, color=CRITERIA_COLOR)
                err.move_to(LEFT * 5.5 + DOWN)
                self.bad_edge = (start, end)

        err.move_to(LEFT * 3 + DOWN * 2)
        self.play(Write(err))
        self.wait(1.3)
        if flag:
            self.play(FadeOut(err))

    def add_cycle(self):
        start, end = self.bad_edge
        self.play(ApplyMethod(self.arrows[(start, end)].set_color, BAD_EDGE_COLOR))
        self.wait(1.3)

        bad_edge_sign = self.deltas[self.bad_edge] > 0
        sign_map = {True: '+', False: '—'}
        self.basis.append(self.bad_edge)
        self.nonbasis.remove(self.bad_edge)

        cycle_order = find_cycle_order(self.basis, self.bad_edge)

        for start, end in cycle_order[:-1]:
            if (start, end) in self.basis:
                sign = bad_edge_sign
                edge = (start, end)
            else:
                sign = not bad_edge_sign
                edge = (end, start)

            sign_text = Tex(fr"\textbf{{{sign_map[sign]}}}", font_size=24, color=CYCLE_COLOR)
            self.sign_texts[edge] = sign_text
            self.signs[edge] = sign
            self.cycle_edges.append(edge)

            arrow = self.arrows[edge]
            arrow_direction = arrow.get_unit_vector()
            normal_direction = np.array([-arrow_direction[1], arrow_direction[0], 0])
            angle = arrow.get_angle()
            sign_text.move_to(
                arrow.get_center() + normal_direction * 0.5).rotate(angle)
            self.play(Write(sign_text), run_time=1.5)

        self.wait(1.3)

    def update_flow(self):

        theta_text = Tex(
            r"$\theta_{ij} = \left\{\begin{array}{ll} d_{ij} - x_{ij} & \text{if } + \\ x_{ij} & \text{if } - \end{array} \right.$",
            font_size=25, color=CYCLE_COLOR)
        x_bar_text = Tex(
            r"$\bar{x}_{ij} = \begin{cases} x_{ij} + \theta & \text{if } + \\ x_{ij} - \theta & \text{if } - \end{cases}$",
            font_size=25, color=CYCLE_COLOR)
        U_b_bar_text = Tex(r"$\bar{U}_b = U_b \setminus \{(i_*, j_*)\} \cup \{(i_0, j_0)\}$", font_size=25,
                           color=CYCLE_COLOR)

        theta_text.next_to(self.criteria_text, DOWN)
        x_bar_text.next_to(theta_text, LEFT*2)
        U_b_bar_text.next_to(x_bar_text, LEFT*2)
        self.play(Write(theta_text), Write(x_bar_text), Write(U_b_bar_text), run_time=1.3)

        thetas = {}
        for edge, sign in self.signs.items():
            thetas[edge] = bandwidth[edge] - self.flow[edge] if sign else self.flow[edge]

        min_edge, min_theta = min(thetas.items(), key=lambda item: item[1])
        self.nonbasis.append(min_edge)
        self.basis.remove(min_edge)

        theta_text = Tex(rf"$\min_{{(i,j) \in U_{{c}}}} \theta_{{ij}} = {min_theta}$", font_size=35,
                         color=CYCLE_COLOR).move_to(LEFT * 5.5 + DOWN)

        edge_text = Tex(fr"$\text{{on edge}} (i_*,j_*)={min_edge}$", font_size=25, color=CRITERIA_COLOR).next_to(theta_text, DOWN)
        self.play(Write(theta_text), Write(edge_text))

        for edge in self.cycle_edges:
            flow = self.flow[edge]
            if self.signs[edge]:
                self.flow[edge] = flow + min_theta
            else:
                self.flow[edge] = flow - min_theta

        self.wait(1.3)
        self.play(FadeOut(theta_text), FadeOut(edge_text))
        self.arrows[self.bad_edge].set_stroke_width(3)
        self.arrows[min_edge].set_stroke_width(2)
        self.play(
            ApplyMethod(self.arrows[self.bad_edge].set_color, BASIS_COLOR))
        self.play(
            ApplyMethod(self.arrows[min_edge].set_color, GRAPH_COLOR))

        self.add_flow()

    def get_elements_to_fade(self):
        groups = [self.flows_text, self.flows_rects, self.sign_texts]
        elements_to_fade = self.potential_texts + [*self.delta_texts.values()]
        for group in groups:
            for edge, element in group.items():
                if edge in self.cycle_edges:
                    elements_to_fade.append(element)
        return elements_to_fade
