import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

def render_tab(df):
    print("Zakres dat:", df['tran_date'].min(), df['tran_date'].max())

    grouped_bar = df[df['total_amt'] > 0].groupby(
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
        title='Przychody',
        title_x=0.5, 
        margin=dict(l=10, r=10, t=40, b=40),
        legend=dict(orientation="h", y=-0.2),
    )

    grouped_map = df[df['total_amt'] > 0].groupby('country')['total_amt'].sum()

    map_fig = go.Figure(
        go.Choropleth(
            locations=grouped_map.index,
            locationmode='country names',
            z=grouped_map.values,
            colorscale='Viridis',
            reversescale=True,
            colorbar=dict(title='Sales')
        )
    )
    map_fig.update_layout(
        title='Mapa',
        title_x=0.5,  
        geo=dict(showframe=False, projection={'type': 'natural earth'}),
        margin=dict(l=10, r=10, t=40, b=40),
    )

    
    layout = html.Div([
        html.H1('Sprzedaż globalna', style={'text-align': 'center', 'color': '#333333', 'margin-bottom': '20px'}),
        html.Div([
            dcc.DatePickerRange(
                id='sales-range',
                start_date=df['tran_date'].min(),
                end_date=df['tran_date'].max(),
                display_format='YYYY-MM-DD',
                style={'margin': '0 auto', 'display': 'block'}
            )
        ], style={'text-align': 'center', 'margin-bottom': '20px'}),
        
        html.Div(id='selected-dates', style={'text-align': 'center', 'margin-top': '20px'}),
        html.Div([
            html.Div([
                dcc.Graph(id='bar-sales', figure=bar_fig)
            ], style={'flex': 1, 'margin-right': '10px'}),
            html.Div([
                dcc.Graph(id='choropleth-sales', figure=map_fig)
            ], style={'flex': 1, 'margin-left': '10px'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between'}),
    ], style={'padding': '20px', 'backgroundColor': '#FFFFFF', 'color': '#333333'})

    return layout
