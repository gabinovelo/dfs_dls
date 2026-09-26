"""
Conjunto fixo de problemas de teste exigido pelo trabalho:
  1 grafo pequeno, 1 médio, 1 maior e 1 com caminhos de custos diferentes.

Todos usam semente fixa, então cada execução compara exatamente os mesmos grafos.
"""
from dataclasses import dataclass
from typing import Hashable, Optional

from algorithms.depth_limit import depth_limit_for
from generators.graph_generator import generate_graph
from models.graph import Graph


@dataclass
class Problem:
    name: str
    graph: Graph
    start: Hashable
    goal: Hashable
    depth_limit: Optional[int] = None   # None = estimado a partir do grafo
    description: str = ""

    def __post_init__(self):
        if self.depth_limit is None:
            self.depth_limit = depth_limit_for(self.graph)


def _random_problem(name, num_nodes, p, seed, description):
    start, goal = "0", str(num_nodes - 1)
    graph = generate_graph(
        num_nodes=num_nodes,
        edge_probability=p,
        seed=seed,
        ensure_path=(start, goal),
    )
    return Problem(name, graph, start, goal, description=description)


def weighted_graph() -> Graph:
    """
    O caminho mais barato é S → B → C → G (custo 3, profundidade 3), mas DFS e
    DLS seguem S → A primeiro e retornam S → A → G (custo 20, profundidade 2).
    Serve para demonstrar que nenhum dos dois é ótimo.
    """
    g = Graph(is_directed=True)
    g.add_edge("S", "A", 10)
    g.add_edge("S", "B", 1)
    g.add_edge("A", "G", 10)
    g.add_edge("B", "C", 1)
    g.add_edge("C", "G", 1)
    return g


def build_problems():
    return [
        _random_problem("pequeno", 10, 0.30, seed=1, description="10 nós, p=0.30"),
        _random_problem("médio", 100, 0.05, seed=2, description="100 nós, p=0.05"),
        _random_problem("grande", 1000, 0.004, seed=3, description="1000 nós, p=0.004"),
        Problem("custos", weighted_graph(), "S", "G", depth_limit=3,
                description="custos diferentes, ótimo = 3"),
        Problem("custos (l=1)", weighted_graph(), "S", "G", depth_limit=1,
                description="limite insuficiente → corte"),
    ]
