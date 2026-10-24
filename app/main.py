import streamlit as st
import pandas as pd
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.agent_swarm import SupportGenSwarm

st.set_page_config(
    page_title="SupportGen-AI | Enterprise Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .animated-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #38bdf8;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        text-align: center;
    }
    .header-title {
        color: #38bdf8;
        font-size: 32px;
        font-weight: 800;
        margin: 0;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }
    .saas-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-title {
        color: #f1f5f9;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-delivered { background-color: #065f46; color: #34d399; }
    .badge-intransit { background-color: #854d0e; color: #fbbf24; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_support_dataset():
    try:
        orders_path = os.path.join(ROOT_DIR, 'data', 'orders.csv')
        products_path = os.path.join(ROOT_DIR, 'data', 'products.csv')
        customers_path = os.path.join(ROOT_DIR, 'data', 'customers.csv')
        
        if not os.path.exists(orders_path):
            return pd.DataFrame()
            
        orders_df = pd.read_csv(orders_path)
        orders_df['order_id'] = orders_df['order_id'].astype(str)
        
        products_df = pd.read_csv(products_path) if os.path.exists(products_path) else pd.DataFrame()
        customers_df = pd.read_csv(customers_path) if os.path.exists(customers_path) else pd.DataFrame()
        
        merged = orders_df
        if not products_df.empty and 'product_id' in merged.columns and 'product_id' in products_df.columns:
            merged = merged.merge(products_df, on='product_id', how='left')
        if not customers_df.empty and 'customer_id' in merged.columns and 'customer_id' in customers_df.columns:
            merged = merged.merge(customers_df, on='customer_id', how='left')
            
        return merged
    except Exception as e:
        return pd.DataFrame()

dataset = load_support_dataset()

@st.cache_resource
def get_swarm_instance():
    return SupportGenSwarm()

swarm = get_swarm_instance()

# Clean Header as requested
st.markdown("""
<div class="animated-header">
    <div class="header-title">SupportGen-AI</div>
    <div class="header-subtitle">Autonomous Multi-Agent E-Commerce Support & Policy Resolution Engine</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("🎯 Enterprise Control Panel")
st.sidebar.markdown("---")

selected_row = None
selected_order_id = "ORD-901"

if not dataset.empty and 'order_id' in dataset.columns:
    order_options = []
    for _, row in dataset.iterrows():
        o_id = str(row.get('order_id', 'ORD'))
        p_name = str(row.get('product_name', row.get('product_id', 'Item')))
        c_name = str(row.get('name', row.get('customer_id', 'Customer')))
        order_options.append(f"{o_id} — {p_name} ({c_name})")
    
    selected_option = st.sidebar.selectbox("Select Customer Order Context:", order_options)
    selected_order_id = selected_option.split(" — ")[0].strip()
    
    matched_rows = dataset[dataset['order_id'].astype(str) == str(selected_order_id)]
    if not matched_rows.empty:
        selected_row = matched_rows.iloc[0]
    
    if selected_row is not None:
        st.sidebar.markdown("### 👤 Active Customer Profile")
        st.sidebar.info(f"""
        * **Name:** {selected_row.get('name', 'Valued Customer')}
        * **Email:** {selected_row.get('email', 'customer@zentromart.com')}
        * **Order ID:** {selected_row.get('order_id', 'ORD-901')}
        """)
else:
    selected_order_id = st.sidebar.text_input("Order ID", "ORD-901")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="saas-card"><div class="card-title">💬 Customer Issue Dispatch</div>', unsafe_allow_html=True)
    query = st.text_area(
        "Support Query / Issue Description:",
        value="What is the return policy for damaged items and is my order eligible?",
        height=110
    )
    process_btn = st.button("🚀 Execute Autonomous Swarm Resolution")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="saas-card"><div class="card-title">📦 Active Order Context & Telemetry</div>', unsafe_allow_html=True)
    if selected_row is not None:
        status = str(selected_row.get('status', 'Delivered'))
        status_class = "badge-delivered" if status.lower() == 'delivered' else "badge-intransit"
        st.markdown(f"**Order ID:** `{selected_row.get('order_id')}`")
        st.markdown(f"**Item Name:** {selected_row.get('product_name', 'ZentroMart Premium Item')}")
        st.markdown(f"**Price:** ${selected_row.get('price', '99.99')}")
        st.markdown(f"**Order Date:** {selected_row.get('order_date', '2026-10-20')}")
        st.markdown(f'**Fulfillment Status:** <span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
    else:
        st.markdown("**Order ID:** `ORD-901`")
        st.markdown("**Item Name:** ZentroMart Smart Watch Pro")
        st.markdown("**Price:** $149.99")
        st.markdown('**Status:** <span class="status-badge badge-delivered">Delivered</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if process_btn:
    st.markdown("---")
    st.subheader("⚡ Multi-Agent Swarm Pipeline Execution")
    
    customer_payload = {
        "customer_id": str(selected_row.get('customer_id', 'CUST-101')) if selected_row is not None else "CUST-101",
        "name": str(selected_row.get('name', 'Priyanshu')) if selected_row is not None else "Priyanshu",
        "email": str(selected_row.get('email', 'priyanshu12tt@gmail.com')) if selected_row is not None else "priyanshu12tt@gmail.com"
    }
    
    with st.spinner("Autonomous Swarm Agents processing..."):
        response = swarm.process_support_ticket(customer_payload, query)
        st.success("Resolution Pipeline Executed Successfully!")
        st.markdown(f"""
        <div class="saas-card">
            <div class="card-title">📌 Agent Swarm Final Resolution & Policy Attribution</div>
            <div style="color: #e2e8f0; font-size: 15px; line-height: 1.7; background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155;">
                {response.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
