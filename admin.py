import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide", 
    page_title="Nashik Run Distribution Dashboard",
    page_icon="👕"
)

# --- LOGO URL ---
LOGO_URL = "https://github.com/nincoreultra5/Admin-dashboard-version-1/raw/main/nsk.png"

# --- CUSTOM CSS (ATTRACTIVE UI) ---
st.markdown("""
<style>
    /* 1. Main Background & Font */
    .stApp {
        background-color: #f0f2f6; /* Very light grey-blue background */
        font-family: 'Inter', sans-serif;
    }
    
    /* 2. Header Styling */
    h1 {
        color: #1e3a8a; /* Dark Blue */
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    h3 {
        color: #374151; /* Charcoal */
        font-weight: 600;
        margin-top: 1rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    
    /* 3. Metric Card Styling (Top Row) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1f2937;
    }
    
    /* 4. Table Styling */
    .stDataFrame {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* 5. Custom Reason Cards (HTML) */
    .reason-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .reason-card:hover {
        border-color: #3b82f6; /* Blue border on hover */
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.15); /* Blue glow */
    }
    .reason-title {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        height: 30px; /* Fixed height for alignment */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .reason-value {
        color: #111827;
        font-size: 2rem;
        font-weight: 800;
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

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 8])

with col_logo:
    try:
        st.image(LOGO_URL, width=120)
    except:
        st.write("📷") 
        
with col_title:
    st.title("Nashik Run Distribution")
    st.markdown("Live Inventory Tracking & Distribution Analytics")

st.markdown("<br>", unsafe_allow_html=True)

# --- KPI CARDS (TOP ROW) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Purchased", f"{int(purchased)}", "Supplier → Warehouse")
with col2:
    st.metric("Total Distributed", f"{int(consumed_total)}", "To Beneficiaries", delta_color="inverse")
with col3:
    st.metric("Current Stock", f"{int(remaining)}", "Available in Warehouse")

st.markdown("---")

# --- INVENTORY TABLE ---
st.subheader("📦 Live Inventory Grid")

if not df_stock.empty:
    pivot_df = df_stock.pivot_table(index='organization', columns='size', values='quantity', aggfunc='sum', fill_value=0)
    
    # Smart sorting for sizes
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

st.markdown("---")

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

# 3x3 Grid Display with Enhanced Cards
r_rows = [st.columns(3), st.columns(3), st.columns(3)]
r_idx = 0

for row in r_rows:
    for col in row:
        if r_idx < len(reasons_list):
            r_name = reasons_list[r_idx]
            r_val = reason_counts[r_name]
            with col:
                st.markdown(f"""
                <div class="reason-card">
                    <div class="reason-title">{r_name}</div>
                    <div class="reason-value">{int(r_val)}</div>
                </div>
                """, unsafe_allow_html=True)
            r_idx += 1

st.markdown("---")

# --- DAILY TREND GRAPH ---
st.subheader(f"📈 Daily Trend Analysis: {selected_org}")

if not df_filtered.empty:
    chart_data = df_filtered.groupby(['date', 'category'])['quantity'].sum().reset_index()
    chart_data['date'] = chart_data['date'].astype(str)
    
    # Professional Chart Colors (Blue & Orange theme)
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('date', title='Date', axis=alt.Axis(labelAngle=-45, grid=False)),
        y=alt.Y('quantity', title='T-Shirts Distributed', axis=alt.Axis(grid=True, gridDash=[2,2])),
        color=alt.Color('category', 
                        scale=alt.Scale(domain=['kids', 'adults'], range=['#f97316', '#2563eb']), 
                        title='Category'),
        tooltip=['date', 'category', 'quantity']
    ).properties(
        height=400,
        background='transparent' # Transparent so it blends with app background
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.container(border=True).info(f"No distribution data available for {selected_org} to generate graph.")

st.markdown("<br><center><small style='color: #9ca3af'>Nashik Run Distribution System • v1.2</small></center>", unsafe_allow_html=True)
