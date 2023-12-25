from typing import Iterable

def to_mermaid(graph: Iterable[tuple[str, str]]) -> str:
    print('graph TD;')
    for edge in graph:
        print(f'{edge[0]} --> {edge[1]};')
