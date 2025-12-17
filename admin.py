import streamlit as st
from supabase import create_client, Client
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CREDENTIALS & CONNECTION
# -----------------------------------------------------------------------------
# specific credentials provided by user
SUPABASE_URL = "https://ocokfyepdgirquwkhbhs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jb2tmeWVwZGdpcnF1d2toYmhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MzU5NjQsImV4cCI6MjA4MTUxMTk2NH0.x6onqjC02j5FTXikDw_5eBaaaPQDDTdFnGkZOfdxoOA"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return None

supabase = init_connection()

# -----------------------------------------------------------------------------
# 2. DATA FETCHING LOGIC
# -----------------------------------------------------------------------------
def get_dashboard_metrics():
    """
    Calculates the 3 key metrics for the top boxes based on database transactions.
    """
    if not supabase: return 0, 0, 0
    
    # BOX 1: Total Purchased (Supplier -> Warehouse)
    # Logic: Sum of all 'in' transactions specifically for the Warehouse
    res_purchased = supabase.table('transactions')\
        .select('quantity')\
        .eq('organization', 'Warehouse')\
        .eq('type', 'in')\
        .execute()
    
    total_purchased = sum(item['quantity'] for item in res_purchased.data) if res_purchased.data else 0

    # BOX 2: Total Consumed (Warehouse -> Bosch/TDK/MN)
    # Logic: Sum of all 'in' transactions for the beneficiary organizations
    # (Meaning: They received it, so it is consumed from the Warehouse perspective)
    res_consumed = supabase.table('transactions')\
        .select('quantity')\
        .neq('organization', 'Warehouse')\
        .eq('type', 'in')\
        .execute()
        
    total_consumed = sum(item['quantity'] for item in res_consumed.data) if res_consumed.data else 0

    # BOX 3: Total Remaining (Live Warehouse Stock)
    # Logic: Sum of the actual 'quantity' column in the stock table for Warehouse
    res_remaining = supabase.table('stock')\
        .select('quantity')\
        .eq('organization', 'Warehouse')\
        .execute()
        
    total_remaining = sum(item['quantity'] for item in res_remaining.data) if res_remaining.data else 0
    
    return total_purchased, total_consumed, total_remaining

def get_detailed_stock():
    """Fetches stock broken down by Size for the table view"""
    if not supabase: return pd.DataFrame()
    
    # Fetch all stock rows
    response = supabase.table('stock').select('*').order('size').execute()
    return pd.DataFrame(response.data)

# -----------------------------------------------------------------------------
# 3. DASHBOARD UI LAYOUT
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="NR Distribution")

st.title("NR T-Shirt Distribution Analysis")
st.markdown("### Dashboard Overview")

# Fetch live data
try:
    purchased, consumed, remaining = get_dashboard_metrics()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    purchased, consumed, remaining = 0, 0, 0

# --- TOP LAYER: 3 BOXES ---
# Using custom CSS to make it look like the diagram boxes
col1, col2, col3 = st.columns(3)

with col1:
    st.container(border=True)
    st.metric(
        label="T-Shirts Purchased", 
        value=purchased, 
        delta="Supplier → Warehouse (IN)"
    )

with col2:
    st.container(border=True)
    st.metric(
        label="T-Shirts Consumed", 
        value=consumed, 
        delta="Bosch, TDK, Mahatma Nagar",
        delta_color="inverse"
    )

with col3:
    st.container(border=True)
    st.metric(
        label="T-Shirts Remaining", 
        value=remaining,
        delta="Warehouse Stock"
    )

# --- MIDDLE LAYER: STOCK TABLE ---
st.markdown("---")
st.subheader("Live Inventory Grid")

try:
    df_stock = get_detailed_stock()

    if not df_stock.empty:
        # Create a Pivot Table: Rows = Organization, Columns = Size, Values = Quantity
        pivot_df = df_stock.pivot_table(
            index='organization', 
            columns='size', 
            values='quantity', 
            aggfunc='sum',
            fill_value=0
        )
        
        # Sort columns numerically if possible (26, 28, 30...)
        try:
            sorted_cols = sorted(pivot_df.columns, key=lambda x: int(x) if x.isdigit() else 999)
            pivot_df = pivot_df[sorted_cols]
        except:
            pass # Keep default sort if non-numeric sizes exist
            
        st.dataframe(
            pivot_df, 
            use_container_width=True,
            column_config={
                "_index": st.column_config.Column("Organization")
            }
        )
    else:
        st.info("No stock data found in database.")
except Exception as e:
    st.error(f"Error loading table: {e}")

# --- BOTTOM LAYER: ACTION BUTTONS (Visual Only) ---
st.markdown("### Locations")
b_col1, b_col2, b_col3, b_col4 = st.columns(4)

with b_col1:
    st.button("🏢 Warehouse", use_container_width=True)
with b_col2:
    st.button("🏭 Bosch", use_container_width=True)
with b_col3:
    st.button("⚡ TDK", use_container_width=True)
with b_col4:
    st.button("📍 Mathma Nagar", use_container_width=True)

