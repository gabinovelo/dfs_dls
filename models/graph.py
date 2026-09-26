"""
Estruturas de dados do grafo.

O grafo implementa a interface de espaço de estados usada pelos algoritmos de
busca (ver models/state_space.py): basta expor `successors(state)`. Assim, os
mesmos algoritmos funcionam tanto para grafos quanto, no futuro, para um jogo
cujos estados sejam gerados sob demanda.
"""


class Node:
    """Nó do grafo: guarda seu valor e os vizinhos com o custo de cada aresta."""

    def __init__(self, value):
        self.value = value
        self.neighbors = {}  # {Node: custo} — O(1) para inserir e consultar

    def _add_neighbor(self, neighbor_node, cost=1):
        self.neighbors[neighbor_node] = cost

    def __repr__(self):
        return f"Node({self.value})"


class Graph:
    """Grafo direcionado ou não, com arestas ponderadas (peso padrão = 1)."""

    def __init__(self, is_directed=True):
        self.is_directed = is_directed
        self.nodes = {}  # {valor: Node}

    # ------------------------------------------------------------ construção
    def add_node(self, value):
        if value not in self.nodes:
            self.nodes[value] = Node(value)
        return self.nodes[value]

    def add_edge(self, source_value, destination_value, cost=1):
        if cost < 0:
            raise ValueError("Custos de aresta devem ser não negativos.")
        source_node = self.add_node(source_value)
        destination_node = self.add_node(destination_value)

        source_node._add_neighbor(destination_node, cost)
        if not self.is_directed:
            destination_node._add_neighbor(source_node, cost)

    # ------------------------------------------------------------- consultas
    def get_node(self, value):
        return self.nodes.get(value)

    def has_node(self, value):
        return value in self.nodes

    def has_edge(self, source_value, destination_value):
        source = self.nodes.get(source_value)
        destination = self.nodes.get(destination_value)
        return source is not None and destination in source.neighbors

    def edge_cost(self, source_value, destination_value):
        source = self.nodes[source_value]
        return source.neighbors[self.nodes[destination_value]]

    def successors(self, state):
        """Interface de espaço de estados: pares (próximo_estado, custo)."""
        node = self.nodes.get(state)
        if node is None:
            raise KeyError(f"Estado '{state}' não existe no grafo.")
        return [(neighbor.value, cost) for neighbor, cost in node.neighbors.items()]

    def path_cost(self, path):
        """Soma dos custos das arestas de um caminho (lista de valores)."""
        if not path:
            return None
        return sum(self.edge_cost(a, b) for a, b in zip(path, path[1:]))

    # ------------------------------------------------------------ estatística
    @property
    def num_nodes(self):
        return len(self.nodes)

    @property
    def num_edges(self):
        total = sum(len(node.neighbors) for node in self.nodes.values())
        return total if self.is_directed else total // 2

    def average_branching_factor(self):
        """Grau de saída médio (b), usado para estimar limites de profundidade."""
        if not self.nodes:
            return 0.0
        return sum(len(n.neighbors) for n in self.nodes.values()) / len(self.nodes)

    def is_reachable(self, start, goal):
        """Verificação utilitária de alcançabilidade (não é um algoritmo avaliado)."""
        if start not in self.nodes or goal not in self.nodes:
            return False
        seen, stack = {start}, [start]
        while stack:
            state = stack.pop()
            if state == goal:
                return True
            for nxt, _ in self.successors(state):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return False

    def __str__(self):
        if not self.nodes:
            return "Graph(Empty)"
        graph_type = "Directed" if self.is_directed else "Undirected"
        lines = [f"--- Graph ({graph_type}, {self.num_nodes} nodes, {self.num_edges} edges) ---"]
        for node in self.nodes.values():
            neighbors_str = ", ".join(f"{n.value}({c})" for n, c in node.neighbors.items())
            lines.append(f"Node {node.value} -> {neighbors_str}")
        return "\n".join(lines)
