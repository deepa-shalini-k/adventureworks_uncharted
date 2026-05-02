"""
Product Compass - Sunburst Chart for Product Category Analysis
"""

import dash
from dash import html, callback, Input, Output, dcc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

from utils.data_filters import apply_global_filters
from utils.data_table import create_data_table

# Register this page
dash.register_page(__name__, path='/product-compass', name='Product Compass')

# Load data
data_dir = Path(__file__).parent.parent / 'data'
sales_df = pd.read_csv(data_dir / 'Sales.csv')
date_df = pd.read_csv(data_dir / 'Date.csv')
territory_df = pd.read_csv(data_dir / 'Sales Territory.csv')
product_df = pd.read_csv(data_dir / 'Product.csv')

# Category colors
CATEGORY_COLORS = {
    'Bikes': '#7c6bff',
    'Components': '#06d6a0',
    'Clothing': '#ff6b6b',
    'Accessories': '#ffd166'
}


def create_sunburst_chart(sales_merged, selected_metric='order_count', is_dark=True):
    """
    Create a sunburst chart showing product categories and subcategories.
    
    Args:
        sales_merged: Pre-filtered and merged sales dataframe
        selected_metric: 'order_count', 'total_revenue', or 'avg_order_value'
        is_dark: Whether dark theme is active
    
    Returns:
        plotly.graph_objects.Figure
    """
    
    # Theme-based colors
    bg_color = "#242424" if is_dark else "#ffffff"
    line_color = "#242424" if is_dark else "#e0e0e0"
    text_color = "#ffffff" if is_dark else "#000000"
    
    # Aggregate data by Category and Subcategory
    agg = sales_merged.groupby(["Category", "Subcategory"]).agg(
        order_count=("SalesOrderLineKey", "count"),
        total_revenue=("Sales Amount", "sum"),
        avg_order_value=("Sales Amount", "mean")
    ).reset_index()
    
    # Build sunburst data arrays
    labels = []
    parents = []
    values = []
    customdata = []
    colors = []
    
    # Category nodes (inner ring)
    for cat in sorted(agg["Category"].unique()):
        cat_data = agg[agg["Category"] == cat]
        labels.append(cat)
        parents.append("")  # Parent is empty (root)
        values.append(cat_data[selected_metric].sum())
        
        # Category-level customdata (aggregate from subcategories)
        cat_orders = int(cat_data["order_count"].sum())
        cat_revenue = cat_data["total_revenue"].sum()
        cat_avg = cat_data["avg_order_value"].mean()
        customdata.append([cat_orders, cat_revenue, cat_avg, cat, cat])
        colors.append(CATEGORY_COLORS.get(cat, '#888888'))
    
    # Subcategory nodes (outer ring)
    for _, row in agg.iterrows():
        labels.append(row["Subcategory"])
        parents.append(row["Category"])
        values.append(row[selected_metric])
        customdata.append([
            int(row["order_count"]),
            row["total_revenue"],
            row["avg_order_value"],
            row["Category"],
            row["Subcategory"],
        ])
        # Subcategory inherits parent color
        colors.append(CATEGORY_COLORS.get(row["Category"], '#888888'))
    
    # Create sunburst figure
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        
        marker=dict(
            colors=colors,
            line=dict(color=line_color, width=2)
        ),
        
        textfont=dict(
            family="DM Sans, sans-serif",
            size=12,
            color=text_color,
        ),
        
        insidetextorientation="radial",
        
        customdata=customdata,
        hovertemplate=(
            "<b>%{customdata[4]}</b><br>"
            "<span style='color:#7986cb'>%{customdata[3]}</span><br>"
            "──────────────────<br>"
            "Orders:     <b>%{customdata[0]:,}</b><br>"
            "Revenue:    <b>$%{customdata[1]:,.0f}</b><br>"
            "Avg Order:  <b>$%{customdata[2]:,.0f}</b><br>"
            "<extra></extra>"
        ),
        
        hoverlabel=dict(
            font_color="#ffffff",
            bgcolor="#1a1d2e",
            bordercolor="#7c6bff",
            font_size=12,
            font_family="DM Sans, sans-serif",
        ),
    ))
    
    # Update layout with theme-aware colors
    fig.update_layout(
        margin=dict(t=40, b=40, l=40, r=40),
        height=620,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
    )
    
    return fig


# Prepare initial data (unfiltered) for stats
initial_merged = sales_df.merge(
    product_df, on='ProductKey', how='left'
).merge(
    date_df, left_on='OrderDateKey', right_on='DateKey', how='left'
).merge(
    territory_df, on='SalesTerritoryKey', how='left'
)
initial_merged = initial_merged[initial_merged['Region'] != 'Corporate HQ']

# Calculate initial statistics
initial_agg = initial_merged.groupby(["Category", "Subcategory"]).agg(
    order_count=("SalesOrderLineKey", "count"),
    total_revenue=("Sales Amount", "sum"),
    avg_order_value=("Sales Amount", "mean")
).reset_index()

total_orders = initial_agg["order_count"].sum()
total_revenue = initial_agg["total_revenue"].sum()
unique_subcats = initial_agg["Subcategory"].nunique()
avg_order = initial_agg["avg_order_value"].mean()

layout = dmc.Container([
    dmc.Title("Product Compass", order=3, mb="lg"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Paper([
                # Summary stats - TOP SECTION
                dmc.Stack([
                    dmc.Grid([
                        dmc.GridCol([
                            dmc.Stack([
                                dmc.Text("Total Orders", size="xs", c="dimmed"),
                                dmc.Text(id='stat-total-orders', children=f"{int(total_orders):,}", size="lg", fw=600),
                            ], gap=0, align="center"),
                        ], span=3),
                        dmc.GridCol([
                            dmc.Stack([
                                dmc.Text("Total Revenue", size="xs", c="dimmed"),
                                dmc.Text(id='stat-total-revenue', children=f"${total_revenue:,.0f}", size="lg", fw=600, c="green"),
                            ], gap=0, align="center"),
                        ], span=3),
                        dmc.GridCol([
                            dmc.Stack([
                                dmc.Text("Subcategories", size="xs", c="dimmed"),
                                dmc.Text(id='stat-subcats', children=f"{unique_subcats}", size="lg", fw=600),
                            ], gap=0, align="center"),
                        ], span=3),
                        dmc.GridCol([
                            dmc.Stack([
                                dmc.Text("Avg Order Value", size="xs", c="dimmed"),
                                dmc.Text(id='stat-avg-order', children=f"${avg_order:,.0f}", size="lg", fw=600, c="blue"),
                            ], gap=0, align="center"),
                        ], span=3),
                    ]),
                    dmc.Divider(mt="md", mb="sm"),
                ], gap="xs"),
                
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
                                        dmc.Text("• Inner ring shows product categories", size="xs"),
                                        dmc.Text("• Outer ring shows subcategories within each category", size="xs"),
                                        dmc.Text("• Size of each segment reflects the selected metric (Orders/Revenue/Avg Order Value)", size="xs"),
                                        dmc.Text("• Click segments to drill down, click center to zoom out", size="xs"),
                                        dmc.Text("• Hover over segments to see detailed statistics", size="xs"),
                                    ], gap="xs")
                                ),
                            ],
                            value="guide",
                        ),
                    ],
                ),
                
                # Metric toggle - centered above chart
                dmc.Center([
                    dmc.SegmentedControl(
                        id="sunburst-metric-toggle",
                        data=[
                            {"value": "order_count", "label": "Orders"},
                            {"value": "total_revenue", "label": "Revenue"},
                            {"value": "avg_order_value", "label": "Avg Order Value"},
                        ],
                        value="order_count",
                        size="sm",
                        color="violet",
                        radius="xl",
                    ),
                ], mb="md"),
                
                # Sunburst chart container
                dcc.Loading(
                    type="circle",
                    children=html.Div(id='sunburst-container', style={'width': '100%'}),
                ),
                
                # Data Table Section
                dmc.Divider(mt="xl", mb="md"),
                dmc.Title("Source Data", order=5, mb="md"),
                html.Div(id='product-data-table', style={'width': '100%'}),
                
            ], p="lg", withBorder=True),
        ], span=12),
    ]),
    
], fluid=True, size="xl")


# Callback to update sunburst chart and statistics based on filters, metric toggle, and theme
@callback(
    Output('sunburst-container', 'children'),
    Output('stat-total-orders', 'children'),
    Output('stat-total-revenue', 'children'),
    Output('stat-subcats', 'children'),
    Output('stat-avg-order', 'children'),
    Output('product-data-table', 'children'),
    Input('global-filters', 'data'),
    Input('sunburst-metric-toggle', 'value'),
    Input('color-scheme-toggle', 'checked')
)
def update_sunburst(filters, selected_metric, is_dark):
    # If no filters, use all data
    if not filters:
        filters = {}
    
    # Apply filters using the utility function (already includes product merge)
    filtered_data = apply_global_filters(sales_df, date_df, territory_df, product_df, filters)
    
    # Calculate statistics
    agg = filtered_data.groupby(["Category", "Subcategory"]).agg(
        order_count=("SalesOrderLineKey", "count"),
        total_revenue=("Sales Amount", "sum"),
        avg_order_value=("Sales Amount", "mean")
    ).reset_index()
    
    total_ord = agg["order_count"].sum()
    total_rev = agg["total_revenue"].sum()
    n_subcats = agg["Subcategory"].nunique()
    avg_ord = agg["avg_order_value"].mean()
    
    # Create the sunburst chart with theme
    fig = create_sunburst_chart(filtered_data, selected_metric, is_dark=is_dark)
    
    # Create data table with the aggregated data used for the chart
    data_table = create_data_table(agg, is_dark=is_dark, page_size=10, max_height='400px')
    
    # Return plot, updated statistics, and data table
    return (
        dcc.Graph(figure=fig, style={'width': '100%'}),
        f"{int(total_ord):,}",
        f"${total_rev:,.0f}",
        f"{n_subcats}",
        f"${avg_ord:,.0f}",
        data_table
    )
