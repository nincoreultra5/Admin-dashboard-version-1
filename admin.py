import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. SETUP & CREDENTIALS
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="NR Distribution Dashboard")

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
# 2. DATA FETCHING
# -----------------------------------------------------------------------------
def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    
    # Fetch Stock
    res_stock = supabase.table('stock').select('*').execute()
    df_stock = pd.DataFrame(res_stock.data)
    
    # Fetch Transactions
    res_trans = supabase.table('transactions').select('*').execute()
    df_trans = pd.DataFrame(res_trans.data)
    
    if not df_trans.empty:
        df_trans['created_at'] = pd.to_datetime(df_trans['created_at'])
        df_trans['date'] = df_trans['created_at'].dt.date
    
    return df_stock, df_trans

df_stock, df_trans = get_data()

# -----------------------------------------------------------------------------
# 3. METRICS (TOP LAYER)
# -----------------------------------------------------------------------------
purchased = 0
if not df_trans.empty:
    purchased = df_trans[(df_trans['organization'] == 'Warehouse') & (df_trans['type'] == 'in')]['quantity'].sum()

consumed_total = 0
df_out_all = pd.DataFrame()
if not df_trans.empty:
    # All OUT transactions from branches
    df_out_all = df_trans[(df_trans['organization'] != 'Warehouse') & (df_trans['type'] == 'out')]
    consumed_total = df_out_all['quantity'].sum()

remaining = 0
if not df_stock.empty:
    remaining = df_stock[df_stock['organization'] == 'Warehouse']['quantity'].sum()

# -----------------------------------------------------------------------------
# 4. UI: HEADER & BOXES
# -----------------------------------------------------------------------------
st.title("NR T-Shirt Distribution Analysis")

col1, col2, col3 = st.columns(3)
col1.metric("T-Shirts Purchased", f"{int(purchased)}", "Supplier → Warehouse")
col2.metric("T-Shirts Consumed", f"{int(consumed_total)}", "Total Distributed", delta_color="inverse")
col3.metric("T-Shirts Remaining", f"{int(remaining)}", "Warehouse Stock")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. UI: INVENTORY TABLE
# -----------------------------------------------------------------------------
st.subheader("Live Inventory Grid")

if not df_stock.empty:
    pivot_df = df_stock.pivot_table(index='organization', columns='size', values='quantity', aggfunc='sum', fill_value=0)
    cols = sorted(pivot_df.columns, key=lambda x: int(x) if x.isdigit() else 999)
    pivot_df = pivot_df[cols]
    
    # Totals
    pivot_df['TOTAL'] = pivot_df.sum(axis=1)
    sum_row = pivot_df.sum().to_frame().T
    sum_row.index = ["TOTAL"]
    final_df = pd.concat([pivot_df, sum_row])
    
    st.dataframe(final_df, use_container_width=True)
else:
    st.info("No stock data.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. UI: REASONS (WITH FILTER)
# -----------------------------------------------------------------------------
col_head, col_filter = st.columns([3, 1])
with col_head:
    st.subheader("Distribution by Reason")
with col_filter:
    # FILTER DROPDOWN
    selected_org = st.selectbox("Select Location", ["All", "Bosch", "TDK", "Mathma Nagar"])

# Filter Logic
df_filtered = df_out_all.copy() # Start with all OUT transactions

if selected_org != "All":
    if not df_filtered.empty:
        df_filtered = df_filtered[df_filtered['organization'] == selected_org]

# Reason Calculation
reasons_list = [
    "Against Registration", "Cycle Rally", "VIP Kit", 
    "Against Donation", "NGO/Beneficiary", "Volunteers", 
    "Flag off & Torch bearers", "Police", "Others"
]

reason_counts = {r: 0 for r in reasons_list}
if not df_filtered.empty:
    grouped = df_filtered.groupby('reason')['quantity'].sum()
    for r in reasons_list:
        reason_counts[r] = grouped.get(r, 0)

# 3x3 Grid Display
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
# 7. UI: GRAPH
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader(f"Daily Distribution Trend ({selected_org})")

if not df_filtered.empty:
    chart_data = df_filtered.groupby(['date', 'category'])['quantity'].sum().reset_index()
    chart_data['date'] = chart_data['date'].astype(str)
    
    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('date', title='Date'),
        y=alt.Y('quantity', title='T-Shirts Distributed'),
        color=alt.Color('category', scale=alt.Scale(domain=['kids', 'adults'], range=['#FF9F36', '#4F8BF9']), title='Category'),
        tooltip=['date', 'category', 'quantity']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info(f"No distribution data available for {selected_org}.")
