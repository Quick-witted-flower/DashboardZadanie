import dash
from dash import dcc, html
import plotly.graph_objs as go

def render_tab(df):
    grouped_pie = df[df['total_amt'] > 0].groupby('prod_cat')['total_amt'].sum()
    pie_fig = go.Figure(
        go.Pie(
            labels=grouped_pie.index,
            values=grouped_pie.values,
            hoverinfo='label+percent',
            textinfo='percent'
        )
    )
    pie_fig.update_layout(title='Udział grup produktów w sprzedaży')

    layout = html.Div([
        html.H1('Specyfika produktów', style={'text-align': 'center'}),
        
        html.Div([
            dcc.Graph(id='pie-prod-cat', figure=pie_fig),
            
            html.Div([
                dcc.Dropdown(
                    id='prod_dropdown',
                    options=[
                        {'label': prod_cat, 'value': prod_cat}
                        for prod_cat in df['prod_cat'].unique()
                    ],
                    value=df['prod_cat'].unique()[0],  
                    style={'width': '100%'}
                ),
                dcc.Graph(id='barh-prod-subcat') 
            ], style={'width': '50%'})
        ], style={'display': 'flex', 'flex-direction': 'row'})
    ])

    return layout
