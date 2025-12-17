import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide", 
    page_title="Nashik Run Distribution",
    page_icon="👕"
)

# --- LOGO & CREDENTIALS ---
LOGO_URL = "https://github.com/nincoreultra5/Admin-dashboard-version-1/raw/main/nsk.png"
SUPABASE_URL = "https://ocokfyepdgirquwkhbhs.supabase.co".strip()
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jb2tmeWVwZGdpcnF1d2toYmhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MzU5NjQsImV4cCI6MjA4MTUxMTk2NH0.x6onqjC02j5FTXikDw_5eBaaaPQDDTdFnGkZOfdxoOA".strip()

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS (COLORS & STYLING)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Background */
    .stApp {
        background-color: #f3f4f6;
    }

    /* Header */
    h1 {
        color: #111827;
        font-weight: 800;
    }
    
    /* CUSTOM KPI CARDS CSS */
    .kpi-card {
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    .kpi-title {
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .kpi-note {
        font-size: 0.8rem;
        opacity: 0.8;
    }

    /* COLOR THEMES FOR CARDS */
    .blue-theme { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); color: #1e40af; border-left: 5px solid #2563eb; }
    .orange-theme { background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%); color: #9a3412; border-left: 5px solid #ea580c; }
    .green-theme { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); color: #166534; border-left: 5px solid #16a34a; }

    /* REASON CARDS CSS */
    .reason-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #6366f1; /* Indigo Accent */
        margin-bottom: 10px;
    }
    .reason-label {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 600;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .reason-number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1f2937;
    }
    
    /* Table Styling */
    div[data-testid="stDataFrame"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. CONNECTION & DATA
# -----------------------------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase = init_connection()

def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    
    # Fetch Data
    stock_data = supabase.table('stock').select('*').execute().data
    trans_data = supabase.table('transactions').select('*').execute().data
    
    df_s = pd.DataFrame(stock_data)
    df_t = pd.DataFrame(trans_data)
    
    if not df_t.empty:
        df_t['created_at'] = pd.to_datetime(df_t['created_at'])
        df_t['date'] = df_t['created_at'].dt.date
    
    return df_s, df_t

df_stock, df_trans = get_data()

# Metrics Logic
purchased = 0
consumed_total = 0
remaining = 0
df_out_all = pd.DataFrame()

if not df_trans.empty:
    purchased = df_trans[(df_trans['organization'] == 'Warehouse') & (df_trans['type'] == 'in')]['quantity'].sum()
    df_out_all = df_trans[(df_trans['organization'] != 'Warehouse') & (df_trans['type'] == 'out')]
    consumed_total = df_out_all['quantity'].sum()

if not df_stock.empty:
    remaining = df_stock[df_stock['organization'] == 'Warehouse']['quantity'].sum()

# -----------------------------------------------------------------------------
# 4. DASHBOARD LAYOUT
# -----------------------------------------------------------------------------

# --- HEADER ---
col_logo, col_title = st.columns([1, 7])
with col_logo:
    st.image(LOGO_URL, width=120)
with col_title:
    st.title("Nashik Run Distribution")
    st.markdown("**Live Inventory Analysis & Tracking System**")

st.markdown("---")

# --- COLORFUL KPI CARDS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="kpi-card blue-theme">
        <div class="kpi-title">Total Purchased</div>
        <div class="kpi-value">{int(purchased)}</div>
        <div class="kpi-note">Supplier → Warehouse</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card orange-theme">
        <div class="kpi-title">Total Distributed</div>
        <div class="kpi-value">{int(consumed_total)}</div>
        <div class="kpi-note">Bosch, TDK, Mahatma Nagar</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card green-theme">
        <div class="kpi-title">Current Stock</div>
        <div class="kpi-value">{int(remaining)}</div>
        <div class="kpi-note">Available in Warehouse</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- INVENTORY TABLE ---
st.subheader("📦 Inventory Grid")

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
    st.info("No data available.")

st.markdown("---")

# --- REASON ANALYSIS ---
c1, c2 = st.columns([3, 1])
with c1:
    st.subheader("📋 Distribution by Reason")
with c2:
    selected_org = st.selectbox("📍 Filter Location", ["All", "Bosch", "TDK", "Mathma Nagar"])

# Filter Logic
df_filtered = df_out_all.copy()
if selected_org != "All" and not df_filtered.empty:
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

# 3x3 Grid
rows = [st.columns(3), st.columns(3), st.columns(3)]
idx = 0
for row in rows:
    for col in row:
        if idx < len(reasons_list):
            r_name = reasons_list[idx]
            r_val = reason_counts[r_name]
            with col:
                st.markdown(f"""
                <div class="reason-card">
                    <div class="reason-label">{r_name}</div>
                    <div class="reason-number">{int(r_val)}</div>
                </div>
                """, unsafe_allow_html=True)
            idx += 1

st.markdown("---")

# --- TREND GRAPH ---
st.subheader(f"📈 Daily Trend: {selected_org}")

if not df_filtered.empty:
    chart_data = df_filtered.groupby(['date', 'category'])['quantity'].sum().reset_index()
    chart_data['date'] = chart_data['date'].astype(str)
    
    # Vibrant Colors: Orange for Kids, Blue for Adults
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('date', title='Date', axis=alt.Axis(labelAngle=-45, grid=False)),
        y=alt.Y('quantity', title='Count'),
        color=alt.Color('category', 
                        scale=alt.Scale(domain=['kids', 'adults'], range=['#f97316', '#3b82f6']), 
                        title='Category'),
        tooltip=['date', 'category', 'quantity']
    ).properties(
        height=400,
        background='transparent'
    ).configure_view(strokeWidth=0)
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning(f"No distribution data for {selected_org}")
