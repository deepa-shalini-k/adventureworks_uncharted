import pandas as pd

def apply_global_filters(sales_df, date_df, territory_df, product_df, filters):
    """Apply global filters to the merged sales data"""
    
    # Merge all data
    merged = sales_df.merge(date_df, left_on='OrderDateKey', right_on='DateKey', how='left')
    merged = merged.merge(territory_df, on='SalesTerritoryKey', how='left')
    merged = merged.merge(product_df, on='ProductKey', how='left')
    
    # Apply fiscal year filter
    if filters.get('fiscal_years') and isinstance(filters['fiscal_years'], list) and len(filters['fiscal_years']) == 2:
        fy_min, fy_max = filters['fiscal_years']
        merged['FY_numeric'] = merged['Fiscal Year'].str.extract(r'FY(\d{4})')[0].astype(int)
        merged = merged[merged['FY_numeric'].between(fy_min, fy_max)]
        merged = merged.drop('FY_numeric', axis=1)
    
    # Apply quarter filter
    if filters.get('quarters') and len(filters['quarters']) > 0 and len(filters['quarters']) < 4:
        # Extract just the quarter number (Q1 -> 1)
        quarter_nums = [q.replace('Q', '') for q in filters['quarters']]
        quarter_pattern = '|'.join([f' Q{q}' for q in quarter_nums])
        merged = merged[merged['Fiscal Quarter'].str.contains(quarter_pattern, na=False)]
    
    # Apply region filter
    if filters.get('region') != 'All':
        merged = merged[merged['Group'] == filters['region']]
    
    # Apply territory filter
    if filters.get('territories') and len(filters['territories']) > 0:
        merged = merged[merged['Region'].isin(filters['territories'])]
    
    # Apply category filter
    if filters.get('categories') and len(filters['categories']) > 0:
        merged = merged[merged['Category'].isin(filters['categories'])]
    
    # Apply channel filter
    if filters.get('channel') == 'B2B':
        merged = merged[merged['ResellerKey'] != -1]
    elif filters.get('channel') == 'B2C':
        merged = merged[merged['CustomerKey'] != -1]
    
    # Exclude Corporate HQ
    merged = merged[merged['Region'] != 'Corporate HQ']
    
    return merged