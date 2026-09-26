"""
Busca em Profundidade (Depth-First Search) — versão de busca em grafo.

Estratégia : expande sempre o nó mais profundo da fronteira.
Fronteira  : pilha (LIFO) explícita — sem recursão, logo sem RecursionError
             em grafos grandes.
Visitados  : conjunto global de estados já expandidos (evita ciclos e
             reexpansões). Isso torna a busca completa em espaços finitos.
Ótima?     : não — retorna o primeiro caminho encontrado, não o mais barato.
Tempo      : O(V + E) em grafos explícitos; O(b^m) em árvores de busca.
Memória    : O(V) no pior caso por causa do conjunto de visitados.
"""
from algorithms.tracing import record_step as _record
from models.search_result import SearchResult
from models.state_space import Goal, StateSpace, make_goal_test


def dfs(space: StateSpace, start, goal: Goal, trace=None) -> SearchResult:
    """
    :param trace: lista opcional; se informada, recebe um registro por expansão
                  (nó expandido, profundidade, caminho atual e fronteira).
                  Usada pela visualização web; não altera o resultado.
    """
    is_goal = make_goal_test(goal)

    # Cada entrada da pilha: (estado, pai, custo acumulado até ele)
    frontier = [(start, None, 0)]
    parents = {}        # estado -> pai (registrado no momento da expansão)
    costs = {}          # estado -> custo acumulado do caminho que o expandiu
    visited = set()

    nodes_explored = 0
    nodes_generated = 1
    max_frontier = 1

    while frontier:
        state, parent, g = frontier.pop()

        # Um mesmo estado pode ter sido empilhado por pais diferentes;
        # só a primeira retirada conta como expansão.
        if state in visited:
            continue
        visited.add(state)
        parents[state] = parent
        costs[state] = g
        nodes_explored += 1

        if is_goal(state):
            path = _reconstruct(parents, state)
            _record(trace, state, path, frontier, goal=True)
            return SearchResult(
                algorithm="DFS",
                path=path,
                nodes_explored=nodes_explored,
                nodes_generated=nodes_generated,
                max_frontier_size=max_frontier,
                cost=g,
            )

        # Empilha em ordem reversa para que o primeiro vizinho seja o
        # primeiro a sair (mesma ordem da versão recursiva).
        for neighbor, step_cost in reversed(list(space.successors(state))):
            if neighbor not in visited:
                frontier.append((neighbor, state, g + step_cost))
                nodes_generated += 1
        max_frontier = max(max_frontier, len(frontier))
        if trace is not None:
            _record(trace, state, _reconstruct(parents, state), frontier)

    return SearchResult(
        algorithm="DFS",
        path=None,
        nodes_explored=nodes_explored,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier,
    )


def _reconstruct(parents, state):
    path = []
    while state is not None:
        path.append(state)
        state = parents[state]
    return path[::-1]

