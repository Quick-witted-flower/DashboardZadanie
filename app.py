import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
import datetime as dt
import os
import tab1
import tab2
import tab3
import sys
sys.stdout.reconfigure(encoding='utf-8')
from database import db


external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.title = "Dashboard"

app.layout = html.Div([
    dcc.Tabs(
        id='tabs',
        value='tab-1',  
        children=[
            dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
            dcc.Tab(label='Produkty', value='tab-2'),
            dcc.Tab(label='Kanały sprzedazy', value='tab-3')
        ]
    ),
    html.Div(id='tabs-content')  
], style={'backgroundColor': '#FFFFFF', 'color': 'black'})

database = db()
merged_df = database.merge()

@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return tab1.render_tab(database.merged)
    elif tab == 'tab-2':
        return tab2.render_tab(database.merged)
    elif tab == 'tab-3':
        if database.merged.empty or 'Store_type' not in database.merged.columns:
            return html.Div("Brak danych dla zakładki", style={'color': 'red'})
        return tab3.render_tab(database.merged)

@app.callback(
    Output('bar-sales', 'figure'),
    [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')]
)
def update_bar_sales(start_date, end_date):
    if start_date is None or end_date is None:
        return go.Figure()  # Zwróć pustą figurę, jeśli brakuje dat

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrowanie danych
    filtered = database.merged[
        (database.merged['tran_date'] >= start_date) &
        (database.merged['tran_date'] <= end_date)
    ]

    # Sprawdzenie, czy wynik filtrowania nie jest pusty
    if filtered.empty:
        return go.Figure()  # Zwróć pustą figurę, jeśli brak danych w zakresie

    # Grupowanie danych
    grouped = filtered.groupby(
        [pd.Grouper(key='tran_date', freq='ME'), 'Store_type']
    )['total_amt'].sum().unstack()

    # Tworzenie wykresu
    bar_fig = go.Figure()
    for col in grouped.columns:
        bar_fig.add_trace(go.Bar(
            x=grouped.index,
            y=grouped[col],
            name=col
        ))

    bar_fig.update_layout(
        barmode='stack',
        title='Miesięczne przychody w podziale na kanały sprzedaży'
    )
    return bar_fig

@app.callback(Output('choropleth-sales','figure'),
            [Input('sales-range','start_date'),Input('sales-range','end_date')])
def tab1_choropleth_sales(start_date,end_date):

    if start_date is None or end_date is None:
        return go.Figure()  # Zwróć pustą figurę, jeśli brakuje dat

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrowanie danych
    truncated = database.merged[
        (database.merged['tran_date'] >= start_date) &
        (database.merged['tran_date'] <= end_date)
    ]

    # Sprawdzenie, czy wynik filtrowania nie jest pusty
    if truncated.empty:
        return go.Figure()  # Zwróć pustą figurę, jeśli brak danych w zakresie

    # Grupowanie danych
    grouped = truncated[truncated['total_amt'] > 0].groupby('country')['total_amt'].sum().round(2)

    # Tworzenie mapy
    trace0 = go.Choropleth(
        colorscale='Viridis',
        reversescale=True,
        locations=grouped.index,
        locationmode='country names',
        z=grouped.values,
        colorbar=dict(title='Przychody')
    )
    data = [trace0]
    fig = go.Figure(data=data, layout=go.Layout(
        title='Mapa sprzedaży wg kraju',
        geo=dict(showframe=False, projection={'type': 'natural earth'})
    ))

    return fig

@app.callback(
    Output('barh-prod-subcat', 'figure'),
    [Input('prod_dropdown', 'value')]
)
def update_barh_prod_subcat(selected_prod_cat):
    filtered = database.merged[
        (database.merged['prod_cat'] == selected_prod_cat) &
        (database.merged['total_amt'] > 0)
    ]
    grouped = filtered.groupby('prod_subcat')['total_amt'].sum()

    barh_fig = go.Figure(
        go.Bar(x=grouped.values, y=grouped.index, orientation='h')
    )
    barh_fig.update_layout(
        title='Sprzedaż w podziale na płeć',
        barmode='stack'
    )
    return barh_fig

@app.callback(
    Output('customer-details', 'children'),
    [Input('store-type-dropdown', 'value')]
)
def update_customer_details(selected_store):
    if database.merged.empty or 'Store_type' not in database.merged.columns:
        return html.H4("Brak danych dla wybranego kanału sprzedaży", style={'color': 'black'})

    
    filtered = database.merged[database.merged['Store_type'] == selected_store]

  
    if filtered.empty:
        return html.H4("Brak danych dla wybranego kanału sprzedaży", style={'color': 'black'})

    
    customer_summary = filtered.groupby('cust_id').agg({
        'total_amt': 'sum',
        'tran_date': 'count'
    }).rename(columns={'tran_date': 'transactions'})

    
    table_header = html.Tr([html.Th('ID Klienta'), html.Th('Łączna sprzedaż'), html.Th('Liczba transakcji')])
    table_rows = [
        html.Tr([html.Td(idx), html.Td(f'{row.total_amt:.2f}'), html.Td(row.transactions)])
        for idx, row in customer_summary.iterrows()
    ]

    return html.Table([table_header] + table_rows, style={
        'width': '100%',
        'border': '1px solid black',
        'margin-top': '10px',
        'backgroundColor': '#FFFFFF',
        'color': 'black'
    })


if __name__ == '__main__':
    app.run_server(debug=True)

       