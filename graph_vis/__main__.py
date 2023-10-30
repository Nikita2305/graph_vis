from graph_vis.graph import Node, Graph
from graph_vis.generation import RandomGraphGenerator
from graph_vis.visualization import GraphVisualizer
import dash
from dash import dcc
from dash import html
import networkx as nx
import plotly.graph_objs as go
from datetime import datetime
from textwrap import dedent as d
import json
from dash_extensions.enrich import State, Output, DashProxy, Input, MultiplexerTransform

class CustomNode(Node):
    """
    Вершина визуализируемого графа
    """
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
    
    def get_info(self):
        return {**super().get_info(), "name": self.name}

graph = Graph()
graph.add_node(CustomNode("Nikita", 0))
graph.add_node(CustomNode("Sasha", 1))
graph.add_node(CustomNode("Kirill", 2))
graph.add_node(CustomNode("Vova", 3))
graph.add_node(CustomNode("SomeStud", 4))
graph.add_node(CustomNode("Kolya", 5))
graph.add_node(CustomNode("SomeStud2", 6))

graph.add_edge(0, 2)
graph.add_edge(1, 2)
graph.add_edge(2, 3)
graph.add_edge(2, 4)
graph.add_edge(2, 5)
graph.add_edge(5, 6)
vis = GraphVisualizer(graph)

LAST_SEARCHED_NODE_ID = None
START_NODE = 0 # TODO: убрать
CURRENT_DISPLAY_NODE_ID = START_NODE

def load_nx_graph(node_id=None):
    global vis
    if node_id is None:
        return nx.Graph()
    return vis.visualize(node_id)

def network_graph(nx_graph=None):
    traceRecode = []
    if nx_graph is not None:
        node_trace = go.Scatter(
            x=[],
            y=[],
            hovertext=[],
            text=[],
            customdata=[],
            mode='markers+text',
            textposition="bottom center",
            hoverinfo="text",
            marker={'size': 50, 'color': 'LightSkyBlue'}
        )

        index = 0
        for node in nx_graph.nodes():
            x, y = nx_graph.nodes[node]['pos']
            name = nx_graph.nodes[node]["name"]
            id = nx_graph.nodes[node]["id"]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['hovertext'] += tuple([str(id)])
            node_trace['text'] += tuple([name])
            node_trace['customdata'] += tuple([id])
        traceRecode += [node_trace]
        
        index = 0
        for edge in nx_graph.edges():
            x0, y0 = nx_graph.nodes[edge[0]]['pos']
            x1, y1 = nx_graph.nodes[edge[1]]['pos']
            trace = go.Scatter(x=tuple([x0, x1, None]),
                               y=tuple([y0, y1, None]),
                               mode='lines',
                               line={'width': 1, 'color': 'red'},
                               line_shape='spline',
                               opacity=1,
                               fillcolor='red')
            traceRecode.append(trace) 
        
    figure = {
        "data": traceRecode,
        "layout": go.Layout(
                # title='Interactive Transaction Visualization',
                showlegend=False,
                hovermode='closest',
                margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                height=600,
                clickmode='event+select')
    }
    return figure

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = DashProxy(__name__,
                external_stylesheets=external_stylesheets,
                prevent_initial_callbacks=True,
                transforms=[MultiplexerTransform()]
)
app.title = "Transaction Network"

# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowY': 'scroll',
        'overflowX': 'scroll',
        'height': '70%',
        'width': '100%' 
    }
}

app.layout = html.Div([
    html.Div([html.H1("Граф связей сообщества X")],
             className="row",
             style={'textAlign': "center"}),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="three columns",
                children=[
                    html.Div(
                        className="twelve columns",
                        children=[
                            html.Div(
                                children=[
                                    dcc.Markdown(d("""
                                    **Поиск аккаунта**
                                    Введите id, чтобы рассмотреть вершину
                                    """)),
                                    dcc.Input(id="id_input", type="text", placeholder="id")
                                ],
                                style={'height': '25%'}
                            ),
                            html.Div(
                                children=[
                                    html.Div(
                                        className="six columns",
                                        children=[
                                                html.Button(id='select-button',
                                                            n_clicks=0,
                                                            children='Submit',
                                                            style={"width": "100%"}
                                                )
                                        ],
                                        style={"width": "35%"}
                                    ),
                                    html.Div(className="six columns",
                                            id='text-box',
                                            style={"text_align": "center", "width": "60%"}
                                    )
                                ],
                                style={'height' : '20%'}
                            ), 
                            
                            html.Div(
                                children=[
                                    dcc.Markdown(d("""
                                    **Найденная вершина**\n
                                    """)),
                                    html.Pre(id='click-data', style=styles['pre'])
                                ]
                                ,style={'height': '50%'}
                            )
                        ],
                        style={'height': '400px'}
                    )
                ], 
            ),

            html.Div(
                className="seven columns",
                children=[
                        dcc.Graph(id="my-graph", figure=network_graph(load_nx_graph(START_NODE)))
                ], 
            ),

            html.Div(
                className="two columns",
                children=[
                    html.Div(
                        className='twelve columns',
                        children=[
                            dcc.Markdown(d("""
                            **Данные**\n
                            Наводите мышку на вершину.
                            """)),
                            html.Pre(id='hover-data', style=styles['pre'])
                        ]
                        ,style={'height': '300px'}
                    ) 
                ]
            )
        ]
    )
])

@app.callback(
    Output('hover-data', 'children'),
    Input('my-graph', 'hoverData'),
    State('hover-data', 'children'))
def display_hover_data(hoverData, old_data):
    global vis
    try:
        node_id = hoverData["points"][0]["customdata"]
    except Exception as ex:
        print(ex)
        return old_data
    return json.dumps(vis.graph.nodes[node_id].get_info(), indent=2)

@app.callback(
    Output('text-box', 'children'),
    Output('my-graph', 'figure'),
    Output('click-data', 'children'),
    Input('select-button', 'n_clicks'),
    State('id_input', 'value'),
    State('click-data', 'children'))
def select_node(n_clicks, id_input, click_data):
    global CURRENT_DISPLAY_NODE_ID
    global LAST_SEARCHED_NODE_ID
    global vis
    try:
        node_id = int(id_input)
        if node_id not in vis.graph.nodes:
            return f"Нет вершины с id={node_id}", network_graph(load_nx_graph(CURRENT_DISPLAY_NODE_ID)), str(click_data)
        LAST_SEARCHED_NODE_ID = node_id 
        CURRENT_DISPLAY_NODE_ID = LAST_SEARCHED_NODE_ID     
    except Exception as ex:
        print(ex)
        return "Ошибка", network_graph(load_nx_graph(CURRENT_DISPLAY_NODE_ID)), str(click_data)
    return "Найдено",\
            network_graph(load_nx_graph(CURRENT_DISPLAY_NODE_ID)),\
            json.dumps(vis.graph.nodes[node_id].get_info(), indent=2)\

@app.callback(
    Output('my-graph', 'figure'),
    Input('my-graph', 'clickData'))
def display_node(clickData):
    global CURRENT_DISPLAY_NODE_ID
    try:
        CURRENT_DISPLAY_NODE_ID = clickData["points"][0]["customdata"]
    except Exception as ex:
        print(ex, clickData)
    return network_graph(load_nx_graph(CURRENT_DISPLAY_NODE_ID))

if __name__ == '__main__':
    app.run_server(debug=True)
