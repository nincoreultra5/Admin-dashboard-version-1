import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. SETUP & CREDENTIALS
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="NR Distribution Dashboard")

# Using the credentials you provided
SUPABASE_URL = "https://ocokfyepdgirquwkhbhs.supabase.co".strip()
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jb2tmeWVwZGdpcnF1d2toYmhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MzU5NjQsImV4cCI6MjA4MTUxMTk2NH0.x6onqjC02j5FTXikDw_5eBaaaPQDDTdFnGkZOfdxoOA".strip()

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_connection()

# -----------------------------------------------------------------------------
# 2. DATA FETCHING & PROCESSING
# -----------------------------------------------------------------------------
def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    
    # Fetch Stock
    res_stock = supabase.table('stock').select('*').execute()
    df_stock = pd.DataFrame(res_stock.data)
    
    # Fetch Transactions (Limit to 1000 or needed range for performance)
    res_trans = supabase.table('transactions').select('*').execute()
    df_trans = pd.DataFrame(res_trans.data)
    
    # Ensure dates are datetime objects
    if not df_trans.empty:
        df_trans['created_at'] = pd.to_datetime(df_trans['created_at'])
        # Create a simple date column for grouping
        df_trans['date'] = df_trans['created_at'].dt.date
    
    return df_stock, df_trans

df_stock, df_trans = get_data()

# -----------------------------------------------------------------------------
# 3. METRICS CALCULATION
# -----------------------------------------------------------------------------
# Box 1: Purchased (Warehouse IN)
purchased = 0
if not df_trans.empty:
    purchased = df_trans[
        (df_trans['organization'] == 'Warehouse') & 
        (df_trans['type'] == 'in')
    ]['quantity'].sum()

# Box 2: Consumed (Branch OUT) -> Matches the sum of reasons
consumed = 0
df_consumed = pd.DataFrame()
if not df_trans.empty:
    # Filter for OUT transactions NOT from Warehouse (Bosch, TDK, MN)
    df_consumed = df_trans[
        (df_trans['organization'] != 'Warehouse') & 
        (df_trans['type'] == 'out')
    ]
    consumed = df_consumed['quantity'].sum()

# Box 3: Remaining (Live Stock)
remaining = 0
if not df_stock.empty:
    remaining = df_stock[df_stock['organization'] == 'Warehouse']['quantity'].sum()

# -----------------------------------------------------------------------------
# 4. DASHBOARD - TOP LAYER
# -----------------------------------------------------------------------------
st.title("NR T-Shirt Distribution Analysis")

col1, col2, col3 = st.columns(3)
col1.metric("T-Shirts Purchased", f"{int(purchased)}", "Supplier → Warehouse")
col2.metric("T-Shirts Consumed", f"{int(consumed)}", "Distributed to People", delta_color="inverse")
col3.metric("T-Shirts Remaining", f"{int(remaining)}", "Warehouse Stock")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. INVENTORY TABLE (WITH TOTALS)
# -----------------------------------------------------------------------------
st.subheader("Live Inventory Grid")

if not df_stock.empty:
    # Pivot
    pivot_df = df_stock.pivot_table(
        index='organization', 
        columns='size', 
        values='quantity', 
        aggfunc='sum', 
        fill_value=0
    )
    
    # Sort Columns Numerically
    cols = sorted(pivot_df.columns, key=lambda x: int(x) if x.isdigit() else 999)
    pivot_df = pivot_df[cols]
    
    # Add Row Totals
    pivot_df['TOTAL'] = pivot_df.sum(axis=1)
    
    # Add Column Totals
    sum_row = pivot_df.sum().to_frame().T
    sum_row.index = ["TOTAL"]
    final_df = pd.concat([pivot_df, sum_row])
    
    st.dataframe(final_df, use_container_width=True)
else:
    st.info("No stock data available.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. REASONS ANALYSIS (3x3 Grid)
# -----------------------------------------------------------------------------
st.subheader("Distribution by Reason")

# Defined reasons list
reasons_list = [
    "Against Registration", "Cycle Rally", "VIP Kit", 
    "Against Donation", "NGO/Beneficiary", "Volunteers", 
    "Flag off & Torch bearers", "Police", "Others"
]

# Calculate counts per reason from the 'consumed' dataframe
reason_counts = {r: 0 for r in reasons_list}
if not df_consumed.empty:
    # Group by reason and sum quantity
    grouped = df_consumed.groupby('reason')['quantity'].sum()
    for r in reasons_list:
        reason_counts[r] = grouped.get(r, 0)

# Display in 3x3 Grid
r_rows = [st.columns(3), st.columns(3), st.columns(3)]
r_idx = 0

for row in r_rows:
    for col in row:
        if r_idx < len(reasons_list):
            r_name = reasons_list[r_idx]
            r_val = reason_counts[r_name]
            
            with col:
                st.container(border=True).metric(label=r_name, value=int(r_val))
            r_idx += 1

# -----------------------------------------------------------------------------
# 7. DAY-WISE GRAPH (Stacked Kids vs Adults)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("Daily Distribution Trend")

if not df_consumed.empty:
    # Prepare data for chart: Date, Category, Quantity
    chart_data = df_consumed.groupby(['date', 'category'])['quantity'].sum().reset_index()
    
    # Rename for cleaner legend
    chart_data['date'] = chart_data['date'].astype(str)
    
    # Create Stacked Bar Chart
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('date', title='Date'),
        y=alt.Y('quantity', title='T-Shirts Distributed'),
        color=alt.Color('category', scale=alt.Scale(domain=['kids', 'adults'], range=['#FF9F36', '#4F8BF9']), title='Category'),
        tooltip=['date', 'category', 'quantity']
    ).properties(
        height=400
    )
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No distribution data available yet for the graph.")
