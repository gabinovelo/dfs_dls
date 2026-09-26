# IA02 — Busca em Grafos: DFS e DLS

## Estrutura dos módulos

```
ia02/
├── main.py                     # ponto de entrada: experimentos e demonstração
├── models/                     # estruturas de dados (não sabem nada de busca)
│   ├── graph.py                #   Node e Graph ponderado (peso padrão = 1)
│   ├── state_space.py          #   interface StateSpace: successors(state)
│   └── search_result.py        #   saída padronizada de qualquer algoritmo
├── algorithms/                 # algoritmos (não sabem nada de geração/experimento)
│   ├── dfs.py                  #   DFS iterativa com pilha explícita
│   ├── dls.py                  #   DLS iterativa, distingue "corte" de "sem solução"
│   ├── depth_limit.py          #   estimativa de limite para a DLS
│   └── tracing.py              #   registro opcional de passos (para a web)
├── generators/
│   └── graph_generator.py      # grafos aleatórios G(n, p) com semente e custos
├── experiments/
│   ├── problems.py             # os 4 problemas de teste fixos
│   ├── runner.py               # mede tempo/memória e gera a tabela + CSV
│   └── export_web.py           # exporta resultados e passos para web/data.js
├── web/
│   ├── index.html              # visualização DFS × DLS (abre direto no navegador)
│   └── data.js                 # gerado por `python main.py --web`
└── tests/
    └── test_search.py          # testes unitários
```

As dependências seguem uma única direção:

```
experiments ──► algorithms ──► models
     └────────► generators ──► models
```

- `models` não importa nada do projeto.
- `algorithms` depende apenas da interface `StateSpace`, e não de `Graph`.
- Só `experiments` conhece tudo.

## Como rodar

```bash
python main.py            # tabela de comparação + results/comparison.csv
python main.py --demo     # demonstração no grafo de custos (bom para o seminário)
python main.py --web      # gera web/data.js; depois abra web/index.html
python -m unittest -v     # testes
```

Requer Python 3.9 ou superior e nenhuma biblioteca externa. Rode os comandos a partir da pasta `ia02/`.

## Visualização web

A página não reimplementa os algoritmos. `dfs` e `dls` aceitam um parâmetro opcional `trace` (uma lista) que recebe um registro por expansão, com o nó expandido, a profundidade, o ramo atual e a pilha. `export_web.py` roda os algoritmos com esse parâmetro e grava tudo em `web/data.js`, e a página apenas anima esses passos. Assim, o que aparece na tela é exatamente o comportamento do código em Python. Sem `trace`, a busca não tem custo extra.

O que a página mostra:

- **Os dois algoritmos lado a lado**, no mesmo passo.
- **Layout radial.** O início fica no centro e cada anel é a distância até ele. O limite da DLS aparece como um círculo tracejado.
- **A pilha, do topo para a base.** No DFS, os itens riscados já foram visitados e serão descartados ao sair da pilha.
- **Barras de comparação** com uma referência para o menor valor possível de profundidade e custo.
- **Um gráfico da DLS para cada limite *l***, que mostra os cortes abaixo da profundidade da solução.

O grafo grande (mais de 150 nós) mostra só as métricas, sem desenho.

## Interface comum dos algoritmos

```python
dfs(space, start, goal)              -> SearchResult
dls(space, start, goal, depth_limit) -> SearchResult
```

- **Entrada**: `space` é o grafo (ou qualquer objeto com `successors`), `start` é o estado inicial e `goal` é o estado objetivo. O objetivo também pode ser uma função de teste, como `lambda s: s.venceu()`.
- **Saída**: `SearchResult` com `path`, `nodes_explored`, `depth`, `cost`, `solution_size`, `max_frontier_size`, `cutoff` e `status`. O runner ainda preenche `elapsed_time` e `peak_memory`.

"Nós explorados" significa nós **retirados da fronteira e testados como objetivo**. O critério é o mesmo nos dois algoritmos.

## Aplicando a um jogo (árvore de movimentos)

Não é preciso montar um `Graph`. Basta uma classe que gere os estados seguintes a partir das regras:

```python
class MeuJogo:
    def successors(self, estado):
        return [(estado.aplicar(m), 1) for m in estado.movimentos_validos()]

dls(MeuJogo(), estado_inicial, lambda s: s.eh_vitoria(), depth_limit=6)
```

Os estados precisam ser *hashable* (por exemplo, tuplas ou dataclasses com `frozen=True`), porque o DFS os guarda em um `set`.

## Comparação teórica (para os slides)

| Critério            | DFS (busca em grafo)                        | DLS                                  |
|---------------------|---------------------------------------------|--------------------------------------|
| Estratégia          | expande o nó mais profundo                  | DFS com corte na profundidade *l*    |
| Fronteira           | pilha (LIFO)                                | pilha (LIFO)                         |
| Completo?           | sim, em espaços finitos                     | só se *d ≤ l*                        |
| Ótimo?              | não                                         | não                                  |
| Tempo               | O(V+E) no grafo; O(b^m) na árvore           | O(b^l)                               |
| Memória             | O(V) (conjunto de visitados)                | O(b·l)                               |

Legenda: *b* é o fator de ramificação, *m* a profundidade máxima, *d* a profundidade da solução mais rasa e *l* o limite.
