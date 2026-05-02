"""
Reusable AG Grid Data Table Component
Provides styled AG Grid tables that match the app's theme (dark/light mode).
"""

import dash_ag_grid as dag
import pandas as pd
from dash import html


def create_data_table(df, is_dark=True, page_size=10, max_height='400px'):
    """
    Create a themed AG Grid data table component.
    
    Args:
        df: pandas DataFrame to display
        is_dark: Whether dark theme is active
        page_size: Number of rows per page (default 10)
        max_height: Maximum height of the table (default '400px')
    
    Returns:
        dash_ag_grid.AgGrid component wrapped in a div with theme-specific styling
    """
    
    # Theme selection - AG Grid themes that match our app
    grid_theme = "ag-theme-quartz-dark" if is_dark else "ag-theme-quartz"
    
    # Define column definitions with formatting
    column_defs = []
    for col in df.columns:
        col_def = {
            "field": col,
            "headerName": col,
            "filter": True,
            "sortable": True,
            "resizable": True,
        }
        
        # Format numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            # Check if it's a currency column
            if 'amount' in col.lower() or 'revenue' in col.lower() or 'sales' in col.lower() or 'price' in col.lower():
                col_def["valueFormatter"] = {"function": "d3.format('$,.2f')(params.value)"}
                col_def["type"] = "rightAligned"
            # Check if it's a large number that should use thousands separator
            elif df[col].abs().max() > 999:
                col_def["valueFormatter"] = {"function": "d3.format(',.0f')(params.value)"}
                col_def["type"] = "rightAligned"
            else:
                col_def["type"] = "rightAligned"
        
        column_defs.append(col_def)
    
    # Default column definition
    default_col_def = {
        "flex": 1,
        "minWidth": 100,
        "filter": True,
        "sortable": True,
        "resizable": True,
    }
    
    # Theme-specific CSS variables to match Mantine theme
    if is_dark:
        grid_style = {
            "height": max_height,
            "width": "100%",
            "--ag-background-color": "#242424",
            "--ag-foreground-color": "#ffffff",
            "--ag-header-background-color": "#25262b",
            "--ag-header-foreground-color": "#ffffff",
            "--ag-row-hover-color": "#2c2e33",
            "--ag-border-color": "#373A40",
            "--ag-font-family": "DM Sans, sans-serif",
            "--ag-font-size": "14px",
            "--ag-cell-horizontal-padding": "12px",
        }
    else:
        grid_style = {
            "height": max_height,
            "width": "100%",
            "--ag-background-color": "#ffffff",
            "--ag-foreground-color": "#000000",
            "--ag-header-background-color": "#f8f9fa",
            "--ag-header-foreground-color": "#000000",
            "--ag-odd-row-background-color": "#ffffff",
            "--ag-row-hover-color": "#f1f3f5",
            "--ag-border-color": "#dee2e6",
            "--ag-font-family": "DM Sans, sans-serif",
            "--ag-font-size": "14px",
            "--ag-cell-horizontal-padding": "12px",
        }
    
    # Create AG Grid component
    table = dag.AgGrid(
        rowData=df.to_dict('records'),
        columnDefs=column_defs,
        defaultColDef=default_col_def,
        
        # Styling
        className=grid_theme,
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": page_size,
            "paginationPageSizeSelector": [10, 25, 50, 100],
            "animateRows": True,
            "enableCellTextSelection": True,
            "ensureDomOrder": True,
        },
        
        # Size and theme variables
        style=grid_style,
    )
    
    return table
