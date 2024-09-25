import requests
from bs4 import BeautifulSoup
import pandas as pd

import networkx as nx
from pyvis.network import Network

def get_df(url: str, to_int_flag: bool = True) -> pd.DataFrame:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find_all('table')[0]
    rows = table.find_all('tr')

    rows.pop(0)
    headers = [col.text.strip() for col in rows.pop(0).find_all('td')]
    empty_cell_index = headers.index("")
    headers = headers[1:empty_cell_index]

    data_dct = {}

    for row in rows:
        cols = row.find_all('td')

        if not cols[0].text.strip():
            break
        
        row_data = [col.text.strip() for col in cols[:empty_cell_index]]
        data_dct[row_data[0]] = row_data[1:]

        if to_int_flag:
            data_dct[row_data[0]] = list(map(int, data_dct[row_data[0]]))

    
    return pd.DataFrame(list(data_dct.values()), columns=headers, index=list(data_dct.keys()))


def draw_graph(pareto_levels: dict, edges: list, levels_number: int):
    G = nx.Graph()
    net = Network(directed=True)

    nodes = [
        (
            lang, 
            {'group': level, 'label': lang, 'size': 20}
        )
        for lang, level in pareto_levels.items()
    ]
    G.add_nodes_from(nodes)

    step, x, y = 50, -300, -250
    legend_nodes = [
        (
            level, 
            {
                'group': level, 
                'label': f"{level} level",
                'size': 30, 
                'physics': False, 
                'x': x, 
                'y': f'{y + (level-1)*step}px',
                'shape': 'box', 
                'widthConstraint': 50, 
                'font': {'size': 20}
            }
        )
        for level in range(1, 1+levels_number)
    ]
    G.add_nodes_from(legend_nodes)

    net.from_nx(G)
    net.add_edges(edges)

    net.show('graph.html', notebook=False)