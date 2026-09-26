"""
Executa os algoritmos sobre o conjunto de problemas e produz a tabela de
comparação (terminal + CSV).

Tempo e memória são medidos em execuções separadas: o tracemalloc deixa o
código mais lento, então não pode ser usado junto com a medição de tempo.
"""
import csv
import statistics
import time
import tracemalloc
from pathlib import Path

from algorithms import dfs, dls
from experiments.problems import Problem, build_problems

# Registro de algoritmos: cada um recebe um Problem e devolve um SearchResult.
# Para adicionar um algoritmo novo, basta incluir uma entrada aqui.
ALGORITHMS = {
    "DFS": lambda p: dfs(p.graph, p.start, p.goal),
    "DLS": lambda p: dls(p.graph, p.start, p.goal, p.depth_limit),
}

COLUMNS = [
    ("problema", lambda p, r: p.name),
    ("algoritmo", lambda p, r: r.algorithm),
    ("nós/arestas", lambda p, r: f"{p.graph.num_nodes}/{p.graph.num_edges}"),
    ("limite", lambda p, r: r.depth_limit if r.depth_limit is not None else "-"),
    ("status", lambda p, r: r.status),
    ("profundidade", lambda p, r: _fmt(r.depth)),
    ("tamanho", lambda p, r: _fmt(r.solution_size)),
    ("custo", lambda p, r: _fmt(r.cost)),
    ("explorados", lambda p, r: r.nodes_explored),
    ("gerados", lambda p, r: r.nodes_generated),
    ("fronteira máx.", lambda p, r: r.max_frontier_size),
    ("tempo (ms)", lambda p, r: f"{r.elapsed_time * 1000:.3f}"),
    ("memória (KiB)", lambda p, r: f"{r.peak_memory / 1024:.1f}"),
]


def _fmt(value):
    return "-" if value is None else value


def run_one(algorithm, problem: Problem, repeats=5):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = algorithm(problem)
        times.append(time.perf_counter() - t0)

    tracemalloc.start()
    algorithm(problem)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    result.elapsed_time = statistics.median(times)
    result.peak_memory = peak
    return result


def run_all(problems=None, algorithms=None, repeats=5):
    problems = problems or build_problems()
    algorithms = algorithms or ALGORITHMS
    rows = []
    for problem in problems:
        for algorithm in algorithms.values():
            result = run_one(algorithm, problem, repeats)
            rows.append((problem, result))
    return rows


def print_table(rows):
    headers = [name for name, _ in COLUMNS]
    data = [[str(fn(p, r)) for _, fn in COLUMNS] for p, r in rows]
    widths = [max(len(h), *(len(row[i]) for row in data)) for i, h in enumerate(headers)]
    line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-+-".join("-" * w for w in widths))
    for row in data:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))


def format_path(path, max_states=12):
    if not path:
        return "-"
    if len(path) <= max_states:
        return " -> ".join(map(str, path))
    head = " -> ".join(map(str, path[: max_states // 2]))
    tail = " -> ".join(map(str, path[-(max_states // 2):]))
    return f"{head} -> ... ({len(path) - max_states} estados) ... -> {tail}"


def print_paths(rows):
    print("\nCaminhos encontrados (caminho completo no CSV):")
    for problem, result in rows:
        print(f"  [{problem.name:13}] {result.algorithm}: {format_path(result.path)}")


def save_csv(rows, file_path="results/comparison.csv"):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name for name, _ in COLUMNS] + ["caminho"])
        for p, r in rows:
            caminho = " -> ".join(map(str, r.path)) if r.path else ""
            writer.writerow([fn(p, r) for _, fn in COLUMNS] + [caminho])
    return path
