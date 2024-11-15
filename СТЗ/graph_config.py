from collections import defaultdict

from manim import *

GRAPH_COLOR = WHITE
LABEL_COLOR = WHITE
TEXT_COLOR = BLUE
FLOW_COLOR = YELLOW

COST_COLOR = GOLD
BANDWIDTH_COLOR = BLUE
IN_COLOR = GREEN
OUT_COLOR = RED

BASIS_COLOR = ManimColor("#EC6B00")
POTENTIAL_COLOR = ManimColor("#9E9645")
CRITERIA_COLOR = PURPLE
BAD_EDGE_COLOR = RED
CYCLE_COLOR = GREEN

out_arrow_len_coef = 1.35

edges = [
    (1, 2), (1, 5), (2, 3), (2, 5),
    (3, 4), (3, 6), (5, 3), (5, 6),
    (6, 4)
]

costs = {a: b for a, b in zip(edges, [1, 2, 5, 2, 3, 1, 2, 6, 1])}

bandwidth = {a: b for a, b in zip(edges, [
    25, 40, 70, 45,
    30, 20, 60, 50,
    30
])}

source = {
    1: 50,
    2: 80,
}

stock = {
    3: 30,
    4: 40,
    6: 60
}

initial_flow = [25, 25, 60, 45, 30, 20, 20, 50, 10]
initial_basis = [(1, 5), (5, 3), (2, 3), (5, 6), (6, 4)]
initial_nonbasis = [(a, b) for a, b in edges if (a, b) not in initial_basis]


def find_cycle_order(edges, start_edge):
    graph = {}
    for u, v in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append(v)
        graph[v].append(u)

    u, v = start_edge
    cycle_order = [start_edge]
    prev_vertex = u
    current_vertex = v

    while True:
        next_vertex = None
        for neighbor in graph[current_vertex]:
            if neighbor != prev_vertex:
                next_vertex = neighbor
                break

        if next_vertex is None:
            break

        edge = (current_vertex, next_vertex) # if (current_vertex, next_vertex) in edges else (next_vertex, current_vertex)
        cycle_order.append(edge)
        prev_vertex, current_vertex = current_vertex, next_vertex

        if (current_vertex, prev_vertex) == start_edge or (prev_vertex, current_vertex) == start_edge:
            break

    return cycle_order

# edges_ = [(1, 5), (5, 3), (2, 3), (5, 6), (6, 4)]  # Заранее известный набор дуг цикла
# start_edge = (1, 2)
#
# cycle_order = find_cycle_order(edges_, start_edge)
# print("Порядок обхода цикла, начиная с дуги", start_edge, ":", cycle_order)