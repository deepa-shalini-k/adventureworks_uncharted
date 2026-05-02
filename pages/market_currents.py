"""
Market Currents - Bubble Map for Geographic Order Distribution
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
dash.register_page(__name__, path='/market-currents', name='Market Currents')

# Load data
data_dir = Path(__file__).parent.parent / 'data'
sales_df = pd.read_csv(data_dir / 'Sales.csv')
date_df = pd.read_csv(data_dir / 'Date.csv')
territory_df = pd.read_csv(data_dir / 'Sales Territory.csv')
product_df = pd.read_csv(data_dir / 'Product.csv')
customer_df = pd.read_csv(data_dir / 'Customer.csv')
reseller_df = pd.read_csv(data_dir / 'Reseller.csv')


def create_bubble_map(sales_merged, is_dark=True, region='World'):
    """
    Create a bubble map showing order intensity by city.
    
    Args:
        sales_merged: Pre-filtered and merged sales dataframe
        is_dark: Whether dark theme is active
        region: Geographic region to zoom into ('World', 'North America', 'Europe', 'Pacific')
    
    Returns:
        plotly.graph_objects.Figure
    """
    
    # Theme-based colors
    bg_color = "#242424" if is_dark else "#ffffff"
    text_color = "#ffffff" if is_dark else "#000000"
    
    # Combine customer and reseller location data
    location_data = []
    
    # B2C orders (from customers)
    b2c_sales = sales_merged[sales_merged['CustomerKey'] != -1].copy()
    if not b2c_sales.empty:
        b2c_locations = b2c_sales.groupby(['City_customer', 'Latitude_customer', 'Longitude_customer']).agg(
            order_count=('SalesOrderLineKey', 'count'),
            total_revenue=('Sales Amount', 'sum')
        ).reset_index()
        b2c_locations.rename(columns={
            'City_customer': 'City',
            'Latitude_customer': 'Latitude',
            'Longitude_customer': 'Longitude'
        }, inplace=True)
        b2c_locations['Channel'] = 'B2C'
        location_data.append(b2c_locations)
    
    # B2B orders (from resellers)
    b2b_sales = sales_merged[sales_merged['ResellerKey'] != -1].copy()
    if not b2b_sales.empty:
        b2b_locations = b2b_sales.groupby(['City_reseller', 'Latitude_reseller', 'Longitude_reseller']).agg(
            order_count=('SalesOrderLineKey', 'count'),
            total_revenue=('Sales Amount', 'sum')
        ).reset_index()
        b2b_locations.rename(columns={
            'City_reseller': 'City',
            'Latitude_reseller': 'Latitude',
            'Longitude_reseller': 'Longitude'
        }, inplace=True)
        b2b_locations['Channel'] = 'B2B'
        location_data.append(b2b_locations)
    
    # Combine all location data
    if location_data:
        all_locations = pd.concat(location_data, ignore_index=True)
        
        # Aggregate by city (combining B2B and B2C for same cities)
        city_agg = all_locations.groupby(['City', 'Latitude', 'Longitude']).agg(
            order_count=('order_count', 'sum'),
            total_revenue=('total_revenue', 'sum')
        ).reset_index()
    else:
        # Empty dataframe if no data
        city_agg = pd.DataFrame(columns=['City', 'Latitude', 'Longitude', 'order_count', 'total_revenue'])
    
    # Remove any rows with missing coordinates
    city_agg = city_agg.dropna(subset=['Latitude', 'Longitude'])
    
    # Create bubble map
    fig = go.Figure()
    
    if not city_agg.empty:
        # Calculate bubble sizes (normalize to reasonable range)
        max_orders = city_agg['order_count'].max()
        min_orders = city_agg['order_count'].min()
        
        # Scale bubble sizes between 8 and 40
        if max_orders > min_orders:
            city_agg['bubble_size'] = 8 + (city_agg['order_count'] - min_orders) / (max_orders - min_orders) * 32
        else:
            city_agg['bubble_size'] = 20
        
        # Add bubble markers
        fig.add_trace(go.Scattergeo(
            lon=city_agg['Longitude'],
            lat=city_agg['Latitude'],
            text=city_agg['City'],
            mode='markers',
            marker=dict(
                size=city_agg['bubble_size'],
                color=city_agg['order_count'],
                colorscale=[
                    [0, '#7c6bff'],      # Purple for low
                    [0.5, '#06d6a0'],    # Teal for medium
                    [1, '#ff6b6b']       # Red for high
                ],
                colorbar=dict(
                    title=dict(
                        text="Order<br>Count",
                        font=dict(
                            family="DM Sans, sans-serif",
                            size=12,
                            color=text_color
                        )
                    ),
                    tickfont=dict(
                        family="DM Sans, sans-serif",
                        color=text_color
                    ),
                    thickness=15,
                    len=0.7,
                ),
                line=dict(
                    width=1,
                    color='rgba(255, 255, 255, 0.3)'
                ),
                opacity=0.85,
                sizemode='diameter'
            ),
            customdata=city_agg[['order_count', 'total_revenue']].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "──────────────────<br>"
                "Orders:     <b>%{customdata[0]:,}</b><br>"
                "Revenue:    <b>$%{customdata[1]:,.0f}</b><br>"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                font_color="#ffffff",
                bgcolor="#1a1d2e",
                bordercolor="#7c6bff",
                font=dict(
                    size=12,
                    family="DM Sans, sans-serif"
                ),
            ),
        ))
    
    # Region-specific map settings
    region_settings = {
        'World': {
            'scope': 'world',
            'projection_type': 'natural earth',
        },
        'North America': {
            'scope': 'north america',
            'projection_type': 'natural earth',
        },
        'Europe': {
            'scope': 'europe',
            'projection_type': 'natural earth',
        },
        'Pacific': {
            'scope': 'world',
            'projection_type': 'natural earth',
            'center': {'lat': -25, 'lon': 135},
            'projection_scale': 2.5,
        },
    }
    
    # Get settings for selected region
    geo_settings = region_settings.get(region, region_settings['World'])
    
    # Base geo configuration
    geo_config = dict(
        showland=True,
        landcolor='#1a1d2e' if is_dark else '#f5f5f5',
        coastlinecolor='#444' if is_dark else '#ccc',
        showocean=True,
        oceancolor='#141824' if is_dark else '#e8f4f8',
        showcountries=True,
        countrycolor='#555' if is_dark else '#ddd',
        countrywidth=0.5,
        showlakes=True,
        lakecolor='#141824' if is_dark else '#e8f4f8',
        bgcolor=bg_color,
    )
    
    # Merge region-specific settings
    geo_config.update(geo_settings)
    
    # Update layout
    fig.update_layout(
        geo=geo_config,
        margin=dict(t=10, b=10, l=10, r=10),
        height=650,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(
            family="DM Sans, sans-serif",
            color=text_color
        ),
    )
    
    return fig


layout = dmc.Container([
    dmc.Title("Market Currents", order=3, mb="lg"),
    
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
                                dmc.AccordionControl("How to read this map", style={"fontSize": "0.875rem"}),
                                dmc.AccordionPanel(
                                    dmc.Stack([
                                        dmc.Text("• Each bubble represents a city with orders", size="xs"),
                                        dmc.Text("• Bubble size indicates the number of orders from that location", size="xs"),
                                        dmc.Text("• Bubble color shows order intensity (purple = low, teal = medium, red = high)", size="xs"),
                                        dmc.Text("• Hover over bubbles to see detailed order count and revenue", size="xs"),
                                        dmc.Text("• Use the map controls to zoom and pan around the globe", size="xs"),
                                    ], gap="xs")
                                ),
                            ],
                            value="guide",
                        ),
                    ],
                ),
                
                # Region selector - centered above map
                dmc.Center([
                    dmc.SegmentedControl(
                        id="region-selector",
                        data=[
                            {"value": "World", "label": "World"},
                            {"value": "North America", "label": "North America"},
                            {"value": "Europe", "label": "Europe"},
                            {"value": "Pacific", "label": "Pacific"},
                        ],
                        value="World",
                        size="sm",
                        color="violet",
                        radius="xl",
                    ),
                ], mb="md"),
                
                # Bubble map container
                dcc.Loading(
                    type="circle",
                    children=html.Div(id='bubble-map-container', style={'width': '100%'}),
                ),
                
                # Data Table Section
                dmc.Divider(mt="xl", mb="md"),
                dmc.Title("Source Data", order=5, mb="md"),
                html.Div(id='market-data-table', style={'width': '100%'}),
                
            ], p="lg", withBorder=True),
        ], span=12),
    ]),
    
], fluid=True, size="xl")


# Callback to update bubble map based on filters, region, and theme
@callback(
    Output('bubble-map-container', 'children'),
    Output('market-data-table', 'children'),
    Input('global-filters', 'data'),
    Input('region-selector', 'value'),
    Input('color-scheme-toggle', 'checked')
)
def update_bubble_map(filters, selected_region, is_dark):
    # If no filters, use all data
    if not filters:
        filters = {}
    
    # Apply filters using the utility function
    filtered_data = apply_global_filters(sales_df, date_df, territory_df, product_df, filters)
    
    # Merge with customer and reseller data for location info
    # Add customer location data
    filtered_with_customer = filtered_data.merge(
        customer_df[['CustomerKey', 'City', 'Latitude', 'Longitude']],
        on='CustomerKey',
        how='left',
        suffixes=('', '_customer')
    )
    
    # Add reseller location data
    filtered_with_locations = filtered_with_customer.merge(
        reseller_df[['ResellerKey', 'City', 'Latitude', 'Longitude']],
        on='ResellerKey',
        how='left',
        suffixes=('_customer', '_reseller')
    )
    
    # Create aggregated data for the table (similar to what's in create_bubble_map)
    location_data = []
    
    # B2C orders (from customers)
    b2c_sales = filtered_with_locations[filtered_with_locations['CustomerKey'] != -1].copy()
    if not b2c_sales.empty:
        b2c_locations = b2c_sales.groupby(['City_customer']).agg(
            Order_Count=('SalesOrderLineKey', 'count'),
            Total_Revenue=('Sales Amount', 'sum')
        ).reset_index()
        b2c_locations.rename(columns={'City_customer': 'City'}, inplace=True)
        b2c_locations['Channel'] = 'B2C'
        location_data.append(b2c_locations)
    
    # B2B orders (from resellers)
    b2b_sales = filtered_with_locations[filtered_with_locations['ResellerKey'] != -1].copy()
    if not b2b_sales.empty:
        b2b_locations = b2b_sales.groupby(['City_reseller']).agg(
            Order_Count=('SalesOrderLineKey', 'count'),
            Total_Revenue=('Sales Amount', 'sum')
        ).reset_index()
        b2b_locations.rename(columns={'City_reseller': 'City'}, inplace=True)
        b2b_locations['Channel'] = 'B2B'
        location_data.append(b2b_locations)
    
    # Combine all location data for table
    if location_data:
        all_locations = pd.concat(location_data, ignore_index=True)
        all_locations = all_locations.sort_values('Total_Revenue', ascending=False)
    else:
        all_locations = pd.DataFrame(columns=['City', 'Channel', 'Order_Count', 'Total_Revenue'])
    
    # Create the bubble map with theme and region
    fig = create_bubble_map(filtered_with_locations, is_dark=is_dark, region=selected_region)
    
    # Create data table
    data_table = create_data_table(all_locations, is_dark=is_dark, page_size=10, max_height='400px')
    
    # Return plot and table
    return dcc.Graph(figure=fig, style={'width': '100%'}, config={'displayModeBar': True}), data_table
