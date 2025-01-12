import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

def render_tab(df):
    # Dodanie kolumny z dniami tygodnia
    df['weekday'] = pd.to_datetime(df['tran_date']).dt.day_name()
    # Poprawna kolejność dni tygodnia
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['weekday'] = pd.Categorical(df['weekday'], categories=day_order, ordered=True)

    # Grupowanie sprzedaży wg dni tygodnia i kanałów sprzedaży
    sales_by_weekday = df.groupby(['weekday', 'Store_type'], observed=True)['total_amt'].sum().unstack()

    # Znalezienie najlepszego dnia sprzedaży dla każdego kanału sprzedaży
    max_sales_by_store = sales_by_weekday.idxmax().reset_index()
    max_sales_by_store.columns = ['Store_type', 'Best_Sales_Day']

    # Tworzenie wykresu słupkowego
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

    # Tworzenie tabeli z najlepszym dniem sprzedaży dla każdego kanału
    sales_table = html.Table(
        children=[
            html.Tr([html.Th("Kanał sprzedaży"), html.Th("Najlepszy dzień sprzedaży")])] +
            [html.Tr([html.Td(row['Store_type']), html.Td(row['Best_Sales_Day'])])
             for _, row in max_sales_by_store.iterrows()],
        style={
            'width': '60%',
            'margin': '20px auto',
            'border': '1px solid black',
            'border-collapse': 'collapse',
            'text-align': 'center',
            'backgroundColor': '#EFEFEF'
        }
    )

    # Sekcja szczegółów klientów
    customer_details = html.Div(
        [
            html.H4('Wybierz kanał sprzedaży:', style={'color': 'black'}),
            dcc.Dropdown(
                id='store-type-dropdown',
                options=[{'label': store, 'value': store} for store in df['Store_type'].unique()],
                value=df['Store_type'].unique()[0],
                style={
                    'backgroundColor': '#FFFFFF',
                    'color': 'black',
                    'border': '1px solid black',
                    'borderRadius': '5px',
                    'padding': '5px'
                }
            ),
            html.Div(id='customer-details', style={'margin-top': '20px', 'color': 'black'})
        ],
        style={'margin': '20px'}
    )

    # Layout zakładki
    layout = html.Div([
        html.H1('Kanały sprzedaży', style={
            'text-align': 'center', 
            'color': 'black',
            'margin-bottom': '20px'
        }),
        dcc.Graph(figure=bar_fig, style={'margin-bottom': '30px'}),
        html.H4("Najlepsze dni sprzedaży dla kanałów sprzedaży:", style={
            'text-align': 'center', 
            'color': 'black',
            'margin-bottom': '10px'
        }),
        sales_table,
        customer_details
    ], style={
        'backgroundColor': '#F0F8FF',
        'padding': '20px',
        'border': '2px solid #000080',
        'borderRadius': '10px'
    })

    return layout

