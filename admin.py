import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Nashik Run T-Shirt Distribution",
    page_icon="👕"
)

# --- LOGO & CREDENTIALS ---
LOGO_URL = "https://github.com/nincoreultra5/Admin-dashboard-version-1/raw/main/nsk.png"
SUPABASE_URL = "https://ocokfyepdgirquwkhbhs.supabase.co".strip()
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jb2tmeWVwZGdpcnF1d2toYmhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU5MzU5NjQsImV4cCI6MjA4MTUxMTk2NH0.x6onqjC02j5FTXikDw_5eBaaaPQDDTdFnGkZOfdxoOA".strip()

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS (NAVBAR + PREMIUM TABLE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(1000px 480px at 10% 0%, rgba(99,102,241,0.14) 0%, rgba(99,102,241,0) 60%),
        radial-gradient(900px 520px at 90% 5%, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0) 55%),
        linear-gradient(180deg, #f8fafc 0%, #f3f4f6 100%);
}

/* Make room so logo never hides under Streamlit top header */
.block-container { padding-top: 4.6rem; padding-bottom: 2.0rem; }

/* Navbar container */
.navbar {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(15,23,42,0.06);
    box-shadow: 0 10px 24px rgba(15,23,42,0.08);
    border-radius: 16px;
    padding: 12px 14px;
}
.nav-title {
    font-size: 1.9rem;
    font-weight: 950;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.nav-sub {
    margin-top: 2px;
    font-size: 0.95rem;
    font-weight: 700;
    color: rgba(15,23,42,0.70);
}

/* KPI cards */
.kpi-card {
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 10px 22px rgba(15,23,42,0.08);
    text-align: left;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    border: 1px solid rgba(15,23,42,0.06);
    position: relative;
    overflow: hidden;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 14px 32px rgba(15,23,42,0.12); }
.kpi-title { font-size: 0.85rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; opacity: 0.9; }
.kpi-value { font-size: 2.25rem; font-weight: 950; margin-bottom: 6px; line-height: 1.05; }
.kpi-note { font-size: 0.9rem; opacity: 0.85; font-weight: 700; }

/* KPI themes */
.blue-theme { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 55%, #e0f2fe 100%); color: #0b3a91; border-left: 6px solid #2563eb; }
.orange-theme { background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 55%, #ffe4e6 100%); color: #9a3412; border-left: 6px solid #ea580c; }
.green-theme { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 55%, #ecfdf5 100%); color: #14532d; border-left: 6px solid #16a34a; }

/* Distribution cards */
.reason-card {
    --accent: #6366f1;
    --bg1: rgba(99,102,241,0.18);
    --bg2: rgba(56,189,248,0.12);
    background: linear-gradient(135deg, var(--bg1), var(--bg2));
    border: 1px solid rgba(15,23,42,0.06);
    border-left: 6px solid var(--accent);
    padding: 14px 14px;
    border-radius: 16px;
    box-shadow: 0 10px 22px rgba(15,23,42,0.08);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    min-height: 122px;
    position: relative;
    overflow: hidden;
    margin-bottom: 12px;
}
.reason-card:hover { transform: translateY(-4px); box-shadow: 0 14px 32px rgba(15,23,42,0.12); }
.reason-top { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; margin-bottom:8px; }
.reason-label { font-size:0.92rem; font-weight:950; color: rgba(15,23,42,0.88); line-height:1.2; }
.reason-icon { font-size:1.1rem; padding:6px 8px; border-radius:10px; background: rgba(255,255,255,0.7); border: 1px solid rgba(15,23,42,0.06); }
.reason-number { font-size:2.05rem; font-weight:950; color:#0f172a; line-height:1.0; margin:6px 0 10px 0; }
.reason-bar { height:10px; background: rgba(255,255,255,0.65); border: 1px solid rgba(15,23,42,0.06); border-radius:999px; overflow:hidden; }
.reason-bar > div { height:100%; width:0%; background: linear-gradient(90deg, var(--accent), rgba(255,255,255,0.0)); border-radius:999px; }
.reason-card:after {
    content:""; position:absolute; top:-60px; right:-80px; width:220px; height:220px; border-radius:999px;
    background: radial-gradient(circle, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0) 70%);
    transform: rotate(18deg);
}

/* PREMIUM INVENTORY TABLE (HTML) */
.table-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(15,23,42,0.06);
    border-radius: 16px;
    box-shadow: 0 10px 22px rgba(15,23,42,0.06);
    padding: 10px 10px;
    overflow-x: auto;
}
.inv-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.95rem;
}
.inv-table thead th {
    position: sticky;
    top: 0;
    background: rgba(255,255,255,0.98);
    color: #0f172a;
    font-weight: 950;
    border-bottom: 1px solid rgba(15,23,42,0.10);
    padding: 10px 10px;
    text-align: center;
    white-space: nowrap;
}
.inv-table tbody th {
    text-align: left;
    padding: 10px 10px;
    font-weight: 950;
    color: #0f172a;
    border-bottom: 1px solid rgba(15,23,42,0.06);
    white-space: nowrap;
}
.inv-table td {
    text-align: center;
    padding: 10px 10px;
    border-bottom: 1px solid rgba(15,23,42,0.06);
    white-space: nowrap;
    color: rgba(15,23,42,0.92);
    font-weight: 700;
}
.inv-table tbody tr:hover td, .inv-table tbody tr:hover th {
    background: rgba(15,23,42,0.03);
}

/* Row accents */
.row-warehouse th, .row-warehouse td { background: rgba(34,197,94,0.08); }
.row-warehouse th { border-left: 6px solid #22c55e; }

/* Mahatma (Online/Offline) theme */
.row-mahatma th, .row-mahatma td { background: rgba(168,85,247,0.08); }
.row-mahatma th { border-left: 6px solid #a855f7; }

.row-bosch th, .row-bosch td { background: rgba(239,68,68,0.10); color:#7f1d1d; }
.row-bosch th { border-left: 6px solid #ef4444; }

.row-tdk th, .row-tdk td { background: rgba(59,130,246,0.10); color:#1e3a8a; }
.row-tdk th { border-left: 6px solid #3b82f6; }

.row-total th, .row-total td { background: rgba(15,23,42,0.08); font-weight: 950; }
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
    if not supabase:
        return pd.DataFrame(), pd.DataFrame()

    # Supabase Python select pattern: .table(...).select(...).execute().data [web:69]
    stock_data = supabase.table("stock").select("*").execute().data
    trans_data = supabase.table("transactions").select("*").execute().data

    df_s = pd.DataFrame(stock_data or [])
    df_t = pd.DataFrame(trans_data or [])

    if not df_t.empty:
        df_t["created_at"] = pd.to_datetime(df_t["created_at"], errors="coerce")
        df_t = df_t.dropna(subset=["created_at"])
        df_t["date"] = df_t["created_at"].dt.date

    return df_s, df_t

df_stock, df_trans = get_data()

# Metrics
purchased = 0
consumed_total = 0
remaining = 0
df_out_all = pd.DataFrame()

if not df_trans.empty:
    purchased = df_trans[(df_trans["organization"] == "Warehouse") & (df_trans["type"] == "in")]["quantity"].sum()
    df_out_all = df_trans[(df_trans["organization"] != "Warehouse") & (df_trans["type"] == "out")]
    consumed_total = df_out_all["quantity"].sum()

if not df_stock.empty:
    remaining = df_stock[df_stock["organization"] == "Warehouse"]["quantity"].sum()

# -----------------------------------------------------------------------------
# 4. NAVBAR
# -----------------------------------------------------------------------------
nav1, nav2 = st.columns([1.2, 7], vertical_alignment="center")
with nav1:
    st.image(LOGO_URL, width=110)
with nav2:
    st.markdown("""
    <div class="navbar">
        <div class="nav-title">Nashik Run T-Shirt disturibution</div>
        <div class="nav-sub">Live Inventory Analysis & Tracking System</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. KPI CARDS
# -----------------------------------------------------------------------------
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
        <div class="kpi-note">Bosch, TDK, Mahatma Nagar Online/Offline</div>
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

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. INVENTORY GRID (HTML TABLE - STABLE + BEAUTIFUL)
# -----------------------------------------------------------------------------
st.subheader("📦 Inventory Grid")

def _safe_int_sort(x):
    x = str(x)
    return int(x) if x.isdigit() else 10**9

def normalize_org(name: str) -> str:
    return " ".join(str(name).strip().lower().split())

def make_inventory_table_html(df: pd.DataFrame) -> str:
    pivot_df = df.pivot_table(index="organization", columns="size", values="quantity", aggfunc="sum", fill_value=0)
    cols = sorted(pivot_df.columns, key=_safe_int_sort)
    pivot_df = pivot_df[cols]
    pivot_df["TOTAL"] = pivot_df.sum(axis=1)

    sum_row = pivot_df.sum().to_frame().T
    sum_row.index = ["TOTAL"]
    final_df = pd.concat([pivot_df, sum_row])

    desired_norm = [
        "warehouse",
        "mahatma nagar online",
        "mahatma nagar offline",
        "bosch",
        "tdk",
        "total",
    ]

    norm_to_original = {}
    for original in final_df.index.astype(str).tolist():
        n = normalize_org(original)
        if n not in norm_to_original:
            norm_to_original[n] = original

    ordered_original = []
    for n in desired_norm:
        if n in norm_to_original:
            ordered_original.append(norm_to_original[n])

    for original in final_df.index.astype(str).tolist():
        if original not in ordered_original:
            ordered_original.append(original)

    final_df = final_df.loc[ordered_original]
    header_cols = ["Organization"] + [str(c) for c in final_df.columns]

    def row_class(org_label: str) -> str:
        n = normalize_org(org_label)
        if n == "warehouse":
            return "row-warehouse"
        if n in ["mahatma nagar online", "mahatma nagar offline"]:
            return "row-mahatma"
        if n == "bosch":
            return "row-bosch"
        if n == "tdk":
            return "row-tdk"
        if n == "total":
            return "row-total"
        return ""

    html = []
    html.append('<div class="table-card">')
    html.append('<table class="inv-table">')

    html.append("<thead><tr>")
    for h in header_cols:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead>")

    html.append("<tbody>")
    for org_label, row in final_df.iterrows():
        cls = row_class(str(org_label))
        html.append(f'<tr class="{cls}">')
        html.append(f"<th>{org_label}</th>")
        for c in final_df.columns:
            val = row[c]
            try:
                val = int(val)
            except Exception:
                pass
            html.append(f"<td>{val}</td>")
        html.append("</tr>")
    html.append("</tbody>")

    html.append("</table></div>")
    return "".join(html)

if df_stock.empty:
    st.info("No data available.")
else:
    st.markdown(make_inventory_table_html(df_stock), unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. DISTRIBUTION BY HEAD (ATTRACTIVE CARDS) — Mahatma only 2 reasons
# -----------------------------------------------------------------------------
c1, c2 = st.columns([3, 1], vertical_alignment="center")
with c1:
    st.subheader("📋 Distribution by Head")
with c2:
    selected_org = st.selectbox(
        "📍 Filter Location",
        ["All", "Bosch", "TDK", "Mahatma Nagar Online", "Mahatma Nagar Offline"],
        index=0
    )  # selectbox filtering usage [web:141]

df_filtered = df_out_all.copy()
if selected_org != "All" and not df_filtered.empty:
    df_filtered = df_filtered[df_filtered["organization"] == selected_org]  # filtering pattern [web:137]

ALL_REASONS = [
    "Against Registration", "Cycle Rally", "VIP Kit",
    "Against Donation", "NGO/Beneficiary", "Volunteers",
    "Flag off & Torch bearers", "Police", "Others"
]

MAHATMA_REASONS = [
    "Distribute by Head",
    "Others"
]

if selected_org in ["Mahatma Nagar Online", "Mahatma Nagar Offline"]:
    reasons_list = MAHATMA_REASONS
else:
    reasons_list = ALL_REASONS

REASON_THEME = {
    "Against Registration": {"accent": "#2563eb", "bg1": "rgba(37,99,235,0.18)", "bg2": "rgba(56,189,248,0.14)", "icon": "📝"},
    "Cycle Rally": {"accent": "#0ea5e9", "bg1": "rgba(14,165,233,0.18)", "bg2": "rgba(125,211,252,0.14)", "icon": "🚴"},
    "VIP Kit": {"accent": "#a855f7", "bg1": "rgba(168,85,247,0.18)", "bg2": "rgba(236,72,153,0.12)", "icon": "🎟️"},
    "Against Donation": {"accent": "#f97316", "bg1": "rgba(249,115,22,0.18)", "bg2": "rgba(251,146,60,0.14)", "icon": "🧾"},
    "NGO/Beneficiary": {"accent": "#22c55e", "bg1": "rgba(34,197,94,0.18)", "bg2": "rgba(16,185,129,0.12)", "icon": "🤝"},
    "Volunteers": {"accent": "#10b981", "bg1": "rgba(16,185,129,0.18)", "bg2": "rgba(52,211,153,0.12)", "icon": "🧑‍🤝‍🧑"},
    "Flag off & Torch bearers": {"accent": "#e11d48", "bg1": "rgba(225,29,72,0.16)", "bg2": "rgba(251,113,133,0.12)", "icon": "🔥"},
    "Police": {"accent": "#334155", "bg1": "rgba(51,65,85,0.14)", "bg2": "rgba(148,163,184,0.12)", "icon": "🛡️"},
    "Others": {"accent": "#6366f1", "bg1": "rgba(99,102,241,0.18)", "bg2": "rgba(129,140,248,0.12)", "icon": "📦"},

    # Mahatma-specific reason card
    "Distribute by Head": {"accent": "#a855f7", "bg1": "rgba(168,85,247,0.18)", "bg2": "rgba(34,197,94,0.10)", "icon": "🧑‍💼"},
}

reason_counts = {r: 0 for r in reasons_list}
if not df_filtered.empty:
    grouped = df_filtered.groupby("reason")["quantity"].sum()  # groupby pattern [web:152]
    for r in reasons_list:
        reason_counts[r] = float(grouped.get(r, 0))

max_reason_value = max(reason_counts.values()) if reason_counts else 0
if max_reason_value <= 0:
    max_reason_value = 1

# Layout: if only 2 reasons, show 2 cards in 2 columns; otherwise keep 3x3 grid
if len(reasons_list) <= 2:
    layout_rows = [st.columns(2)]
else:
    layout_rows = [st.columns(3), st.columns(3), st.columns(3)]

idx = 0
for row in layout_rows:
    for col in row:
        if idx >= len(reasons_list):
            continue

        r_name = reasons_list[idx]
        r_val = reason_counts.get(r_name, 0)
        pct = max(0, min(100, (r_val / max_reason_value) * 100))
        theme = REASON_THEME.get(r_name, {"accent": "#6366f1", "bg1": "rgba(99,102,241,0.18)", "bg2": "rgba(56,189,248,0.12)", "icon": "📌"})

        with col:
            st.markdown(f"""
            <div class="reason-card" style="--accent:{theme['accent']}; --bg1:{theme['bg1']}; --bg2:{theme['bg2']};">
                <div class="reason-top">
                    <div class="reason-label">{r_name}</div>
                    <div class="reason-icon">{theme['icon']}</div>
                </div>
                <div class="reason-number">{int(r_val)}</div>
                <div class="reason-bar">
                    <div style="width:{pct:.1f}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        idx += 1

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. TREND GRAPH
# -----------------------------------------------------------------------------
st.subheader(f"📈 Daily Trend: {selected_org}")

if not df_filtered.empty and "date" in df_filtered.columns:
    chart_data = df_filtered.groupby(["date", "category"])["quantity"].sum().reset_index()
    chart_data["date"] = chart_data["date"].astype(str)

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("date", title="Date", axis=alt.Axis(labelAngle=-45, grid=False)),
            y=alt.Y("quantity", title="Count"),
            color=alt.Color(
                "category",
                scale=alt.Scale(domain=["kids", "adults"], range=["#f97316", "#3b82f6"]),
                title="Category",
            ),
            tooltip=["date", "category", "quantity"],
        )
        .properties(height=420, background="transparent")
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.warning(f"No distribution data for {selected_org}")
