"""
Estimativa de limite de profundidade para a DLS.

Em um grafo aleatório (Erdős–Rényi) com n nós e grau médio b > 1, a distância
típica entre dois nós é aproximadamente ln(n) / ln(b). Somamos uma folga
(`slack`) para cobrir caminhos um pouco mais longos que a média.
"""
import math

from models.graph import Graph


def estimate_depth_limit(num_nodes: int, branching_factor: float, slack: int = 2) -> int:
    if num_nodes <= 1:
        return 0
    if branching_factor <= 1:
        # Grafo muito esparso: a fórmula não vale; o limite seguro é n - 1.
        return num_nodes - 1
    estimate = math.ceil(math.log(num_nodes) / math.log(branching_factor)) + slack
    return min(estimate, num_nodes - 1)


def depth_limit_for(graph: Graph, slack: int = 2) -> int:
    """Estima o limite a partir das propriedades reais do grafo."""
    return estimate_depth_limit(graph.num_nodes, graph.average_branching_factor(), slack)
