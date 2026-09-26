"""
Geração de grafos aleatórios reprodutíveis (modelo de Erdős–Rényi G(n, p)).
"""
import random

from models.graph import Graph


def generate_graph(
    num_nodes=10,
    edge_probability=0.5,
    is_directed=True,
    cost_range=(1, 1),
    seed=None,
    ensure_path=None,
    max_attempts=100,
):
    """
    :param num_nodes: quantidade de nós (int) ou intervalo (min, max) sorteado.
    :param edge_probability: probabilidade p de cada aresta existir.
    :param is_directed: grafo direcionado ou não.
    :param cost_range: (mín, máx) inteiros para o custo das arestas; (1, 1) = sem custo.
    :param seed: semente para reprodutibilidade dos experimentos.
    :param ensure_path: par (início, objetivo); se informado, regera o grafo até
                        existir caminho entre eles (até `max_attempts` tentativas).
    """
    if not 0 <= edge_probability <= 1:
        raise ValueError("edge_probability deve estar em [0, 1].")
    rng = random.Random(seed)

    if isinstance(num_nodes, tuple):
        num_nodes = rng.randint(*num_nodes)

    for _ in range(max_attempts):
        graph = _build(rng, num_nodes, edge_probability, is_directed, cost_range)
        if ensure_path is None or graph.is_reachable(*ensure_path):
            return graph

    raise RuntimeError(
        f"Não foi possível gerar um grafo com caminho {ensure_path} em "
        f"{max_attempts} tentativas. Aumente edge_probability."
    )


def _build(rng, num_nodes, edge_probability, is_directed, cost_range):
    graph = Graph(is_directed=is_directed)
    values = [str(i) for i in range(num_nodes)]
    for value in values:
        graph.add_node(value)

    for i, source in enumerate(values):
        # Não direcionado: só pares i < j, pois add_edge já liga os dois lados.
        # Sem isso a probabilidade efetiva vira 2p - p².
        destinations = values if is_directed else values[i + 1:]
        for dest in destinations:
            if source == dest:
                continue
            if rng.random() < edge_probability:
                graph.add_edge(source, dest, rng.randint(*cost_range))
    return graph
