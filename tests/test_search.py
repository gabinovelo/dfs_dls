"""
Testes unitários (sem dependências externas):  python -m unittest -v
"""
import unittest

from algorithms import dfs, dls, estimate_depth_limit
from experiments.problems import weighted_graph
from generators import generate_graph
from models import Graph


def chain(n):
    g = Graph()
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g


class TestDFS(unittest.TestCase):
    def test_finds_path_and_metrics(self):
        r = dfs(weighted_graph(), "S", "G")
        self.assertEqual(r.path, ["S", "A", "G"])
        self.assertEqual(r.depth, 2)
        self.assertEqual(r.cost, 20)            # não ótimo: o ótimo é 3
        self.assertEqual(r.nodes_explored, 3)

    def test_start_is_goal(self):
        r = dfs(weighted_graph(), "S", "S")
        self.assertEqual(r.path, ["S"])
        self.assertEqual(r.depth, 0)
        self.assertEqual(r.cost, 0)

    def test_unreachable(self):
        r = dfs(weighted_graph(), "G", "S")
        self.assertFalse(r.found)

    def test_cycles_terminate(self):
        g = Graph()
        g.add_edge("a", "b"); g.add_edge("b", "a"); g.add_edge("b", "c")
        self.assertEqual(dfs(g, "a", "c").path, ["a", "b", "c"])

    def test_deep_graph_no_recursion_error(self):
        r = dfs(chain(20_000), 0, 19_999)
        self.assertEqual(r.depth, 19_999)

    def test_goal_as_predicate(self):
        r = dfs(chain(10), 0, lambda s: s > 5)
        self.assertEqual(r.path[-1], 6)


class TestDLS(unittest.TestCase):
    def test_within_limit(self):
        r = dls(weighted_graph(), "S", "G", 3)
        self.assertEqual(r.path, ["S", "A", "G"])
        self.assertEqual(r.cost, 20)

    def test_cutoff(self):
        r = dls(weighted_graph(), "S", "G", 1)
        self.assertFalse(r.found)
        self.assertTrue(r.cutoff)
        self.assertEqual(r.status, "corte (limite)")

    def test_no_solution_is_not_cutoff(self):
        r = dls(weighted_graph(), "G", "S", 5)
        self.assertFalse(r.found)
        self.assertFalse(r.cutoff)

    def test_goal_exactly_at_limit(self):
        self.assertTrue(dls(chain(5), 0, 4, 4).found)
        self.assertFalse(dls(chain(5), 0, 4, 3).found)

    def test_limit_zero(self):
        self.assertEqual(dls(chain(3), 0, 0, 0).path, [0])

    def test_path_checking_avoids_cycles(self):
        g = Graph(is_directed=False)
        g.add_edge("a", "b"); g.add_edge("b", "c")
        self.assertFalse(dls(g, "a", "z_inexistente_no_grafo" , 50).found)


class TestGenerator(unittest.TestCase):
    def test_seed_reproducible(self):
        a = generate_graph(30, 0.2, seed=42)
        b = generate_graph(30, 0.2, seed=42)
        self.assertEqual(str(a), str(b))

    def test_undirected_probability(self):
        # Com a correção, a densidade observada fica perto de p (e não de 2p - p²).
        n, p = 200, 0.1
        g = generate_graph(n, p, is_directed=False, seed=0)
        density = g.num_edges / (n * (n - 1) / 2)
        self.assertAlmostEqual(density, p, delta=0.01)

    def test_ensure_path(self):
        g = generate_graph(50, 0.05, seed=7, ensure_path=("0", "49"))
        self.assertTrue(g.is_reachable("0", "49"))

    def test_costs(self):
        g = generate_graph(20, 0.5, cost_range=(1, 10), seed=1)
        costs = [c for n in g.nodes.values() for c in n.neighbors.values()]
        self.assertTrue(all(1 <= c <= 10 for c in costs))


class TestDepthLimit(unittest.TestCase):
    def test_edge_cases(self):
        self.assertEqual(estimate_depth_limit(1, 3), 0)
        self.assertEqual(estimate_depth_limit(10, 0.5), 9)   # sem divisão por zero
        self.assertEqual(estimate_depth_limit(10, 1.0), 9)
        self.assertIsInstance(estimate_depth_limit(1000, 4), int)


if __name__ == "__main__":
    unittest.main()
