"""
Channel Streams - Stream Graph for B2B vs B2C Revenue Over Time
"""

import dash
from dash import html, callback, Input, Output, dcc
import dash_mantine_components as dmc
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

from utils.data_filters import apply_global_filters
from utils.data_table import create_data_table

# Register this page
dash.register_page(__name__, path='/channel-streams', name='Channel Streams')

# Load data
data_dir = Path(__file__).parent.parent / 'data'
sales_df = pd.read_csv(data_dir / 'Sales.csv')
date_df = pd.read_csv(data_dir / 'Date.csv')
territory_df = pd.read_csv(data_dir / 'Sales Territory.csv')
product_df = pd.read_csv(data_dir / 'Product.csv')


def create_stream_graph(sales_merged, is_dark=True):
    """
    Create a stacked area chart (stream graph) showing B2B vs B2C revenue over time.
    
    Args:
        sales_merged: Pre-filtered and merged sales dataframe
        is_dark: Whether dark theme is active
    
    Returns:
        plotly.graph_objects.Figure
    """
    
    # Theme-based colors
    bg_color = "#242424" if is_dark else "#ffffff"
    grid_color = "#3a3a3a" if is_dark else "#e0e0e0"
    text_color = "#ffffff" if is_dark else "#000000"
    
    # Classify each sale as B2B or B2C
    sales_merged['Channel'] = sales_merged.apply(
        lambda row: 'B2B' if row['ResellerKey'] != -1 else 'B2C', 
        axis=1
    )
    
    # Convert date to datetime for proper sorting
    sales_merged['Date_parsed'] = pd.to_datetime(sales_merged['Full Date'])
    
    # Aggregate revenue by Month and Channel
    # Using MonthKey for grouping (YYYYMM format)
    monthly_channel = sales_merged.groupby(['MonthKey', 'Channel']).agg(
        revenue=('Sales Amount', 'sum')
    ).reset_index()
    
    # Pivot to get B2B and B2C as separate columns
    revenue_pivot = monthly_channel.pivot(
        index='MonthKey', 
        columns='Channel', 
        values='revenue'
    ).fillna(0).reset_index()
    
    # Create a proper date column for the x-axis
    revenue_pivot['Date'] = pd.to_datetime(revenue_pivot['MonthKey'].astype(str), format='%Y%m')
    revenue_pivot = revenue_pivot.sort_values('Date')
    
    # Ensure both B2B and B2C columns exist
    if 'B2B' not in revenue_pivot.columns:
        revenue_pivot['B2B'] = 0
    if 'B2C' not in revenue_pivot.columns:
        revenue_pivot['B2C'] = 0
    
    # Color scheme for channels
    b2c_color = '#06d6a0'  # Teal/Green for B2C (Internet)
    b2b_color = '#7c6bff'  # Purple for B2B (Reseller)
    
    # Create the stacked area chart
    fig = go.Figure()
    
    # Add B2C trace
    fig.add_trace(go.Scatter(
        x=revenue_pivot['Date'],
        y=revenue_pivot['B2C'],
        name='B2C (Internet)',
        mode='lines',
        line=dict(width=0.5, color=b2c_color, shape='spline', smoothing=1.3),
        fillcolor=b2c_color,
        fill='tonexty',
        stackgroup='one',
        hovertemplate=(
            "<b>B2C (Internet)</b><br>"
            "Date: %{x|%B %Y}<br>"
            "Revenue: $%{y:,.0f}<br>"
            "<extra></extra>"
        ),
    ))
    
    # Add B2B trace
    fig.add_trace(go.Scatter(
        x=revenue_pivot['Date'],
        y=revenue_pivot['B2B'],
        name='B2B (Reseller)',
        mode='lines',
        line=dict(width=0.5, color=b2b_color, shape='spline', smoothing=1.3),
        fillcolor=b2b_color,
        fill='tonexty',
        stackgroup='one',
        hovertemplate=(
            "<b>B2B (Reseller)</b><br>"
            "Date: %{x|%B %Y}<br>"
            "Revenue: $%{y:,.0f}<br>"
            "<extra></extra>"
        ),
    ))
    
    # Update layout with theme-aware colors
    fig.update_layout(
        margin=dict(t=40, b=60, l=60, r=40),
        height=650,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(
            family="DM Sans, sans-serif",
            size=12,
            color=text_color,
        ),
        xaxis=dict(
            title="Time Period",
            showgrid=True,
            gridcolor=grid_color,
            linecolor=grid_color,
            color=text_color,
            tickformat='%b %Y',
        ),
        yaxis=dict(
            title="Revenue ($)",
            showgrid=True,
            gridcolor=grid_color,
            linecolor=grid_color,
            color=text_color,
            tickformat='$,.0f',
        ),
        hovermode='x unified',
        hoverlabel=dict(
            font_color="#ffffff",
            bgcolor="#1a1d2e",
            bordercolor="#7c6bff",
            font_size=12,
            font_family="DM Sans, sans-serif",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=13),
            bgcolor='rgba(0,0,0,0)',
        ),
    )
    
    return fig


layout = dmc.Container([
    dmc.Title("Channel Streams", order=3, mb="lg"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Paper([
                # Collapsed accordion for chart reading guide
                dmc.Accordion(
                    chevronPosition="left",
                    variant="subtle",
                    mb="sm",
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("How to read this chart", style={"fontSize": "0.875rem"}),
                                dmc.AccordionPanel(
                                    dmc.Stack([
                                        dmc.Text("• This stream graph shows revenue distribution between B2B (Reseller) and B2C (Internet) channels over time", size="xs"),
                                        dmc.Text("• The stacked areas represent cumulative revenue, with each channel's contribution visible", size="xs"),
                                        dmc.Text("• Hover over the chart to see exact revenue values for each channel by month", size="xs"),
                                        dmc.Text("• Use global filters to analyze specific time periods, territories, or product categories", size="xs"),
                                    ], gap="xs")
                                ),
                            ],
                            value="guide",
                        ),
                    ],
                ),
                
                # Stream graph container
                dcc.Loading(
                    type="circle",
                    children=html.Div(id='stream-graph-container', style={'width': '100%'}),
                ),
                
                # Data Table Section
                dmc.Divider(mt="xl", mb="md"),
                dmc.Title("Source Data", order=5, mb="md"),
                html.Div(id='channel-data-table', style={'width': '100%'}),
                
            ], p="lg", withBorder=True),
        ], span=12),
    ]),
    
], fluid=True, size="xl")


# Callback to update stream graph based on filters and theme
@callback(
    Output('stream-graph-container', 'children'),
    Output('channel-data-table', 'children'),
    Input('global-filters', 'data'),
    Input('color-scheme-toggle', 'checked')
)
def update_stream_graph(filters, is_dark):
    # If no filters, use all data
    if not filters:
        filters = {}
    
    # Apply filters using the utility function
    filtered_data = apply_global_filters(sales_df, date_df, territory_df, product_df, filters)
    
    # Classify each sale as B2B or B2C
    filtered_data['Channel'] = filtered_data.apply(
        lambda row: 'B2B' if row['ResellerKey'] != -1 else 'B2C', 
        axis=1
    )
    
    # Aggregate revenue by Month and Channel for the table
    monthly_channel = filtered_data.groupby(['MonthKey', 'Channel']).agg(
        Revenue=('Sales Amount', 'sum'),
        Order_Count=('SalesOrderLineKey', 'count')
    ).reset_index().sort_values('MonthKey', ascending=False)
    
    # Create the stream graph with theme
    fig = create_stream_graph(filtered_data, is_dark=is_dark)
    
    # Create data table
    data_table = create_data_table(monthly_channel, is_dark=is_dark, page_size=10, max_height='400px')
    
    # Return the graph and table
    return dcc.Graph(figure=fig, style={'width': '100%'}, config={'displayModeBar': False}), data_table
