import streamlit as st
import pandas as pd
import re
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.agent_swarm import SupportGenSwarm

st.set_page_config(
    page_title="ZentroMart | SupportGen-AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra-Premium Dark Theme CSS for Entire Page (Main Body + Sidebar)
st.markdown("""
<style>
    /* Global Background Override */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0a0e17 !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Force Sidebar to match dark theme */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(10, 14, 23, 0.9) !important;
    }

    /* Premium ZentroMart Branding Banner */
    .brand-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
    }
    
    .brand-logo {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 14px;
        letter-spacing: 1px;
    }

    .brand-title {
        color: #f8fafc;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Section Cards Styling */
    .pre-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .card-title-pre {
        color: #38bdf8;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 10px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 6px;
    }

    .post-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-top: 18px;
    }

    .card-title-post {
        color: #34d399;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 12px;
        border-bottom: 1px solid #334155;
        padding-bottom: 6px;
    }

    .metric-label {
        color: #94a3b8;
        font-weight: 600;
        font-size: 13px;
    }

    .metric-val {
        color: #f1f5f9;
        font-size: 13px;
    }

    .badge {
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    .b-delivered { background-color: #065f46; color: #34d399; }
    .b-shipped { background-color: #1e3a8a; color: #60a5fa; }
    .b-cancelled { background-color: #7f1d1d; color: #fca5a5; }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-weight: 700;
        font-size: 14px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    }

    /* Key-Value Highlight CSS */
    .yaml-key { color: #60a5fa !important; font-weight: 700; }
    .yaml-val { color: #f59e0b !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

def format_policy_metadata(text: str) -> str:
    def replace_kv(match):
        key = match.group(1)
        val = match.group(2)
        return f'<span class="yaml-key">{key}:</span> <span class="yaml-val">{val}</span>'

    formatted = re.sub(r'([a-zA-Z0-9_]+):\s*([^\n<]+)', replace_kv, text)
    return formatted

@st.cache_data
def load_all_datasets():
    data_dir = os.path.join(ROOT_DIR, 'data')
    try:
        orders = pd.read_csv(os.path.join(data_dir, 'orders.csv'))
        customers = pd.read_csv(os.path.join(data_dir, 'customers.csv'))
        order_items = pd.read_csv(os.path.join(data_dir, 'order_items.csv'))
        products = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        pincodes = pd.read_csv(os.path.join(data_dir, 'pincodes.csv'))
        support_logs = pd.read_csv(os.path.join(data_dir, 'support_logs.csv'))
        
        orders['order_id'] = orders['order_id'].astype(str)
        order_items['order_id'] = order_items['order_id'].astype(str)
        
        return orders, customers, order_items, products, pincodes, support_logs
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

orders_df, customers_df, order_items_df, products_df, pincodes_df, support_logs_df = load_all_datasets()

@st.cache_resource
def get_swarm():
    return SupportGenSwarm()

swarm = get_swarm()

# Clean Executive Header
st.markdown("""
<div class="brand-banner">
    <span class="brand-logo">ZENTROMART</span>
    <span class="brand-title">SupportGen-AI</span>
</div>
""", unsafe_allow_html=True)

# Sidebar Control
st.sidebar.markdown("### 🎛️ Control Panel")
st.sidebar.markdown("---")

selected_oid = None
current_order = {}
current_customer = {}
current_items = pd.DataFrame()

if not orders_df.empty:
    merged_context = orders_df.merge(customers_df, on='customer_id', how='left')
    
    order_options = ["-- Select Customer Order --"]
    for _, row in merged_context.iterrows():
        oid = str(row['order_id'])
        cname = str(row.get('name', 'Customer'))
        status = str(row.get('status', 'processing')).upper()
        order_options.append(f"#{oid} | {cname} [{status}]")
    
    selected_option = st.sidebar.selectbox("Select Customer Order:", order_options)
    
    if selected_option != "-- Select Customer Order --":
        selected_oid = selected_option.split(" | ")[0].replace("#", "").strip()
        current_order = orders_df[orders_df['order_id'] == selected_oid].iloc[0]
        current_customer = customers_df[customers_df['customer_id'] == current_order['customer_id']].iloc[0] if not customers_df.empty else {}
        current_items = order_items_df[order_items_df['order_id'] == selected_oid]
        
        pincode_val = str(current_order.get('delivery_pincode', ''))
        pin_info = pincodes_df[pincodes_df['pincode'].astype(str) == pincode_val]
        is_serviceable = pin_info['serviceable'].values[0] if not pin_info.empty else True
        cod_avail = pin_info['cod_available'].values[0] if not pin_info.empty else True
        
        st.sidebar.markdown("#### 👤 Customer Profile")
        st.sidebar.info(f"""
        * **Name:** {current_customer.get('name', 'N/A')}
        * **Email:** {current_customer.get('email', 'N/A')}
        * **Location:** {pin_info['city'].values[0] if not pin_info.empty else 'N/A'}, {pin_info['state'].values[0] if not pin_info.empty else 'N/A'} (Pin: {pincode_val})
        * **Serviceable:** {'✅ Yes' if is_serviceable else '❌ No'} | **COD:** {'✅' if cod_avail else '❌'}
        """)
    else:
        st.sidebar.warning("No Order Selected. Select an order above.")

# Main Display
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="pre-card"><div class="card-title-pre">💬 Customer Support Dispatch</div>', unsafe_allow_html=True)
    query = st.text_area(
        "Enter Support Query / Issue:",
        value="What is the return policy for damaged items and is my order eligible?",
        height=110
    )
    run_swarm = st.button("🚀 Run Autonomous Swarm Resolution")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="pre-card"><div class="card-title-pre">📦 Order Items & Telemetry Details</div>', unsafe_allow_html=True)
    if selected_oid and not current_items.empty:
        st.markdown(f'<span class="metric-label">Order ID:</span> <span class="metric-val">`{selected_oid}`</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="metric-label">Payment / Type:</span> <span class="metric-val">{str(current_order.get("payment_method","")).upper()} | {str(current_order.get("delivery_type","")).capitalize()}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="metric-label">Total Amount:</span> <span class="metric-val">₹{current_order.get("total_inr", 0)}</span>', unsafe_allow_html=True)
        
        status_str = str(current_order.get("status", "shipped"))
        b_class = "b-delivered" if status_str=='delivered' else ("b-shipped" if status_str=='shipped' else "b-cancelled")
        st.markdown(f'<span class="metric-label">Status:</span> <span class="badge {b_class}">{status_str.upper()}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**Ordered SKUs / Items:**")
        for _, item in current_items.iterrows():
            st.markdown(f"- **{item.get('title')}** (Qty: {item.get('qty')} | ₹{item.get('unit_price_inr')})")
    else:
        st.info("Select an order from the left sidebar to load context.")
    st.markdown('</div>', unsafe_allow_html=True)

# Output Section
if run_swarm:
    st.markdown("---")
    st.subheader("⚡ Multi-Agent Swarm Resolution Pipeline Execution")
    
    cust_payload = {
        "customer_id": str(current_customer.get('customer_id', 'C100000')) if selected_oid else "None",
        "name": str(current_customer.get('name', 'Guest User')) if selected_oid else "Guest User",
        "email": str(current_customer.get('email', 'guest@example.com')) if selected_oid else "guest@example.com"
    }
    
    with st.spinner("Executing Swarm Agents..."):
        raw_response = swarm.process_support_ticket(cust_payload, query)
        formatted_response = format_policy_metadata(raw_response)
        
        st.success("Resolution Generated Successfully!")
        st.markdown(f"""
        <div class="post-card">
            <div class="card-title-post">📌 Final Agent Swarm Resolution & Policy Attribution</div>
            <div style="color: #e2e8f0; font-size: 14px; line-height: 1.8; background: #020617; padding: 18px; border-radius: 8px; border: 1px solid #1e293b;">
                {formatted_response.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
