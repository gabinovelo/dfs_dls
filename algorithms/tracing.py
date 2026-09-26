"""
Registro opcional dos passos de uma busca, usado pela visualização web.

Os algoritmos chamam `record_step` a cada expansão; se `trace` for None nada é
feito, então a busca normal não paga nenhum custo extra.
"""


def record_step(trace, state, path, frontier, goal=False, cut=False):
    if trace is None:
        return
    trace.append({
        "node": state,                               # nó expandido neste passo
        "depth": len(path) - 1,                      # profundidade dele
        "path": list(path),                          # ramo atual (início -> nó)
        "frontier": [entry[0] for entry in frontier],  # pilha após o passo (topo = fim)
        "goal": goal,                                # passo em que o objetivo foi achado
        "cut": cut,                                  # DLS: nó podado pelo limite
    })
