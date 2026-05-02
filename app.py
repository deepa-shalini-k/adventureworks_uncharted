"""
Appshell with header and  navbar that collapses on mobile.  Includes a theme switch.
"""

import dash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc, html, Dash, Input, Output, State, callback, clientside_callback, page_container

app = Dash(use_pages=True, suppress_callback_exceptions=True)

theme_toggle = dmc.Switch(
    offLabel=DashIconify(
        icon="radix-icons:moon", width=15, color= "var(--mantine-color-yellow-8)"
    ),
    onLabel=DashIconify(
        icon="radix-icons:sun",
        width=15,
        color= "var(--mantine-color-yellow-6)",
    ),
    id="color-scheme-toggle",
    persistence=True,
    color="grey",
)

layout = dmc.AppShell(
    [
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Group(
                        [
                            dmc.Burger(
                                id="burger",
                                size="sm",
                                hiddenFrom="sm",
                                opened=False,
                            ),
                            dmc.Group(
                                [                                    
                                    DashIconify(icon="noto-v1:woman-biking-medium-skin-tone", width=30, flip="horizontal"),
                                    dmc.Title("AdventureWorks Uncharted", c="blue", fz="18px"),
                                ]
                            )
                        ]
                    ),
                    dmc.Group(
                        [
                            dmc.Tooltip(
                                dmc.ActionIcon(
                                    DashIconify(icon="carbon:global-filters", width=20),
                                    id="aside-toggle",
                                    size="lg",
                                    variant="subtle",
                                    color="gray",
                                ),
                                label="Toggle Filters Panel",
                                position="bottom",
                            ),
                            dmc.Tooltip(
                                dmc.Anchor(
                                    dmc.ActionIcon(
                                        DashIconify(icon="mdi:github", width=30),
                                        id="github-link",
                                        size="lg",
                                        variant="subtle",
                                        color="gray"
                                    ),
                                    href="https://github.com/deepa-shalini-k/adventureworks_uncharted",
                                    target="_blank",
                                ),
                                label="View on GitHub",
                                position="bottom",
                            ),
                            dmc.Tooltip(
                                theme_toggle,
                                label="Toggle Theme",
                                position="bottom",
                            )   
                        ],
                        gap="sm",
                    ),
                ],
                justify="space-between",
                style={"flex": 1},
                h="100%",
                px="md",
            ),
        ),
        dmc.AppShellNavbar(
            id="navbar",
            children=[
                dmc.NavLink(
                    label="Overview",
                    leftSection=DashIconify(icon="carbon:dashboard", height=16),
                    id="nav-overview",
                    href="/"
                ),
                dmc.NavLink(
                    label="Product Compass",
                    leftSection=DashIconify(icon="carbon:chart-sunburst", height=16),
                    id="nav-product-compass",
                    href="/product-compass"
                ),
                dmc.NavLink(
                    label="Revenue Flows",
                    leftSection=DashIconify(icon="fluent:flow-24-regular", height=16),
                    id="nav-revenue-flows",
                    href="/revenue-flows"
                ),
                dmc.NavLink(
                    label="Channel Streams",
                    leftSection=DashIconify(icon="fluent:stream-24-regular", height=16),
                    id="nav-channel-streams",
                    href="/channel-streams"
                ),
                dmc.NavLink(
                    label="Market Currents",
                    leftSection=DashIconify(icon="mdi:earth", height=16),
                    id="nav-market-currents",
                    href="/market-currents"
                ),
                dmc.NavLink(
                    label="Seasonal Tides",
                    leftSection=DashIconify(icon="streamline-ultimate:analytics-mountain-bold", height=16),
                    id="nav-seasonal-tides",
                    href="/seasonal-tides"
                )
            ],
            p="0.7rem",
        ),
        dmc.AppShellMain(page_container),
        dmc.AppShellAside(
            id="filters-aside",
            children=[
                # Resize handle
                html.Div([
                    dmc.ActionIcon(
                        DashIconify(icon="bi:chevron-bar-left", width=16),
                        id="aside-resize-toggle",
                        size="sm",
                        variant="subtle",
                        color="gray",
                        style={
                            "position": "absolute",
                            "left": "0",
                            "top": "50%",
                            "transform": "translateY(-50%)",
                            "zIndex": 1000,
                            "borderRadius": "0 4px 4px 0",
                        }
                    ),
                ], style={"position": "relative", "height": "0"}),
                dmc.Stack([
                    dmc.Text(),
                    dmc.Text(),
                    
                    # Fiscal Year Range Slider
                    dmc.Text("Fiscal Year", size="sm", fw=500),
                    dcc.RangeSlider(
                        id='fiscal-year-filter',
                        min=2017,
                        max=2022,
                        value=[2017, 2022],
                        marks={i: {'label': f'{i}', 'style': {'color': '#228be6'}} for i in range(2017, 2023)},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": False}
                    ),
                    
                    # Fiscal Quarter Multi-Select
                    dmc.Text("Fiscal Quarter", size="sm", fw=500, mt="md"),
                    dmc.ChipGroup(
                        id='quarter-filter',
                        value=['Q1', 'Q2', 'Q3', 'Q4'],
                        multiple=True,
                        children=dmc.Stack([
                            dmc.Group([
                                dmc.Chip("Q1", value="Q1", size="sm"),
                                dmc.Chip("Q2", value="Q2", size="sm"),
                            ], gap="xs"),
                            dmc.Group([
                                dmc.Chip("Q3", value="Q3", size="sm"),
                                dmc.Chip("Q4", value="Q4", size="sm"),
                            ], gap="xs"),
                        ], gap="xs"),
                    ),
                    
                    
                    dmc.Divider(mt="md", mb="md"),
                    
                    # Region Segmented Control
                    dmc.Text("Region", size="sm", fw=500),
                    dmc.Select(
                        id='region-filter',
                        value='All',
                        data=[
                            {'label': 'All', 'value': 'All'},
                            {'label': 'North America', 'value': 'North America'},
                            {'label': 'Europe', 'value': 'Europe'},
                            {'label': 'Pacific', 'value': 'Pacific'}
                        ],
                        clearable=False,
                    ),
                    
                    # Sales Territory Multi-Select
                    dmc.Text("Sales Territory", size="sm", fw=500, mt="md"),
                    dmc.MultiSelect(
                        id='territory-filter',
                        data=[
                            'Northwest', 'Northeast', 'Central', 'Southwest', 'Southeast',
                            'Canada', 'France', 'Germany', 'Australia', 'United Kingdom'
                        ],
                        value=[],  # Empty means all selected
                        placeholder="All territories",
                        searchable=True,
                        clearable=True
                    ),
                    
                    dmc.Divider(mt="md", mb="md"),
                    
                    # Category Multi-Select
                    dmc.Text("Category", size="sm", fw=500),
                    dmc.ChipGroup(
                        id='category-filter',
                        value=['Bikes', 'Components', 'Clothing', 'Accessories'],
                        multiple=True,
                        children=[
                            dmc.Chip(cat, value=cat)
                            for cat in ['Bikes', 'Components', 'Clothing', 'Accessories']
                        ]
                    ),
                    
                    # Channel Segmented Control
                    dmc.Text("Channel", size="sm", fw=500, mt="md"),
                    dmc.SegmentedControl(
                        id='channel-filter',
                        value='All',
                        data=[
                            {'label': 'All', 'value': 'All'},
                            {'label': 'Internet', 'value': 'B2C'},
                            {'label': 'Reseller', 'value': 'B2B'}
                        ],
                        fullWidth=True
                    ),
                ], gap="xs")
            ],
            p="md",
            style={"overflowY": "auto", "overflowX": "hidden"},
        ),
    ],
    header={"height": 60},
    padding="md",
    navbar={
        "width": 250,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    },
    aside={
        "width": 300,
        "breakpoint": "md",
        "collapsed": {"mobile": True, "desktop": False},
    },
    id="appshell",
)

app.layout = dmc.MantineProvider([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='global-filters', storage_type='session'),
    dcc.Store(id='aside-width-state', data={'expanded': False}),
    layout
])

clientside_callback(
    """ 
    (switchOn) => {
       document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'dark' : 'light');  
       return window.dash_clientside.no_update
    }
    """,
    Output("color-scheme-toggle", "id"),
    Input("color-scheme-toggle", "checked"),
)

clientside_callback(
    """
    (opened, navbar) => {
        navbar.collapsed = {mobile: !opened};
        return navbar;
    }
    """,
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)

clientside_callback(
    """
    (n_clicks, widthState) => {
        if (n_clicks) {
            widthState.expanded = !widthState.expanded;
        }
        return widthState;
    }
    """,
    Output("aside-width-state", "data"),
    Input("aside-resize-toggle", "n_clicks"),
    State("aside-width-state", "data"),
)

clientside_callback(
    """
    (widthState) => {
        const icon = widthState.expanded ? "bi:chevron-bar-right" : "bi:chevron-bar-left";
        return {props: {icon: icon, width: 16}, type: 'DashIconify', namespace: 'dash_iconify'};
    }
    """,
    Output("aside-resize-toggle", "children"),
    Input("aside-width-state", "data"),
)

clientside_callback(
    """
    (switchOn) => {
        const color = switchOn ? '#fff' : '#000';
        return {props: {icon: 'mdi:github', width: 30, color: color}, type: 'DashIconify', namespace: 'dash_iconify'};
    }
    """,
    Output("github-link", "children"),
    Input("color-scheme-toggle", "checked"),
)

clientside_callback(
    """
    (toggleClicks, widthState, aside) => {
        const ctx = dash_clientside.callback_context;
        
        if (ctx.triggered.length > 0) {
            const triggerId = ctx.triggered[0].prop_id.split('.')[0];
            
            if (triggerId === 'aside-toggle') {
                const isCollapsed = aside.collapsed?.desktop || false;
                aside.collapsed = {mobile: true, desktop: !isCollapsed};
            }
            
            // Always update width based on state
            aside.width = widthState.expanded ? 450 : 300;
        }
        
        return aside;
    }
    """,
    Output("appshell", "aside"),
    Input("aside-toggle", "n_clicks"),
    Input("aside-width-state", "data"),
    State("appshell", "aside"),
)

@callback(
    Output('global-filters', 'data'),
    Input('fiscal-year-filter', 'value'),
    Input('quarter-filter', 'value'),
    Input('region-filter', 'value'),
    Input('territory-filter', 'value'),
    Input('category-filter', 'value'),
    Input('channel-filter', 'value'),
)
def update_global_filters(fiscal_years, quarters, region, territories, categories, channel):
    return {
        'fiscal_years': fiscal_years,
        'quarters': quarters,
        'region': region,
        'territories': territories,
        'categories': categories,
        'channel': channel
    }

@callback(
    Output('nav-overview', 'active'),
    Output('nav-product-compass', 'active'),
    Output('nav-revenue-flows', 'active'),
    Output('nav-channel-streams', 'active'),
    Output('nav-market-currents', 'active'),
    Output('nav-seasonal-tides', 'active'),
    Input('url', 'pathname')
)
def update_active_nav(pathname):
    # Default to home page if pathname is None
    if pathname is None:
        pathname = '/'
    
    return (
        pathname == '/' or pathname == '/overview',
        pathname == '/product-compass',
        pathname == '/revenue-flows',
        pathname == '/channel-streams',
        pathname == '/market-currents',
        pathname == '/seasonal-tides'
    )

if __name__ == "__main__":
    app.run(debug=True)