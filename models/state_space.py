"""
Interface mínima que um problema precisa oferecer para ser resolvido pelos
algoritmos de busca.

`Graph` já a implementa. Para aplicar a busca a um jogo (árvore de movimentos),
basta criar uma classe com `successors(state)` que gere os estados seguintes a
partir das regras do jogo — sem precisar montar o grafo inteiro na memória.
"""
from typing import Any, Callable, Hashable, Iterable, Protocol, Tuple, Union


class StateSpace(Protocol):
    def successors(self, state: Hashable) -> Iterable[Tuple[Hashable, float]]:
        """Retorna pares (próximo_estado, custo_da_ação)."""
        ...


# O objetivo pode ser um estado específico ou uma função de teste
# (útil em jogos, onde vários estados podem ser vitória).
Goal = Union[Hashable, Callable[[Any], bool]]


def make_goal_test(goal: Goal) -> Callable[[Any], bool]:
    if callable(goal):
        return goal
    return lambda state: state == goal
