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

# Enterprise SaaS Light Theme CSS
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    [data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.9) !important;
    }

    .brand-banner {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    }
    
    .brand-logo-badge {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        color: #ffffff !important;
        padding: 8px 16px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 15px;
        letter-spacing: 1.2px;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }

    .brand-title {
        color: #0f172a !important;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .clean-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
    }

    .card-header-label {
        color: #0284c7 !important;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 16px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
        display: block;
    }

    .metric-label {
        color: #64748b !important;
        font-weight: 600;
        font-size: 14px;
    }

    .metric-val {
        color: #0f172a !important;
        font-weight: 700;
        font-size: 14px;
    }

    .badge {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
    }
    .b-delivered { background-color: #d1fae5; color: #047857 !important; }
    .b-shipped { background-color: #dbeafe; color: #1d4ed8 !important; }
    .b-cancelled { background-color: #fee2e2; color: #b91c1c !important; }
</style>
""", unsafe_allow_html=True)

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
        holidays = pd.read_csv(os.path.join(data_dir, 'holidays.csv'))
        
        orders['order_id'] = orders['order_id'].astype(str)
        order_items['order_id'] = order_items['order_id'].astype(str)
        
        return orders, customers, order_items, products, pincodes, support_logs, holidays
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

orders_df, customers_df, order_items_df, products_df, pincodes_df, support_logs_df, holidays_df = load_all_datasets()

# Header Display
st.markdown("""
<div class="brand-banner">
    <div class="brand-logo-badge">⚡ ZENTROMART</div>
    <span class="brand-title">SupportGen-AI Enterprise Hub</span>
</div>
""", unsafe_allow_html=True)

# Sidebar Control Panel with Quick Search & Comprehensive Customer Profile
st.sidebar.markdown("### ⚙️ Control Panel")
st.sidebar.markdown("---")

selected_oid = None
current_order = {}
current_customer = {}
current_items = pd.DataFrame()

if not orders_df.empty:
    merged_context = orders_df.merge(customers_df, on='customer_id', how='left')
    
    # Quick Search Bar
    search_query = st.sidebar.text_input("🔍 Quick Search (Order ID / Name):", "").strip()
    
    filtered_context = merged_context
    if search_query:
        filtered_context = merged_context[
            merged_context['order_id'].str.contains(search_query, case=False, na=False) |
            merged_context['name'].str.contains(search_query, case=False, na=False)
        ]
    
    order_options = ["-- Select Customer Order --"]
    for _, row in filtered_context.iterrows():
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
        
        # Comprehensive Customer Bio Data Profile
        st.sidebar.markdown("#### 👤 Comprehensive Customer Profile")
        st.sidebar.info(f"""
        * **Customer ID:** `{current_customer.get('customer_id', 'N/A')}`
        * **Name:** {current_customer.get('name', 'N/A')}
        * **Email:** {current_customer.get('email', 'N/A')}
        * **Phone:** {current_customer.get('phone', 'N/A')}
        * **Member Since:** {current_customer.get('created_at', 'N/A')}
        * **Location:** {pin_info['city'].values[0] if not pin_info.empty else 'N/A'}, {pin_info['state'].values[0] if not pin_info.empty else 'N/A'} (Pin: {pincode_val})
        * **Serviceable:** {'✅ Yes' if is_serviceable else '❌ No'} | **COD:** {'✅' if cod_avail else '❌'}
        """)
    else:
        st.sidebar.warning("No Order Selected. Select an order above.")

# Main Display: Prominent Order Items & Telemetry Details box
st.markdown("""
<div class="clean-card">
    <span class="card-header-label">📦 Order Items & Telemetry Details</span>
""", unsafe_allow_html=True)

if selected_oid and not current_items.empty:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<span class="metric-label">Order ID:</span> <span class="metric-val">`{selected_oid}`</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="metric-label">Payment / Type:</span> <span class="metric-val">{str(current_order.get("payment_method","")).upper()} | {str(current_order.get("delivery_type","")).capitalize()}</span>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<span class="metric-label">Total Amount:</span> <span class="metric-val">₹{current_order.get("total_inr", 0)}</span>', unsafe_allow_html=True)
        status_str = str(current_order.get("status", "shipped"))
        b_class = "b-delivered" if status_str=='delivered' else ("b-shipped" if status_str=='shipped' else "b-cancelled")
        st.markdown(f'<span class="metric-label">Status:</span> <span class="badge {b_class}">{status_str.upper()}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Ordered SKUs / Items:**")
    for _, item in current_items.iterrows():
        st.markdown(f"- **{item.get('title')}** (Qty: {item.get('qty')} | ₹{item.get('unit_price_inr')})")
else:
    st.info("Select an order from the left sidebar to load complete depth telemetry and item details.")

st.markdown('</div>', unsafe_allow_html=True)
