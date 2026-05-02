"""
Revenue Flows - AdventureWorks Sales Flow Circos Diagram
"""

import dash
from dash import html, callback, Input, Output, dcc
import dash_mantine_components as dmc
import dash_bio
import pandas as pd
import numpy as np
from pathlib import Path

from utils.data_filters import apply_global_filters
from utils.data_table import create_data_table

# Register this page
dash.register_page(__name__, path='/revenue-flows', name='Revenue Flows')

# Load data
data_dir = Path(__file__).parent.parent / 'data'
sales_df = pd.read_csv(data_dir / 'Sales.csv')
date_df = pd.read_csv(data_dir / 'Date.csv')
territory_df = pd.read_csv(data_dir / 'Sales Territory.csv')
product_df = pd.read_csv(data_dir / 'Product.csv')
reseller_df = pd.read_csv(data_dir / 'Reseller.csv')
customer_df = pd.read_csv(data_dir / 'Customer.csv')

# Category color mapping (now source of chords)
CATEGORY_COLORS = {
    'Accessories': '#FFD700',
    'Bikes': '#FF6347',
    'Clothing': '#4682B4',
    'Components': '#32CD32'
}

# Category shortform mapping (3-letter codes)
CATEGORY_SHORTFORMS = {
    'Bikes': 'BIK',
    'Accessories': 'ACC',
    'Clothing': 'CLO',
    'Components': 'CMP'
}

# Territory color mapping
TERRITORY_COLORS = {
    'Northwest': '#1f77b4',
    'Northeast': '#ff7f0e',
    'Central': '#2ca02c',
    'Southwest': '#d62728',
    'Southeast': '#9467bd',
    'Canada': '#8c564b',
    'France': '#e377c2',
    'Germany': '#7f7f7f',
    'Australia': '#bcbd22',
    'United Kingdom': '#17becf',
}

# Territory shortform mapping (3-letter codes)
TERRITORY_SHORTFORMS = {
    'Northwest': 'NWE',
    'Northeast': 'NEA',
    'Central': 'CEN',
    'Southwest': 'SWE',
    'Southeast': 'SEA',
    'Canada': 'CAN',
    'France': 'FRA',
    'Germany': 'GER',
    'Australia': 'AUS',
    'United Kingdom': 'UK',
}

def prepare_circos_data(sales_merged):
    """
    Prepare data for Circos diagram showing:
    - Outer arc: Product Categories and Sales Territories
    - Chords: Revenue flow from Product Category to Territory
    - Chord thickness: Revenue volume
    - Secondary ring: B2B vs B2C split per territory
    
    Args:
        sales_merged: Pre-filtered and merged sales dataframe
    """
    
    # Determine B2B vs B2C: B2B has ResellerKey != -1, B2C has CustomerKey != -1
    if 'Channel' not in sales_merged.columns:
        sales_merged['Channel'] = sales_merged.apply(
            lambda row: 'B2B' if row['ResellerKey'] != -1 else 'B2C', axis=1
        )
    
    # Aggregate revenue by Territory, Category, and Channel
    territory_category = sales_merged.groupby(['Region', 'Category'])['Sales Amount'].sum().reset_index()
    territory_channel = sales_merged.groupby(['Region', 'Channel'])['Sales Amount'].sum().reset_index()
    
    # Get unique territories and categories
    territories = sorted([t for t in territory_df['Region'].unique() if t != 'Corporate HQ'])
    categories = sorted(product_df['Category'].unique())
    
    # Create layout data for Circos
    layout_data = []
    
    # Add territories to layout first (placed on right side of circle)
    for territory in territories:
        territory_total = territory_category[territory_category['Region'] == territory]['Sales Amount'].sum()
        if territory_total > 0:
            layout_data.append({
                'id': territory,
                'label': TERRITORY_SHORTFORMS.get(territory, territory),
                'len': int(territory_total / 10000),  # Scale down for visualization
                'color': TERRITORY_COLORS.get(territory, '#cccccc')
            })
    
    # Add product categories to layout second (placed on left side of circle)
    for category in categories:
        category_total = territory_category[territory_category['Category'] == category]['Sales Amount'].sum()
        if category_total > 0:
            layout_data.append({
                'id': category,
                'label': CATEGORY_SHORTFORMS.get(category, category),
                'len': int(category_total / 10000),  # Scale down for visualization
                'color': CATEGORY_COLORS.get(category, '#999999')
            })
    
    # Create chord data (flows from categories to territories)
    # Need to track cumulative positions for each block
    source_positions = {}  # Track position for each category
    target_positions = {}  # Track position for each territory
    
    chord_data = []
    for _, row in territory_category.iterrows():
        if row['Sales Amount'] > 0:
            source_id = row['Category']  # Category is now the source
            target_id = row['Region']    # Territory is now the target
            actual_revenue = row['Sales Amount']
            value = int(actual_revenue / 10000) # Scale down for visualization
            source_color = CATEGORY_COLORS.get(source_id, '#cccccc')
            
            # Get current position for source (or initialize to 0)
            source_start = source_positions.get(source_id, 0)
            source_end = source_start + value
            source_positions[source_id] = source_end
            
            # Get current position for target (or initialize to 0)
            target_start = target_positions.get(target_id, 0)
            target_end = target_start + value
            target_positions[target_id] = target_end
            
            chord_data.append({
                'source': {
                    'id': source_id,
                    'start': source_start,
                    'end': source_end
                },
                'target': {
                    'id': target_id,
                    'start': target_start,
                    'end': target_end
                },
                'value': value,
                'color': source_color,
                'source_id': source_id,
                'target_id': target_id,
                'name': f'{source_id} → {target_id}: ${actual_revenue:,.0f}'
            })
    
    # Create track data for B2B vs B2C split
    track_data = []
    for territory in territories:
        territory_data = territory_channel[territory_channel['Region'] == territory]
        b2b_amount = territory_data[territory_data['Channel'] == 'B2B']['Sales Amount'].sum()
        b2c_amount = territory_data[territory_data['Channel'] == 'B2C']['Sales Amount'].sum()
        
        if b2b_amount > 0 or b2c_amount > 0:
            track_data.append({
                'block_id': territory,
                'start': 0,
                'end': int(b2b_amount / 10000),
                'value': int(b2b_amount / 10000),
                'color': '#1E90FF'  # B2B color
            })
            track_data.append({
                'block_id': territory,
                'start': int(b2b_amount / 10000),
                'end': int((b2b_amount + b2c_amount) / 10000),
                'value': int(b2c_amount / 10000),
                'color': '#FF69B4'  # B2C color
            })
    
    return layout_data, chord_data, track_data


# Prepare initial Circos data (unfiltered)
initial_merged = sales_df.merge(
    territory_df, on='SalesTerritoryKey', how='left'
).merge(
    product_df, on='ProductKey', how='left'
)
initial_merged = initial_merged[initial_merged['Region'] != 'Corporate HQ']
initial_merged['Channel'] = initial_merged.apply(
    lambda row: 'B2B' if row['ResellerKey'] != -1 else 'B2C', axis=1
)
layout_data, chord_data, track_data = prepare_circos_data(initial_merged)

"""def create_custom_labels(layout_data, radius=360, center=400):
    # Create custom positioned labels for Circos segments
    labels = []
    cumulative = 0
    total = sum(item['len'] for item in layout_data)
    
    for item in layout_data:
        # Calculate middle angle of segment
        start_angle = (cumulative / total) * 360
        end_angle = ((cumulative + item['len']) / total) * 360
        mid_angle = (start_angle + end_angle) / 2
        
        # Convert to radians
        rad = (mid_angle - 90) * (3.14159 / 180)
        
        # Calculate position
        x = center + radius * np.cos(rad)
        y = center + radius * np.sin(rad)
        
        # Calculate rotation for perpendicular (radial) orientation
        # Subtract 90 to make text perpendicular to the arc
        rotation = mid_angle - 90
        
        # Flip text on left side so it's always readable (not upside down)
        if 90 < mid_angle < 270:
            rotation += 180
        
        labels.append(
            html.Div(
                item['label'],
                style={
                    'position': 'absolute',
                    'left': f'{x}px',
                    'top': f'{y}px',
                    'transform': f'translate(-50%, -50%) rotate({rotation}deg)',
                    'transformOrigin': 'center',
                    'fontSize': '11px',
                    'color': '#228be6',
                    'fontWeight': '500',
                    'whiteSpace': 'nowrap',
                }
            )
        )
        cumulative += item['len']
    
    return labels

# Generate custom labels
custom_labels = create_custom_labels(layout_data)"""

layout = dmc.Container([
    dmc.Title("Revenue Flows", order=3, mb="lg"),
    
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
                                        dmc.Text("• Outer arcs represent Product Categories and Sales Territories", size="xs"),
                                        dmc.Text("• Chord thickness shows revenue volume flowing from categories to territories", size="xs"),
                                        dmc.Text("• Inner ring shows B2B/Reseller (blue) vs B2C/Customer (pink) split per territory", size="xs"),
                                    ], gap="xs")
                                ),
                            ],
                            value="guide",
                        ),
                    ],
                ),
                
                dcc.Loading(
                    type="circle",
                    children=html.Div([
                        dash_bio.Circos(
                            id='circos-diagram',
                            layout=layout_data,
                            config={
                                'innerRadius': 250,
                                'outerRadius': 320,
                                'ticks': {'display': False},
                                'labels': {
                                    'display': True,
                                    'size': 12,
                                    'color': '#228be6',
                                    'radialOffset': 90,
                                    'radialDirection': 'perpendicular',
                                },
                                'tooltipContent': {
                                    'name': 'source_id'
                                }
                            },
                        tracks=[{
                            'type': 'CHORDS',
                            'data': chord_data,
                            'config': {
                                'tooltipContent': {
                                    'name': 'name'
                                },
                                'color': {'name': 'color'},
                                'opacity': 0.6,
                            }
                        },
                        {
                            'type': 'STACK',
                            'data': track_data,
                            'config': {
                                'innerRadius': 0.85,
                                'outerRadius': 0.95,
                                'thickness': 4,
                                'color': {'name': 'color'},
                            }
                        }],
                        size=800,
                    ),
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
                ),
                
                # Data Table Section
                dmc.Divider(mt="xl", mb="md"),
                dmc.Title("Source Data", order=5, mb="md"),
                html.Div(id='revenue-data-table', style={'width': '100%'}),
                
            ], p="lg", withBorder=True),
            
        ], span=12),
    ]),
    
], fluid=True, size="xl")


# Callback to update circos diagram based on filters
@callback(
    Output('circos-diagram', 'layout'),
    Output('circos-diagram', 'tracks'),
    Output('revenue-data-table', 'children'),
    Input('global-filters', 'data'),
    Input('color-scheme-toggle', 'checked')
)
def update_circos(filters, is_dark):
    # If no filters, use all data
    if not filters:
        filters = {}
    
    # Apply filters using the utility function
    filtered_data = apply_global_filters(sales_df, date_df, territory_df, product_df, filters)
    
    # Add Channel column
    filtered_data['Channel'] = filtered_data.apply(
        lambda row: 'B2B' if row['ResellerKey'] != -1 else 'B2C', axis=1
    )
    
    # Generate circos data from filtered data
    layout, chord, track = prepare_circos_data(filtered_data)
    
    # Create aggregated data for the table
    territory_category = filtered_data.groupby(['Region', 'Category', 'Channel']).agg(
        Sales_Amount=('Sales Amount', 'sum'),
        Order_Count=('SalesOrderLineKey', 'count')
    ).reset_index().sort_values('Sales_Amount', ascending=False)
    
    # Create data table
    data_table = create_data_table(territory_category, is_dark=is_dark, page_size=10, max_height='400px')
    
    # Build tracks structure for Circos component
    tracks = [
        {
            'type': 'CHORDS',
            'data': chord,
            'config': {
                'tooltipContent': {
                    'name': 'name'
                },
                'color': {'name': 'color'},
                'opacity': 0.6,
            }
        },
        {
            'type': 'STACK',
            'data': track,
            'config': {
                'innerRadius': 0.85,
                'outerRadius': 0.95,
                'thickness': 4,
                'color': {'name': 'color'}
            }
        }
    ]
    
    return layout, tracks, data_table
