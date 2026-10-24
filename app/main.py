import streamlit as st
import pandas as pd
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.agent_swarm import SupportGenSwarm

st.set_page_config(
    page_title="SupportGen-AI | Enterprise Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise SaaS Styling
st.markdown("""
<style>
    .main {
        background-color: #0b0f19;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #6366f1;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 25px rgba(99, 102, 241, 0.2);
    }
    .hero-title {
        color: #818cf8;
        font-size: 30px;
        font-weight: 800;
        margin: 0;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 5px;
    }
    .card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .card-title {
        color: #f3f4f6;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 10px;
        border-bottom: 1px solid #374151;
        padding-bottom: 6px;
    }
    .metric-label {
        color: #38bdf8;
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
    .b-returned { background-color: #581c87; color: #d8b4fe; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-weight: 700;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 100%, #3730a3 100%);
    }
</style>
""", unsafe_allow_html=True)

# Comprehensive Multi-Dataset Loader
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
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

orders_df, customers_df, order_items_df, products_df, pincodes_df, support_logs_df = load_all_datasets()

@st.cache_resource
def get_swarm():
    return SupportGenSwarm()

swarm = get_swarm()

# Header
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">SupportGen-AI Enterprise Hub</div>
    <div class="hero-sub">Fully Integrated Multi-Agent E-Commerce Resolution & Telemetry Platform</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ Control & Telemetry Panel")
st.sidebar.markdown("---")

if not orders_df.empty:
    # Merge orders with customers for rich selection context
    merged_context = orders_df.merge(customers_df, on='customer_id', how='left')
    
    order_options = []
    for _, row in merged_context.iterrows():
        oid = str(row['order_id'])
        cname = str(row.get('name', 'Customer'))
        status = str(row.get('status', 'processing')).upper()
        order_options.append(f"#{oid} | {cname} [{status}]")
    
    selected_option = st.sidebar.selectbox("Select Customer Order:", order_options)
    selected_oid = selected_option.split(" | ")[0].replace("#", "").strip()
    
    current_order = orders_df[orders_df['order_id'] == selected_oid].iloc[0]
    current_customer = customers_df[customers_df['customer_id'] == current_order['customer_id']].iloc[0] if not customers_df.empty else {}
    current_items = order_items_df[order_items_df['order_id'] == selected_oid]
    
    # Check pincode serviceability from pincodes dataset
    pincode_val = str(current_order.get('delivery_pincode', ''))
    pin_info = pincodes_df[pincodes_df['pincode'].astype(str) == pincode_val]
    is_serviceable = pin_info['serviceable'].values[0] if not pin_info.empty else True
    cod_avail = pin_info['cod_available'].values[0] if not pin_info.empty else True
    
    st.sidebar.markdown("#### 👤 Customer Profile")
    st.sidebar.info(f"""
    * **Name:** {current_customer.get('name', 'N/A')}
    * **Email:** {current_customer.get('email', 'N/A')}
    * **Location:** {pin_info['city'].values[0] if not pin_info.empty else 'N/A'}, {pin_info['state'].values[0] if not pin_info.empty else 'N/A'} (Pin: {pincode_val})
    * **Serviceable Hub:** {'✅ Yes' if is_serviceable else '❌ No'} | **COD:** {'✅' if cod_avail else '❌'}
    """)
else:
    selected_oid = "69520867"
    current_order = {}
    current_customer = {}
    current_items = pd.DataFrame()

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="card"><div class="card-title">💬 Customer Support Dispatch</div>', unsafe_allow_html=True)
    query = st.text_area(
        "Enter Support Query / Issue:",
        value="What is the return policy for damaged items and is my order eligible?",
        height=110
    )
    run_swarm = st.button("🚀 Run Autonomous Swarm Resolution")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📦 Order Items & Telemetry Details</div>', unsafe_allow_html=True)
    if not current_items.empty:
        st.markdown(f'<span class="metric-label">Order ID:</span> <span class="metric-val">`{selected_oid}`</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="metric-label">Payment / Type:</span> <span class="metric-val">{str(current_order.get("payment_method","")).upper()} | {str(current_order.get("delivery_type","")).capitalize()}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="metric-label">Total Amount:</span> <span class="metric-val">₹{current_order.get("total_inr", 0)}</span>', unsafe_allow_html=True)
        
        status_str = str(current_order.get("status", "shipped"))
        b_class = "b-delivered" if status_str=='delivered' else ("b-shipped" if status_str=='shipped' else ("b-cancelled" if status_str=='cancelled' else "b-returned"))
        st.markdown(f'<span class="metric-label">Status:</span> <span class="badge {b_class}">{status_str.upper()}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**Ordered SKUs / Items:**")
        for _, item in current_items.iterrows():
            st.markdown(f"- **{item.get('title')}** (Qty: {item.get('qty')} | ₹{item.get('unit_price_inr')})")
    else:
        st.markdown("No items found for this order.")
    st.markdown('</div>', unsafe_allow_html=True)

if run_swarm:
    st.markdown("---")
    st.subheader("⚡ Multi-Agent Swarm Resolution Pipeline Execution")
    
    cust_payload = {
        "customer_id": str(current_customer.get('customer_id', 'C100124')),
        "name": str(current_customer.get('name', 'Customer')),
        "email": str(current_customer.get('email', 'customer@example.com'))
    }
    
    with st.spinner("Executing Autonomous Swarm Agents across database models..."):
        response = swarm.process_support_ticket(cust_payload, query)
        st.success("Resolution Generated Successfully via Swarm Pipeline!")
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📌 Final Agent Swarm Resolution & Policy Attribution</div>
            <div style="color: #e2e8f0; font-size: 14px; line-height: 1.6; background: #030712; padding: 16px; border-radius: 8px; border: 1px solid #1f2937;">
                {response.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
