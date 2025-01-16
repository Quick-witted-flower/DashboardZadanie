import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
from database import db
import tab1
import tab2
import tab3

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.title = "Dashboard"

app.layout = html.Div([
    dcc.Tabs(
        id='tabs',
        value='tab-1',
        children=[
            dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
            dcc.Tab(label='Produkty', value='tab-2'),
            dcc.Tab(label='Kanały sprzedaży', value='tab-3')
        ]
    ),
    html.Div(id='tabs-content')  
], style={'backgroundColor': '#FFFFFF', 'color': 'black'})

database = db()
merged_df = database.merge()


@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    print(f"Wybrana zakładka: {tab}")
    if tab == 'tab-1':
        print("Renderowanie tab1")
        return tab1.render_tab(database.merged)
    elif tab == 'tab-2':
        print("Renderowanie tab2")
        return tab2.render_tab(database.merged)
    elif tab == 'tab-3':
        print("Renderowanie tab3")
        if database.merged.empty or 'Store_type' not in database.merged.columns:
            return html.Div("Brak danych dla zakładki", style={'color': 'red'})
        return tab3.render_tab(database.merged)

@app.callback(
    [Output('bar-sales', 'figure'),
     Output('choropleth-sales', 'figure'),
     Output('selected-dates', 'children')],
    [Input('sales-range', 'start_date'),
     Input('sales-range', 'end_date')]
)
def update_sales_graphs(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_df = merged_df[(merged_df['tran_date'] >= start_date) & (merged_df['tran_date'] <= end_date)]

    grouped_bar = filtered_df[filtered_df['total_amt'] > 0].groupby(
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

    grouped_map = filtered_df[filtered_df['total_amt'] > 0].groupby('country')['total_amt'].sum()

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

    selected_dates = f"Wybrane daty: {start_date.date()} do {end_date.date()}"

    return bar_fig, map_fig, selected_dates

@app.callback(
    Output('barh-prod-subcat', 'figure'),
    [Input('prod_dropdown', 'value')]
)
def update_bar_chart(selected_category):
    filtered_data =merged_df[merged_df['prod_cat'] == selected_category]

    sales_by_subcat = filtered_data.groupby(['prod_subcat', 'Gender'])['total_amt'].sum().unstack().fillna(0)

    bar_fig = go.Figure()

    for gender in sales_by_subcat.columns:
        bar_fig.add_trace(go.Bar(
            x=sales_by_subcat.index,
            y=sales_by_subcat[gender],
            name=gender,
            orientation='h'
        ))

    bar_fig.update_layout(
        barmode='stack',
        title=f"Sprzedaż w podziale na płeć - {selected_category}",
        xaxis={'title': 'Sprzedaż'},
        yaxis={'title': 'Subkategoria produktów'}
    )

    return bar_fig

@app.callback(
    [Output('bar-sales-weekday', 'figure'),
     Output('channel-sales', 'figure'),
     Output('customer-details', 'children')],
    [Input('store-type-dropdown', 'value')]  
)
def update_channel_sales(store_type):
    filtered_data = merged_df[merged_df['Store_type'] == store_type]

    sales_by_weekday = filtered_data.groupby(['weekday', 'Store_type'], observed=True)['total_amt'].sum().unstack()

    bar_fig = go.Figure()
    for store_type in sales_by_weekday.columns:
        bar_fig.add_trace(go.Bar(
            x=sales_by_weekday.index,
            y=sales_by_weekday[store_type],
            name=store_type
        ))

    bar_fig.update_layout(
        barmode='stack',
        title='Sprzedaż w dniach tygodnia według kanałów sprzedaży',
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor='center'),
        xaxis_title="Dzień tygodnia",
        yaxis_title="Sprzedaż",
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='black')
    )

    customer_stats = filtered_data.groupby('Store_type').agg(
        customer_count=('cust_id', 'nunique'),
        transaction_count=('transaction_id', 'nunique'),
        total_sales=('total_amt', 'sum')
    ).reset_index()

    customer_stats['transaction_count'] = customer_stats['transaction_count'].fillna(0)
    customer_stats['total_sales'] = customer_stats['total_sales'].fillna(0)

    customer_fig = go.Figure()

    customer_fig.add_trace(go.Bar(
        x=customer_stats['Store_type'],
        y=customer_stats['transaction_count'],
        name="Liczba transakcji",
        marker_color='rgba(255, 99, 132, 0.6)',  
        hovertemplate="Liczba transakcji: %{y}<extra></extra>",  
    ))

    customer_fig.add_trace(go.Bar(
        x=customer_stats['Store_type'],
        y=customer_stats['total_sales'],
        name="Suma sprzedaży",
        marker_color='rgba(54, 162, 235, 0.6)', 
        hovertemplate="Suma sprzedaży: %{y:.2f}<extra></extra>",  
    ))

    customer_fig.update_layout(
        barmode='group',
        title='Transakcje i sprzedaż według kanałów sprzedaży',
        xaxis_title="Kanał sprzedaży",
        yaxis_title="Wartość",
        plot_bgcolor='#f4f4f4',  
        paper_bgcolor='#ffffff',  
        font=dict(color='black'),
        legend=dict(
            title="Legendy",
            x=0.5,
            xanchor="center",
            y=-0.3,
            orientation="h"
        ),
        margin=dict(l=30, r=30, t=50, b=80),  
    )

    customer_count = filtered_data['cust_id'].nunique()
    transaction_count = filtered_data['transaction_id'].nunique()
    total_sales = filtered_data['total_amt'].sum()
    avg_sales = filtered_data['total_amt'].mean()

    customer_details = html.Div([
        html.P(f'Liczba unikalnych klientów: {customer_count}'),
        html.P(f'Liczba transakcji: {transaction_count}'),
        html.P(f'Łączna sprzedaż: {total_sales:.2f} PLN'),
        html.P(f'Średnia sprzedaż: {avg_sales:.2f} PLN')
    ])

    return bar_fig, customer_fig, customer_details

if __name__ == '__main__':
    app.run_server(debug=True)
