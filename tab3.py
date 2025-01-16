import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

def render_tab(df):
    df['weekday'] = pd.to_datetime(df['tran_date']).dt.day_name()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['weekday'] = pd.Categorical(df['weekday'], categories=day_order, ordered=True)

    sales_by_weekday = df.groupby(['weekday', 'Store_type'], observed=True)['total_amt'].sum().unstack()

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

    customer_stats = df.groupby('Store_type').agg(
        customer_count=('cust_id', 'nunique'),  
        transaction_count=('transaction_id', 'nunique'), 
        total_sales=('total_amt', 'sum')  
    ).reset_index()
    
    customer_stats['transaction_count'] = customer_stats['transaction_count'].fillna(0)
    customer_stats['total_sales'] = customer_stats['total_sales'].fillna(0)

    customer_stats['transaction_count'] = customer_stats['transaction_count'].apply(lambda x: x if x > 0 else 1)

    customer_fig = go.Figure()

    customer_fig.add_trace(go.Bar(
        x=customer_stats['Store_type'],
        y=customer_stats['transaction_count'],
        name="Liczba transakcji",
        marker_color='rgba(255, 99, 132, 0.6)',  
        yaxis="y2"  
    ))

    customer_fig.add_trace(go.Bar(
        x=customer_stats['Store_type'],
        y=customer_stats['total_sales'] / 1000, 
        name="Suma sprzedaży (tys.)",
        marker_color='rgba(54, 162, 235, 0.6)' 
    ))

    customer_fig.update_layout(
        barmode='group',
        title='Transakcje i sprzedaż według kanałów sprzedaży',
        xaxis_title="Kanał sprzedaży",
        yaxis=dict(
            title="Suma sprzedaży (tys.)",
            titlefont=dict(color='rgba(54, 162, 235, 0.6)'),
            tickfont=dict(color='rgba(54, 162, 235, 0.6)'),
            tickformat=",",
        ),
        yaxis2=dict(
            title="Liczba transakcji",
            titlefont=dict(color='rgba(255, 99, 132, 0.6)'),
            tickfont=dict(color='rgba(255, 99, 132, 0.6)'),
            overlaying="y",
            side="right"
        ),
        legend=dict(
            title="Legenda",
            x=0.5,
            xanchor="center",
            y=-0.3,
            orientation="h"
        ),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(color='black'),
        margin=dict(l=30, r=30, t=50, b=80)
    )
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

    layout = html.Div([
        html.H1('Kanały sprzedaży', style={
            'text-align': 'center', 
            'color': 'black',
            'margin-bottom': '20px'
        }),
        dcc.Graph(id='bar-sales-weekday', figure=bar_fig, style={'margin-bottom': '30px'}),
        html.H4("Transakcje i sprzedaż dla kanałów sprzedaży:", style={
            'text-align': 'center', 
            'color': 'black',
            'margin-bottom': '10px'
        }),
        dcc.Graph(id='channel-sales', figure=customer_fig),
        customer_details
    ], style={
        'backgroundColor': '#F0F8FF',
        'padding': '20px',
        'border': '2px solid #000080',
        'borderRadius': '10px'
    })

    return layout
