"""
Exporta os problemas de teste, os resultados e os passos de cada busca para
`web/data.js`, que a página `web/index.html` lê.

A página não reimplementa os algoritmos: ela só anima o que o Python produziu,
então o que aparece na tela é exatamente o comportamento do código avaliado.

    python main.py --web
"""
import heapq
import json
from collections import deque
from pathlib import Path

from algorithms import dfs, dls
from experiments.problems import Problem, build_problems
from experiments.runner import run_one

MAX_NODES_TO_ANIMATE = 150   # acima disso só exporta métricas (sem desenho/passos)
EXTRA_LIMITS = 4             # limites da DLS além do estimado, para o controle deslizante


def reference_optimum(problem: Problem):
    """Referência para comparação (não é um algoritmo avaliado):
    menor profundidade (BFS) e menor custo (Dijkstra) entre início e objetivo."""
    graph, start, goal = problem.graph, problem.start, problem.goal

    depth = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for nxt, _ in graph.successors(state):
            if nxt not in depth:
                depth[nxt] = depth[state] + 1
                queue.append(nxt)

    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, state = heapq.heappop(heap)
        if d > dist.get(state, float("inf")):
            continue
        for nxt, cost in graph.successors(state):
            if d + cost < dist.get(nxt, float("inf")):
                dist[nxt] = d + cost
                heapq.heappush(heap, (d + cost, nxt))

    return {"depth": depth.get(goal), "cost": dist.get(goal)}


def result_to_dict(result, trace=None):
    data = {
        "status": result.status,
        "found": result.found,
        "path": result.path,
        "depth": result.depth,
        "solutionSize": result.solution_size,
        "cost": result.cost,
        "nodesExplored": result.nodes_explored,
        "nodesGenerated": result.nodes_generated,
        "maxFrontier": result.max_frontier_size,
        "cutoff": result.cutoff,
        "depthLimit": result.depth_limit,
        "timeMs": round(result.elapsed_time * 1000, 4),
        "memoryKiB": round(result.peak_memory / 1024, 2),
    }
    if trace is not None:
        data["trace"] = trace
    return data


def export_problem(problem: Problem, repeats=5):
    graph = problem.graph
    animate = graph.num_nodes <= MAX_NODES_TO_ANIMATE

    def run(fn):
        result = run_one(fn, problem, repeats)
        trace = None
        if animate:
            trace = []
            fn(problem, trace)
        return result_to_dict(result, trace)

    dfs_data = run(lambda p, trace=None: dfs(p.graph, p.start, p.goal, trace=trace))

    optimum = reference_optimum(problem)
    max_limit = max(problem.depth_limit, optimum["depth"] or 0) + EXTRA_LIMITS
    dls_data = {}
    for limit in range(0, max_limit + 1):
        dls_data[limit] = run(
            lambda p, trace=None, l=limit: dls(p.graph, p.start, p.goal, l, trace=trace)
        )

    return {
        "name": problem.name,
        "description": problem.description,
        "directed": graph.is_directed,
        "numNodes": graph.num_nodes,
        "numEdges": graph.num_edges,
        "branching": round(graph.average_branching_factor(), 2),
        "start": problem.start,
        "goal": problem.goal,
        "estimatedLimit": problem.depth_limit,
        "optimum": optimum,
        "animate": animate,
        "nodes": list(graph.nodes) if animate else [],
        "edges": [
            [src, dst.value, cost]
            for src, node in graph.nodes.items()
            for dst, cost in node.neighbors.items()
        ] if animate else [],
        "dfs": dfs_data,
        "dls": dls_data,
    }


def export(file_path="web/data.js", problems=None):
    problems = problems or [
        p for p in build_problems() if p.name != "custos (l=1)"  # o controle de limite cobre esse caso
    ]
    payload = {"problems": [export_problem(p) for p in problems]}
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "// Gerado por experiments/export_web.py — não edite à mão.\n"
        "window.SEARCH_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    return path
