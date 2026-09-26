"""
Ponto de entrada do projeto.

  python main.py              -> roda os experimentos e salva results/comparison.csv
  python main.py --demo       -> demonstração passo a passo no grafo de custos
  python main.py --web        -> gera web/data.js para a visualização (web/index.html)
"""
import sys

from algorithms import dfs, dls
from experiments.problems import weighted_graph
from experiments.runner import print_paths, print_table, run_all, save_csv


def demo():
    graph = weighted_graph()
    print(graph, end="\n\n")
    print(dfs(graph, "S", "G"))
    for limit in (1, 2, 3):
        print(dls(graph, "S", "G", depth_limit=limit))
    print("\nMenor custo possível: S -> B -> C -> G (custo 3)")


def main():
    if "--demo" in sys.argv:
        demo()
        return
    if "--web" in sys.argv:
        from experiments.export_web import export
        print(f"Dados exportados para: {export()}")
        print("Abra web/index.html no navegador.")
        return
    rows = run_all()
    print_table(rows)
    print_paths(rows)
    print(f"\nCSV salvo em: {save_csv(rows)}")


if __name__ == "__main__":
    main()
