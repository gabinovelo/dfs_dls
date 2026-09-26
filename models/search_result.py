from dataclasses import dataclass
from typing import Hashable, List, Optional


@dataclass
class SearchResult:
    """Saída padronizada de todos os algoritmos de busca."""

    algorithm: str
    path: Optional[List[Hashable]]
    nodes_explored: int = 0        # nós retirados da fronteira e testados como objetivo
    nodes_generated: int = 0       # nós inseridos na fronteira
    max_frontier_size: int = 0     # pico de elementos na fronteira (proxy de memória)
    cost: Optional[float] = None   # soma dos custos das arestas do caminho
    cutoff: bool = False           # DLS: a busca foi interrompida pelo limite?
    depth_limit: Optional[int] = None
    elapsed_time: Optional[float] = None   # preenchido pelo runner (segundos)
    peak_memory: Optional[int] = None      # preenchido pelo runner (bytes)

    @property
    def found(self) -> bool:
        return self.path is not None

    @property
    def depth(self) -> Optional[int]:
        """Profundidade da solução = número de arestas do caminho."""
        return len(self.path) - 1 if self.path else None

    @property
    def solution_size(self) -> Optional[int]:
        """Tamanho da solução = número de estados no caminho."""
        return len(self.path) if self.path else None

    @property
    def status(self) -> str:
        if self.found:
            return "encontrado"
        return "corte (limite)" if self.cutoff else "sem solução"

    def __str__(self):
        path = " -> ".join(map(str, self.path)) if self.path else "-"
        return (
            f"[{self.algorithm}] {self.status} | caminho: {path} | "
            f"profundidade: {self.depth} | custo: {self.cost} | "
            f"explorados: {self.nodes_explored} | fronteira máx.: {self.max_frontier_size}"
        )
