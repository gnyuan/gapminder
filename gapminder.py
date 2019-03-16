#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/15 14:02
# @Author  : yuangn
# @File    : gapminder.py
# @Software: PyCharm

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

print('Loading CSV...')
df = pd.read_csv('sector_gapminder.csv')
print('Loaded Success.')
df = df[df.tdate>20190201]

sizeref = 200000
unique_sectors = list(df["sector"].unique())
unique_tdates = list(df['tdate'].unique())

app = dash.Dash()

app.layout = html.Div([
    html.H2(children='Gapminder. X:Volume. Y:Rate of Return. Bubble:Market Value'),
    dcc.Dropdown(
        id="sector-dropdown",
        options=[
            {'label': i, 'value': i} for i in unique_sectors
        ],
        value=unique_sectors[:5],
        multi=True
    ),
    dcc.Graph(id='gapminder',
              animate=True
              ),
    html.Button('Run', id='btn_run',),
    dcc.Slider(
        id='tdate-slider',
        min=0,
        max=len(unique_tdates)-1,
        value=0,
        step=1,
        marks={ i: str(unique_tdates[i])[4:] for i in range(len(unique_tdates)) }
    ),
    html.Div(children=max(df['tdate']), id='hidden-div', style={'display': 'none'}),
])

@app.callback(
    dash.dependencies.Output('tdate-slider', 'value'),
    [dash.dependencies.Input('btn_run', 'n_clicks'),],
    [dash.dependencies.State('hidden-div', 'children')]
)
def run_trigger(n_clicks, value):
    hidden_value = int(value)
    next_tdate = hidden_value+1 if hidden_value < len(unique_tdates)-1 else 0
    return next_tdate


@app.callback(
    dash.dependencies.Output('hidden-div', 'children'),
    [dash.dependencies.Input('tdate-slider', 'value'),])
def sync_tdate(value):
    return value

@app.callback(
    dash.dependencies.Output('gapminder', 'figure'),
    [dash.dependencies.Input('tdate-slider', 'value'),
     dash.dependencies.Input('sector-dropdown', 'value')])
def update_figure(selected_tdate_index, selected_sector):
    tdate_filtered_df = df[df.tdate == unique_tdates[selected_tdate_index]]
    filtered_df = tdate_filtered_df[df.sector.isin(selected_sector)]
    traces = []
    for i in filtered_df.sector.unique():
        df_by_sector = filtered_df[filtered_df['sector'] == i]
        traces.append(go.Scatter(
            x=df_by_sector['dealvalue'],
            y=df_by_sector['rate'],
            text=df_by_sector['stockname'],
            mode='markers',
            opacity=0.6,
            marker={
                'sizemode': 'area',
                'sizemin': 1,
                'sizeref': sizeref,
                'size': df_by_sector['floatvalue'],
            },
            name=i
        ))
    figure = {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'Volumne', 'range':[4, 5.7]},
            yaxis={'title': 'Rate of Return', 'range': [-10, 10]},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
        )
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')