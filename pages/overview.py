"""
Overview - Home page with global KPIs and business introduction
"""

import dash
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
from pathlib import Path

# Register this page as the home page
dash.register_page(__name__, path='/', name='Overview')

# Load data
data_dir = Path(__file__).parent.parent / 'data'
sales_df = pd.read_csv(data_dir / 'Sales.csv')
territory_df = pd.read_csv(data_dir / 'Sales Territory.csv')
product_df = pd.read_csv(data_dir / 'Product.csv')
reseller_df = pd.read_csv(data_dir / 'Reseller.csv')
customer_df = pd.read_csv(data_dir / 'Customer.csv')

# Calculate static KPIs (immune to global filters)
# 1. Years of Data
years_of_data = 6

# 2. Countries Served - distinct countries in territory table
countries_served = territory_df['Country'].nunique()

# 3. Unique Products - distinct SKUs in Product table
unique_products = product_df['ProductKey'].nunique()

# 4. Reseller Partners - distinct resellers
reseller_partners = reseller_df['ResellerKey'].nunique()

# 5. Cities Reached - distinct cities across Customer + Reseller tables
customer_cities = customer_df['City'].dropna().unique()
reseller_cities = reseller_df['City'].dropna().unique()
all_cities = set(customer_cities) | set(reseller_cities)
cities_reached = len(all_cities)

# 6. Total Customers - distinct CustomerKeys
total_customers = customer_df['CustomerKey'].nunique()


layout = dmc.Container([
    # Title with icon
    dmc.Group([
        DashIconify(icon="noto-v1:woman-biking-medium-skin-tone", width=48, flip="horizontal"),
        dmc.Title("AdventureWorks Uncharted", order=1),
    ], gap="md", mb="lg", align="center"),
    
    # Description text
    dmc.Text(
        "AdventureWorks sells bikes, components, clothing and accessories across 10 global territories through two competing sales channels. "
        "This application explores a $84M business over 6 fiscal years using unconventional visualizations — rarely seen in business analytics — that transform raw sales data into compelling narratives.",
        size="md",
        c="dimmed",
        mb="md",
        style={"lineHeight": 1.6}
    ),

    # KPI Section
    dmc.Paper([
        dmc.Grid([
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("Years of Data", size="xs", c="dimmed"),
                    dmc.Text(f"{years_of_data}", size="lg", fw=600),
                ], gap=0, align="center"),
            ], span={"base": 6, "sm": 4, "md": 2}),
            
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("Countries Served", size="xs", c="dimmed"),
                    dmc.Text(f"{countries_served}", size="lg", fw=600, c="blue"),
                ], gap=0, align="center"),
            ], span={"base": 6, "sm": 4, "md": 2}),
            
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("Unique Products", size="xs", c="dimmed"),
                    dmc.Text(f"{unique_products}", size="lg", fw=600, c="green"),
                ], gap=0, align="center"),
            ], span={"base": 6, "sm": 4, "md": 2}),
            
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("Reseller Partners", size="xs", c="dimmed"),
                    dmc.Text(f"{reseller_partners}", size="lg", fw=600, c="violet"),
                ], gap=0, align="center"),
            ], span={"base": 6, "sm": 4, "md": 2}),
            
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("Cities Reached", size="xs", c="dimmed"),
                    dmc.Text(f"{cities_reached:,}", size="lg", fw=600, c="orange"),
                ], gap=0, align="center"),
            ], span={"base": 6, "sm": 4, "md": 2}),
            
            dmc.GridCol([
                dmc.Stack([
                    dmc.Text("Total Customers", size="xs", c="dimmed"),
                    dmc.Text(f"{total_customers:,}", size="lg", fw=600, c="cyan"),
                ], gap=0, align="center"),
            ], span={"base": 6, "sm": 4, "md": 2}),
        ]),
    ], p="lg", withBorder=True),
    
    # Spacer
    dmc.Space(h="sm"),
    
    # Page Description Cards
    dmc.Grid([
        # Row 1 - 3 cards
        dmc.GridCol([
            dmc.Anchor([
                dmc.Paper([
                    dmc.Stack([
                        DashIconify(icon="carbon:chart-sunburst", width=20, color="var(--mantine-color-blue-6)"),
                        dmc.Text("Product Compass", size="lg", fw=600),
                        dmc.Text(
                            "Navigate product hierarchies from categories to subcategories with an interactive sunburst chart revealing sales patterns.",
                            size="sm",
                            c="dimmed",
                            style={"lineHeight": 1.5}
                        ),
                    ], gap="xs"),
                ], p="lg", withBorder=True, radius="md", style={"height": "100%"}),
            ], href="/product-compass", underline=False, c="inherit"),
        ], span={"base": 12, "sm": 6, "md": 4}),
        
        dmc.GridCol([
            dmc.Anchor([
                dmc.Paper([
                    dmc.Stack([
                        DashIconify(icon="fluent:flow-24-regular", width=20, color="var(--mantine-color-blue-6)"),
                        dmc.Text("Revenue Flows", size="lg", fw=600),
                        dmc.Text(
                            "Trace revenue pathways through territory, channel, category and product with a striking circos flow diagram.",
                            size="sm",
                            c="dimmed",
                            style={"lineHeight": 1.5}
                        ),
                    ], gap="xs"),
                ], p="lg", withBorder=True, radius="md", style={"height": "100%"}),
            ], href="/revenue-flows", underline=False, c="inherit"),
        ], span={"base": 12, "sm": 6, "md": 4}),
        
        dmc.GridCol([
            dmc.Anchor([
                dmc.Paper([
                    dmc.Stack([
                        DashIconify(icon="fluent:stream-24-regular", width=20, color="var(--mantine-color-blue-6)"),
                        dmc.Text("Channel Streams", size="lg", fw=600),
                        dmc.Text(
                            "Visualize revenue flow between B2B reseller and B2C direct channels over time with interactive stream graphs.",
                            size="sm",
                            c="dimmed",
                            style={"lineHeight": 1.5}
                        ),
                    ], gap="xs"),
                ], p="lg", withBorder=True, radius="md", style={"height": "100%"}),
            ], href="/channel-streams", underline=False, c="inherit"),
        ], span={"base": 12, "sm": 6, "md": 4}),
        
        # Row 2 - 2 cards
        dmc.GridCol([
            dmc.Anchor([
                dmc.Paper([
                    dmc.Stack([
                        DashIconify(icon="mdi:earth", width=20, color="var(--mantine-color-blue-6)"),
                        dmc.Text("Market Currents", size="lg", fw=600),
                        dmc.Text(
                            "Explore global sales distribution with a bubble map showing order volumes across territories and countries.",
                            size="sm",
                            c="dimmed",
                            style={"lineHeight": 1.5}
                        ),
                    ], gap="xs"),
                ], p="lg", withBorder=True, radius="md", style={"height": "100%"}),
            ], href="/market-currents", underline=False, c="inherit"),
        ], span={"base": 12, "sm": 6, "md": 4, "lg": 4}, offset={"md": 0, "lg": 2}),
        
        dmc.GridCol([
            dmc.Anchor([
                dmc.Paper([
                    dmc.Stack([
                        DashIconify(icon="streamline-ultimate:analytics-mountain-bold", width=20, color="var(--mantine-color-blue-6)"),
                        dmc.Text("Seasonal Tides", size="lg", fw=600),
                        dmc.Text(
                            "Discover daily revenue patterns and seasonal trends across fiscal years using ridgeline distribution plots.",
                            size="sm",
                            c="dimmed",
                            style={"lineHeight": 1.5}
                        ),
                    ], gap="xs"),
                ], p="lg", withBorder=True, radius="md", style={"height": "100%"}),
            ], href="/seasonal-tides", underline=False, c="inherit"),
        ], span={"base": 12, "sm": 6, "md": 4, "lg": 4}),
    ], gutter="md"),
], fluid=True, p="lg")
