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

# --- CREDENTIALS ---
LOGO_URL = "https://github.com/nincoreultra5/Admin-dashboard-version-1/raw/main/nsk.png"
SUPABASE_URL = "https://ocokfyepdgirquwkhbhs.supabase.co".strip()
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jb2tmeWVwZGdpcnF1d2toYmhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MzU5NjQsImV4cCI6MjA4MTUxMTk2NH0.x6onqjC02j5FTXikDw_5eBaaaPQDDTdFnGkZOfdxoOA".strip()

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS (VIBRANT UI)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Background */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    h1 { color: #0f172a; font-weight: 800; }
    h3 { color: #334155; }

    /* --- TOP KPI CARDS --- */
    .kpi-card {
        padding: 24px;
        border-radius: 16px;
        background: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    .kpi-label { font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 8px; }
    .kpi-val { font-size: 2.5rem; font-weight: 800; color: #0f172a; line-height: 1; margin-bottom: 8px; }
    .kpi-sub { font-size: 0.8rem; font-weight: 500; padding: 4px 12px; border-radius: 20px; display: inline-block; }

    /* KPI Color Themes */
    .theme-blue .kpi-sub { background: #eff6ff; color: #2563eb; }
    .theme-orange .kpi-sub { background: #fff7ed; color: #ea580c; }
    .theme-green .kpi-sub { background: #f0fdf4; color: #16a34a; }

    /* --- ATTRACTIVE REASON GRID --- */
    .reason-box {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border: 1px solid #f1f5f9;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .reason-box:hover {
        border-color: #cbd5e1;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
    }
    /* Colored stripe on top */
    .reason-stripe {
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
    }
    .r-title { font-size: 0.85rem; color: #64748b; font-weight: 600; margin-top: 8px; text-align: center; }
    .r-count { font-size: 2rem; font-weight: 800; color: #1e293b; margin-top: 4px; }
    
    /* Specific Colors for Reasons */
    .c-reg { background: #3b82f6; } /* Blue */
    .c-cyc { background: #14b8a6; } /* Teal */
    .c-vip { background: #8b5cf6; } /* Purple */
    .c-don { background: #f59e0b; } /* Amber */
    .c-ngo { background: #10b981; } /* Emerald */
    .c-vol { background: #ec4899; } /* Pink */
    .c-flg { background: #ef4444; } /* Red */
    .c-pol { background: #6366f1; } /* Indigo */
    .c-oth { background: #64748b; } /* Slate */

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. DATA FETCHING
# -----------------------------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except: return None

supabase = init_connection()

def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    s = supabase.table('stock').select('*').execute().data
    t = supabase.table('transactions').select('*').execute().data
    
    df_s = pd.DataFrame(s)
    df_t = pd.DataFrame(t)
    
    if not df_t.empty:
        df_t['created_at'] = pd.to_datetime(df_t['created_at'])
        df_t['date'] = df_t['created_at'].dt.date
    return df_s, df_t

df_stock, df_trans = get_data()

# Logic
purchased, consumed_total, remaining = 0, 0, 0
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

# HEADER
c_logo, c_title = st.columns([1, 7])
with c_logo: st.image(LOGO_URL, width=110)
with c_title:
    st.title("Nashik Run Distribution")
    st.markdown("Live Inventory Tracking System")

st.markdown("---")

# TOP KPI CARDS
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""
    <div class="kpi-card theme-blue">
        <div class="kpi-label">Total Purchased</div>
        <div class="kpi-val">{int(purchased)}</div>
        <div class="kpi-sub">Supplier → Warehouse</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card theme-orange">
        <div class="kpi-label">Total Distributed</div>
        <div class="kpi-val">{int(consumed_total)}</div>
        <div class="kpi-sub">To Beneficiaries</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card theme-green">
        <div class="kpi-label">Current Stock</div>
        <div class="kpi-val">{int(remaining)}</div>
        <div class="kpi-sub">Available in Warehouse</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# INVENTORY GRID
st.subheader("📦 Live Inventory")
if not df_stock.empty:
    pivot_df = df_stock.pivot_table(index='organization', columns='size', values='quantity', aggfunc='sum', fill_value=0)
    cols = sorted(pivot_df.columns, key=lambda x: int(x) if x.isdigit() else 999)
    pivot_df = pivot_df[cols]
    pivot_df['TOTAL'] = pivot_df.sum(axis=1)
    sum_row = pivot_df.sum().to_frame().T
    sum_row.index = ["TOTAL"]
    final_df = pd.concat([pivot_df, sum_row])
    st.dataframe(final_df, use_container_width=True)
else:
    st.info("No data.")

st.markdown("---")

# REASONS GRID (ATTRACTIVE)
h_col, f_col = st.columns([3, 1])
with h_col: st.subheader("📊 Distribution by Reason")
with f_col: selected_org = st.selectbox("📍 Filter Location", ["All", "Bosch", "TDK", "Mathma Nagar"])

# Filter Logic
df_filt = df_out_all.copy()
if selected_org != "All" and not df_filt.empty:
    df_filt = df_filt[df_filt['organization'] == selected_org]

# Reason Data Mapping with Colors
reasons_map = [
    {"name": "Against Registration", "color": "c-reg"},
    {"name": "Cycle Rally", "color": "c-cyc"},
    {"name": "VIP Kit", "color": "c-vip"},
    {"name": "Against Donation", "color": "c-don"},
    {"name": "NGO/Beneficiary", "color": "c-ngo"},
    {"name": "Volunteers", "color": "c-vol"},
    {"name": "Flag off & Torch bearers", "color": "c-flg"}, 
    {"name": "Police", "color": "c-pol"},
    {"name": "Others", "color": "c-oth"},
]

# Calculate Counts
reason_counts = {}
if not df_filt.empty:
    grouped = df_filt.groupby('reason')['quantity'].sum()
    for r in reasons_map:
        reason_counts[r["name"]] = grouped.get(r["name"], 0)
else:
    for r in reasons_map: reason_counts[r["name"]] = 0

# Render 3x3 Grid
rows = [st.columns(3), st.columns(3), st.columns(3)]
idx = 0
for row in rows:
    for col in row:
        if idx < len(reasons_map):
            item = reasons_map[idx]
            val = reason_counts[item["name"]]
            with col:
                st.markdown(f"""
                <div class="reason-box">
                    <div class="reason-stripe {item['color']}"></div>
                    <div class="r-count">{int(val)}</div>
                    <div class="r-title">{item['name']}</div>
                </div>
                """, unsafe_allow_html=True)
            idx += 1

st.markdown("---")

# GRAPH
st.subheader(f"📈 Trends: {selected_org}")
if not df_filt.empty:
    chart_data = df_filt.groupby(['date', 'category'])['quantity'].sum().reset_index()
    chart_data['date'] = chart_data['date'].astype(str)
    
    c = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('date', title='Date', axis=alt.Axis(labelAngle=-45, grid=False)),
        y=alt.Y('quantity', title='Qty'),
        color=alt.Color('category', scale=alt.Scale(domain=['kids', 'adults'], range=['#f59e0b', '#3b82f6'])),
        tooltip=['date', 'category', 'quantity']
    ).properties(height=350, background='transparent').configure_view(strokeWidth=0)
    st.altair_chart(c, use_container_width=True)
else:
    st.info("No chart data available.")
