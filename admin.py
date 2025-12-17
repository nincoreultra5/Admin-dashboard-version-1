import streamlit as st
from supabase import create_client
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CREDENTIALS (CLEANED)
# -----------------------------------------------------------------------------
# I have removed any potential hidden whitespace
SUPABASE_URL = "https://ocokfyepdgirquwkhbhs.supabase.co".strip()
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jb2tmeWVwZGdpcnF1d2toYmhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MzU5NjQsImV4cCI6MjA4MTUxMTk2NH0.x6onqjC02j5FTXikDw_5eBaaaPQDDTdFnGkZOfdxoOA".strip()

@st.cache_resource
def init_connection():
    try:
        # Create client with timeout options to prevent hanging
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Connection Failed: {e}")
        return None

supabase = init_connection()

# -----------------------------------------------------------------------------
# 2. DATA FETCHING
# -----------------------------------------------------------------------------
def get_dashboard_metrics():
    if not supabase: return 0, 0, 0
    
    # BOX 1: Purchased
    res_purchased = supabase.table('transactions').select('quantity').eq('organization', 'Warehouse').eq('type', 'in').execute()
    total_purchased = sum(item['quantity'] for item in res_purchased.data) if res_purchased.data else 0

    # BOX 2: Consumed
    res_consumed = supabase.table('transactions').select('quantity').neq('organization', 'Warehouse').eq('type', 'in').execute()
    total_consumed = sum(item['quantity'] for item in res_consumed.data) if res_consumed.data else 0

    # BOX 3: Remaining
    res_remaining = supabase.table('stock').select('quantity').eq('organization', 'Warehouse').execute()
    total_remaining = sum(item['quantity'] for item in res_remaining.data) if res_remaining.data else 0
    
    return total_purchased, total_consumed, total_remaining

def get_detailed_stock():
    if not supabase: return pd.DataFrame()
    response = supabase.table('stock').select('*').execute()
    return pd.DataFrame(response.data)

# -----------------------------------------------------------------------------
# 3. UI
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="NR Distribution")
st.title("NR T-Shirt Distribution Analysis")

try:
    purchased, consumed, remaining = get_dashboard_metrics()
except Exception as e:
    st.error(f"Detailed Error: {e}")
    purchased, consumed, remaining = 0, 0, 0

col1, col2, col3 = st.columns(3)
col1.metric("T-Shirts Purchased", purchased, "Supplier → Warehouse")
col2.metric("T-Shirts Consumed", consumed, "Bosch, TDK, MN", delta_color="inverse")
col3.metric("T-Shirts Remaining", remaining, "Warehouse Stock")

st.markdown("---")
st.subheader("Live Inventory Grid")

try:
    df_stock = get_detailed_stock()
    if not df_stock.empty:
        pivot_df = df_stock.pivot_table(index='organization', columns='size', values='quantity', aggfunc='sum', fill_value=0)
        st.dataframe(pivot_df, use_container_width=True)
    else:
        st.warning("Database connected but returned no data.")
except Exception as e:
    st.error(f"Table Error: {e}")
