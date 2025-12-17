import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide", 
    page_title="NR Distribution Dashboard",
    page_icon="👕"
)

# --- PUT YOUR LOGO URL HERE ---
LOGO_URL = "nsk.png" 
# Example: "nsk.png"

# Custom CSS for "Attractive" UI
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header Styling */
    h1 {
        color: #1f2937;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        padding-bottom: 0.5rem;
    }
    h3 {
        color: #374151;
        font-weight: 600;
        padding-top: 1rem;
    }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #6b7280;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
    }
    
    /* Table Styling */
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SUPABASE CONNECTION
# -----------------------------------------------------------------------------
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
# 3. DATA FETCHING
# -----------------------------------------------------------------------------
def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    
    res_stock = supabase.table('stock').select('*').execute()
    df_stock = pd.DataFrame(res_stock.data)
    
    res_trans = supabase.table('transactions').select('*').execute()
    df_trans = pd.DataFrame(res_trans.data)
    
    if not df_trans.empty:
        df_trans['created_at'] = pd.to_datetime(df_trans['created_at'])
        df_trans['date'] = df_trans['created_at'].dt.date
    
    return df_stock, df_trans

df_stock, df_trans = get_data()

# -----------------------------------------------------------------------------
# 4. METRICS CALCULATION
# -----------------------------------------------------------------------------
purchased = 0
if not df_trans.empty:
    purchased = df_trans[(df_trans['organization'] == 'Warehouse') & (df_trans['type'] == 'in')]['quantity'].sum()

consumed_total = 0
df_out_all = pd.DataFrame()
if not df_trans.empty:
    df_out_all = df_trans[(df_trans['organization'] != 'Warehouse') & (df_trans['type'] == 'out')]
    consumed_total = df_out_all['quantity'].sum()

remaining = 0
if not df_stock.empty:
    remaining = df_stock[df_stock['organization'] == 'Warehouse']['quantity'].sum()

# -----------------------------------------------------------------------------
# 5. DASHBOARD LAYOUT
# -----------------------------------------------------------------------------

# --- LOGO & TITLE ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if LOGO_URL and "http" in LOGO_URL:
        st.image(LOGO_URL, width=120)
    else:
        st.write("📷 Logo") # Placeholder if URL is broken/empty
with col_title:
    st.title("NR T-Shirt Distribution Analysis")
    st.markdown("Overview of inventory flow from Supplier to End Beneficiaries.")

st.markdown("---")

# --- KPI CARDS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("T-Shirts Purchased", f"{int(purchased)}", "Supplier → Warehouse")
with col2:
    st.metric("T-Shirts Consumed", f"{int(consumed_total)}", "Total Distributed", delta_color="inverse")
with col3:
    st.metric("T-Shirts Remaining", f"{int(remaining)}", "Warehouse Stock")

st.markdown("<br>", unsafe_allow_html=True) 

# --- INVENTORY TABLE ---
st.subheader("📦 Live Inventory Grid")

if not df_stock.empty:
    pivot_df = df_stock.pivot_table(index='organization', columns='size', values='quantity', aggfunc='sum', fill_value=0)
    cols = sorted(pivot_df.columns, key=lambda x: int(x) if x.isdigit() else 999)
    pivot_df = pivot_df[cols]
    
    # Add Totals
    pivot_df['TOTAL'] = pivot_df.sum(axis=1)
    sum_row = pivot_df.sum().to_frame().T
    sum_row.index = ["TOTAL"]
    final_df = pd.concat([pivot_df, sum_row])
    
    st.dataframe(final_df, use_container_width=True)
else:
    st.info("No stock data available.")

st.markdown("<br>", unsafe_allow_html=True)

# --- REASONS GRID ---
c1, c2 = st.columns([3, 1])
with c1:
    st.subheader("📋 Distribution by Reason")
with c2:
    selected_org = st.selectbox("📍 Filter by Location", ["All", "Bosch", "TDK", "Mathma Nagar"])

# Filter Data
df_filtered = df_out_all.copy()
if selected_org != "All":
    if not df_filtered.empty:
        df_filtered = df_filtered[df_filtered['organization'] == selected_org]

# Reason Counts
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
                st.markdown(f"""
                <div style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; text-align: center; margin-bottom: 10px;">
                    <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 5px; height: 40px; display: flex; align-items: center; justify-content: center;">{r_name}</div>
                    <div style="color: #111827; font-size: 1.8rem; font-weight: bold;">{int(r_val)}</div>
                </div>
                """, unsafe_allow_html=True)
            r_idx += 1

st.markdown("<br>", unsafe_allow_html=True)

# --- DAILY TREND GRAPH ---
st.subheader(f"📈 Daily Trend: {selected_org}")

if not df_filtered.empty:
    chart_data = df_filtered.groupby(['date', 'category'])['quantity'].sum().reset_index()
    chart_data['date'] = chart_data['date'].astype(str)
    
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X('date', title='Date', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('quantity', title='Count'),
        color=alt.Color('category', 
                        scale=alt.Scale(domain=['kids', 'adults'], range=['#f97316', '#3b82f6']), 
                        title='Category'),
        tooltip=['date', 'category', 'quantity']
    ).properties(
        height=400,
        background='#ffffff'
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.container(border=True).info(f"No distribution data available for {selected_org}.")

st.markdown("---")
st.caption("NR Distribution System • v1.0")
