import streamlit as st
import pandas as pd
import sys
import os

# Set root path correctly for imports
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.agent_swarm import SupportGenSwarm
from tools.tools import OrderLookupTool

# Page Configuration
st.set_page_config(
    page_title="SupportGen-AI | Enterprise Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Custom CSS Styling
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        color: #38bdf8;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }
    .saas-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
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
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 0 12px rgba(2, 132, 199, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Load Orders & Products Data for Dynamic Selection
@st.cache_data
def load_support_dataset():
    try:
        orders_df = pd.read_csv('data/orders.csv')
        products_df = pd.read_csv('data/products.csv')
        customers_df = pd.read_csv('data/customers.csv')
        merged = orders_df.merge(products_df, on='product_id', how='left')
        merged = merged.merge(customers_df, on='customer_id', how='left')
        return merged
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return pd.DataFrame()

dataset = load_support_dataset()

# Initialize Backend Swarm with Correct Class Name
@st.cache_resource
def get_swarm_instance():
    return SupportGenSwarm()

swarm = get_swarm_instance()
order_tool = OrderLookupTool()

# Header Section
st.markdown("""
<div class="header-box">
    <div class="header-title">⚡ SupportGen-AI Swarm Engine</div>
    <div class="header-subtitle">Enterprise E-Commerce Support Automation Platform | ZentroMart Dataset</div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Controls & Dynamic Selection
st.sidebar.header("🎯 Context & Customer Controls")

if not dataset.empty:
    order_options = dataset.apply(
        lambda row: f"{row['order_id']} - {row['product_name']} ({row['name']})", axis=1
    ).tolist()
    
    selected_option = st.sidebar.selectbox("Select Active Customer Order:", order_options)
    selected_order_id = selected_option.split(" - ")[0]
    selected_row = dataset[dataset['order_id'] == selected_order_id].iloc[0]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Customer Profile")
    st.sidebar.text(f"Name: {selected_row['name']}")
    st.sidebar.text(f"Email: {selected_row['email']}")
    st.sidebar.text(f"Order ID: {selected_row['order_id']}")
else:
    selected_order_id = st.sidebar.text_input("Order ID", "ORD-901")
    selected_row = None

# Main Dashboard Grid
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="saas-card"><div class="card-title">💬 Customer Issue Dispatch</div>', unsafe_allow_html=True)
    query = st.text_area(
        "Support Query:",
        value="What is the return policy for damaged items and is my order eligible?",
        height=100
    )
    process_btn = st.button("🚀 Execute Swarm Resolution")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="saas-card"><div class="card-title">📦 Active Order Context</div>', unsafe_allow_html=True)
    if selected_row is not None:
        status_class = "badge-delivered" if str(selected_row['status']).lower() == 'delivered' else "badge-intransit"
        st.markdown(f"**Item:** {selected_row['product_name']}")
        st.markdown(f"**Price:** ${selected_row['price']}")
        st.markdown(f"**Order Date:** {selected_row['order_date']}")
        st.markdown(f'**Status:** <span class="status-badge {status_class}">{selected_row["status"]}</span>', unsafe_allow_html=True)
    else:
        st.info("Lookup active order context from sidebar.")
    st.markdown('</div>', unsafe_allow_html=True)

# Execution Results using correct method signature
if process_btn:
    st.markdown("---")
    st.subheader("⚡ Resolution Pipeline Execution")
    
    # Prepare customer data dictionary required by Agent1
    customer_payload = {
        "customer_id": str(selected_row['customer_id']) if selected_row is not None else "CUST-101",
        "name": str(selected_row['name']) if selected_row is not None else "Priyanshu",
        "email": str(selected_row['email']) if selected_row is not None else "priyanshu12tt@gmail.com"
    }
    
    with st.spinner("Swarm agents evaluating policy & order context..."):
        response = swarm.process_support_ticket(customer_payload, query)
        st.success("Resolution Generated Successfully!")
        st.markdown(f"""
        <div class="saas-card">
            <div class="card-title">📌 Agent Swarm Final Resolution</div>
            <p style="color: #cbd5e1; font-size: 15px; line-height: 1.6; white-space: pre-line;">{response}</p>
        </div>
        """, unsafe_allow_html=True)
