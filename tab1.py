import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

def render_tab(df):
    grouped_bar = df[(df['total_amt'] > 0)].groupby(
        [pd.Grouper(key='tran_date', freq='ME'), 'Store_type']
    )['total_amt'].sum().unstack()

    bar_fig = go.Figure()
    for col in grouped_bar.columns:
        bar_fig.add_trace(go.Bar(
            x=grouped_bar.index,
            y=grouped_bar[col],
            name=col
        ))

    bar_fig.update_layout(
        barmode='stack',
        title='Miesięczne przychody w podziale na kanały sprzedaży'
    )

    grouped_map = df[df['total_amt'] > 0].groupby('country')['total_amt'].sum()

    map_fig = go.Figure(
        go.Choropleth(
            locations=grouped_map.index,
            locationmode='country names',
            z=grouped_map.values,
            colorscale='Viridis',
            reversescale=True,
            colorbar=dict(title='Przychody')
        )
    )
    map_fig.update_layout(
        title='Mapa sprzedaży wg kraju',
        geo=dict(showframe=False, projection={'type': 'natural earth'})
    )

    layout = html.Div([
        html.H1('Sprzedaż globalna', style={'text-align': 'center' ,'color': 'white' , 'margin-bottom' : '20px'}),
        dcc.DatePickerRange(
            id='sales-range',
            start_date=df['tran_date'].min(),
            end_date=df['tran_date'].max(),
        ),
        html.Div([
            dcc.Graph(id='bar-sales', figure=bar_fig),
            dcc.Graph(id='choropleth-sales', figure=map_fig)
        ], style={'display': 'flex', 'flex-direction': 'row'}),
    ])

    return layout
