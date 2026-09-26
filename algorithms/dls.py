"""
Busca em Profundidade Limitada (Depth-Limited Search).

Estratégia : DFS que não expande nós além da profundidade `depth_limit`.
Fronteira  : pilha (LIFO) explícita, cada entrada guarda o caminho até o nó.
Ciclos     : evitados checando se o vizinho já está no caminho atual
             (checagem por ramo). Diferente do DFS, NÃO há visitados global,
             então um estado pode ser reexpandido por caminhos diferentes —
             é o comportamento clássico da DLS e explica seu custo O(b^l).
Completa?  : só se a solução mais rasa tiver profundidade d <= l.
Ótima?     : não.
Tempo      : O(b^l)     Memória: O(b·l)

Resultados possíveis (SearchResult.status):
  - "encontrado"      : caminho dentro do limite;
  - "corte (limite)"  : nada encontrado, mas algum ramo foi podado pelo limite
                        (aumentar l pode revelar uma solução);
  - "sem solução"     : o espaço foi esgotado sem atingir o limite, logo não
                        existe caminho em profundidade alguma.
"""
from algorithms.tracing import record_step as _record
from models.search_result import SearchResult
from models.state_space import Goal, StateSpace, make_goal_test


def dls(space: StateSpace, start, goal: Goal, depth_limit: int, trace=None) -> SearchResult:
    """:param trace: lista opcional de passos para visualização (ver dfs)."""
    if depth_limit < 0:
        raise ValueError("depth_limit deve ser >= 0.")
    is_goal = make_goal_test(goal)

    # Cada entrada: (estado, caminho até ele como tupla, custo acumulado)
    frontier = [(start, (start,), 0)]
    nodes_explored = 0
    nodes_generated = 1
    max_frontier = 1
    cutoff = False

    while frontier:
        state, path, g = frontier.pop()
        nodes_explored += 1
        depth = len(path) - 1

        if is_goal(state):
            _record(trace, state, path, frontier, goal=True)
            return SearchResult(
                algorithm="DLS",
                path=list(path),
                nodes_explored=nodes_explored,
                nodes_generated=nodes_generated,
                max_frontier_size=max_frontier,
                cost=g,
                depth_limit=depth_limit,
            )

        successors = [
            (nxt, c) for nxt, c in space.successors(state) if nxt not in path
        ]

        if depth >= depth_limit:
            # Nó no limite: não expande. Só é "corte" se havia para onde ir.
            if successors:
                cutoff = True
            _record(trace, state, path, frontier, cut=bool(successors))
            continue

        for neighbor, step_cost in reversed(successors):
            frontier.append((neighbor, path + (neighbor,), g + step_cost))
            nodes_generated += 1
        max_frontier = max(max_frontier, len(frontier))
        _record(trace, state, path, frontier)

    return SearchResult(
        algorithm="DLS",
        path=None,
        nodes_explored=nodes_explored,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier,
        cutoff=cutoff,
        depth_limit=depth_limit,
    )
