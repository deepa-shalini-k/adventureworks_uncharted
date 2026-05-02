"""
Seasonal Tides - Ridgeline Plot for Daily Revenue Distribution Over Time
"""

import dash
from dash import html, callback, Input, Output, dcc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime
from scipy import stats

from utils.data_filters import apply_global_filters
from utils.data_table import create_data_table

# Register this page
dash.register_page(__name__, path='/seasonal-tides', name='Seasonal Tides')

# Load data
data_dir = Path(__file__).parent.parent / 'data'
sales_df = pd.read_csv(data_dir / 'Sales.csv')
date_df = pd.read_csv(data_dir / 'Date.csv')
territory_df = pd.read_csv(data_dir / 'Sales Territory.csv')
product_df = pd.read_csv(data_dir / 'Product.csv')


def create_ridgeline_chart(sales_merged, is_dark=True):
    """
    Create a ridgeline (joy) plot showing Sales Amount distribution by fiscal quarter using KDE.
    
    Args:
        sales_merged: Pre-filtered and merged sales dataframe
        is_dark: Whether dark theme is active
    
    Returns:
        plotly.graph_objects.Figure
    """
    
    # Theme-based colors
    bg_color = "#242424" if is_dark else "#ffffff"
    text_color = "#ffffff" if is_dark else "#000000"
    grid_color = "#3a3a3a" if is_dark else "#e0e0e0"
    
    # Extract fiscal year numeric for sorting and color mapping
    sales_merged['FiscalYear'] = sales_merged['Fiscal Year'].str.extract(r'FY(\d{4})')[0].astype(int)
    
    # Group by Fiscal Quarter
    quarters = sales_merged.groupby('Fiscal Quarter')['Sales Amount'].apply(list).to_dict()
    
    # Sort quarters chronologically by extracting year and quarter number
    def parse_quarter(q):
        # Format: "FY2020 Q1"
        parts = q.split()
        year = int(parts[0].replace('FY', ''))
        quarter = int(parts[1].replace('Q', ''))
        return (year, quarter)
    
    sorted_quarters = sorted(quarters.keys(), key=parse_quarter)
    
    # Color gradient: #3b82f6 (FY2017) to #06d6a0 (FY2022)
    # FY2017 -> FY2022 is a 5-year range
    color_start = np.array([59, 130, 246])    # #3b82f6 (blue)
    color_end = np.array([6, 214, 160])       # #06d6a0 (teal/green)
    
    def get_color_for_year(year):
        # Map FY2017 (2017) to FY2022 (2022)
        # Linear interpolation
        t = (year - 2017) / (2022 - 2017)
        t = np.clip(t, 0, 1)
        color = color_start + t * (color_end - color_start)
        r, g, b = color.astype(int)
        return f'rgba({r}, {g}, {b}, 0.8)'
    
    # Create figure
    fig = go.Figure()
    
    # Compute KDE for each quarter and find global max for normalization
    kde_data = []
    max_density = 0
    
    for quarter in sorted_quarters:
        sales_amounts = np.array(quarters[quarter])
        
        if len(sales_amounts) < 2:
            continue
            
        # Compute KDE
        kde = stats.gaussian_kde(sales_amounts)
        
        # Create x-axis range for KDE evaluation
        x_min = sales_amounts.min()
        x_max = sales_amounts.max()
        x_range = np.linspace(x_min, x_max, 200)
        
        # Evaluate KDE
        density = kde(x_range)
        
        max_density = max(max_density, density.max())
        
        # Extract fiscal year from quarter name
        fiscal_year = int(quarter.split()[0].replace('FY', ''))
        
        kde_data.append({
            'quarter': quarter,
            'x_range': x_range,
            'density': density,
            'fiscal_year': fiscal_year
        })
    
    # Calculate offset for 40% overlap
    # Each ridge will be offset by 0.6 * normalized_height (so they overlap by 40%)
    offset_amount = 0.6
    
    # Add ridges from bottom to top (oldest to newest)
    y_labels = []
    y_positions = []
    
    for idx, kde_info in enumerate(kde_data):
        quarter = kde_info['quarter']
        x_range = kde_info['x_range']
        density = kde_info['density']
        fiscal_year = kde_info['fiscal_year']
        
        # Normalize density to [0, 1]
        normalized_density = density / max_density
        
        # Calculate baseline and ridge values
        baseline = idx * offset_amount
        y_values = normalized_density + baseline
        
        # Get color for this fiscal year
        fill_color = get_color_for_year(fiscal_year)
        line_color = fill_color.replace('0.8', '1.0')
        
        # Create closed polygon for the ridge (baseline -> curve -> baseline)
        # Concatenate: baseline line + curve + baseline line back
        x_polygon = np.concatenate([x_range, x_range[::-1]])
        y_polygon = np.concatenate([y_values, [baseline] * len(x_range)])
        
        # Create filled area for the ridge
        fig.add_trace(go.Scatter(
            x=x_polygon,
            y=y_polygon,
            fill='toself',
            fillcolor=fill_color,
            line=dict(color=line_color, width=1.5),
            name=quarter,
            showlegend=False,
            mode='lines',
            hoverinfo='skip'
        ))
        
        # Add invisible scatter for hover (just the top curve)
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_values,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hovertemplate=(
                f"<b>{quarter}</b><br>"
                "Sales Amount: $%{x:,.0f}<br>"
                "Density: %{y:.3f}<br>"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                font_color="#ffffff",
                bgcolor="#1a1d2e",
                bordercolor=line_color,
                font_size=12,
                font_family="DM Sans, sans-serif",
            ),
        ))
        
        # Store label position (at the baseline of each ridge)
        y_labels.append(quarter)
        y_positions.append(baseline)
    
    # Update layout
    fig.update_layout(
        margin=dict(t=60, b=80, l=120, r=40),
        height=700,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        
        xaxis=dict(
            title=dict(
                text="Sales Amount ($)",
                font=dict(
                    size=14,
                    color=text_color,
                    family="DM Sans, sans-serif"
                )
            ),
            showgrid=True,
            gridcolor=grid_color,
            gridwidth=1,
            zeroline=True,
            zerolinecolor=grid_color,
            tickfont=dict(
                size=11,
                color=text_color,
                family="DM Sans, sans-serif"
            ),
            tickformat="$,.0f",
        ),
        
        yaxis=dict(
            title=None,
            showgrid=False,
            showticklabels=True,
            tickfont=dict(
                size=10,
                color=text_color,
                family="DM Sans, sans-serif"
            ),
            tickmode='array',
            tickvals=y_positions,
            ticktext=y_labels,
            range=[-0.2, len(kde_data) * offset_amount + 1.2]
        ),
        
        font=dict(
            family="DM Sans, sans-serif",
            color=text_color
        ),
    )
    
    return fig


layout = dmc.Container([
    dmc.Title("Seasonal Tides", order=3, mb="lg"),
    
    dmc.Grid([
        dmc.GridCol([
            dmc.Paper([
                # Collapsed accordion for chart reading guide
                dmc.Accordion(
                    chevronPosition="left",
                    variant="subtle",
                    #mb=0,
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("How to read this chart", style={"fontSize": "0.875rem"}),
                                dmc.AccordionPanel(
                                    dmc.Stack([
                                        dmc.Text("• Each ridge (curve) represents a fiscal quarter", size="xs"),
                                        dmc.Text("• X-axis shows the distribution of sales amounts within that quarter", size="xs"),
                                        dmc.Text("• Height/width of ridge shows probability density at that sales amount", size="xs"),
                                        dmc.Text("• Color gradient from blue (#3b82f6 for FY2017) to teal/green (#06d6a0 for FY2022)", size="xs"),
                                        dmc.Text("• Ridges overlap by ~40% to create a mountain range effect", size="xs"),
                                        dmc.Text("• Hover over ridges to see quarter details and specific values", size="xs"),
                                    ], gap="xs")
                                ),
                            ],
                            value="guide",
                        ),
                    ],
                ),
                
                # Ridgeline chart container
                dcc.Loading(
                    type="circle",
                    children=html.Div(id='ridgeline-container', style={'width': '100%'}),
                ),
                
                # Data Table Section
                dmc.Divider(mt="xl", mb="md"),
                dmc.Title("Source Data", order=5, mb="md"),
                html.Div(id='seasonal-data-table', style={'width': '100%'}),
                
            ], p="lg", withBorder=True),
        ], span=12),
    ]),
    
], fluid=True, size="xl")


# Callback to update ridgeline chart based on filters and theme
@callback(
    Output('ridgeline-container', 'children'),
    Output('seasonal-data-table', 'children'),
    Input('global-filters', 'data'),
    Input('color-scheme-toggle', 'checked')
)
def update_ridgeline(filters, is_dark):
    # If no filters, use all data
    if not filters:
        filters = {}
    
    # Apply filters using the utility function
    filtered_data = apply_global_filters(sales_df, date_df, territory_df, product_df, filters)
    
    # Create aggregated data for the table by fiscal quarter
    quarterly_stats = filtered_data.groupby('Fiscal Quarter').agg(
        Total_Revenue=('Sales Amount', 'sum'),
        Order_Count=('SalesOrderLineKey', 'count'),
        Avg_Sale_Amount=('Sales Amount', 'mean'),
        Min_Sale_Amount=('Sales Amount', 'min'),
        Max_Sale_Amount=('Sales Amount', 'max')
    ).reset_index().sort_values('Fiscal Quarter', ascending=False)
    
    # Create the ridgeline chart with theme
    fig = create_ridgeline_chart(filtered_data, is_dark=is_dark)
    
    # Create data table
    data_table = create_data_table(quarterly_stats, is_dark=is_dark, page_size=10, max_height='400px')
    
    # Return plot and table
    return dcc.Graph(figure=fig, style={'width': '100%'}), data_table
