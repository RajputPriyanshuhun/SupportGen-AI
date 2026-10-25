import streamlit as st
import pandas as pd
import re
import sys
import os
from fpdf import FPDF

# PDF Generation Class using FPDF
class SupportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ZENTROMART | SupportGen-AI Enterprise Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 6, 'Automated Multi-Agent Swarm Resolution Audit Document', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Confidential - Internal Company Use Only | Page {self.page_no()}', 0, 0, 'C')

def generate_support_pdf(order_id, customer_name, customer_email, query_text, resolution_text):
    pdf = SupportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)
    
    # Safe text encoder to prevent UnicodeEncodeError and clean markdown symbols
    def safe_text(txt):
        if not isinstance(txt, str):
            txt = str(txt)
        txt = txt.replace('**', '').replace('__', '').replace('`', '').replace('₹', 'INR ')
        return txt.encode('latin-1', 'replace').decode('latin-1')

    # Section 1: Customer & Order Telemetry
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, safe_text("1. Customer & Order Telemetry"), 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, safe_text(f"Order ID: #{order_id}"), 0, 1)
    pdf.cell(0, 6, safe_text(f"Customer Name: {customer_name}"), 0, 1)
    pdf.cell(0, 6, safe_text(f"Customer Email: {customer_email}"), 0, 1)
    pdf.ln(4)
    
    # Section 2: Support Dispatch Query
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, safe_text("2. Support Dispatch Query / Issue"), 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, safe_text(query_text))
    pdf.ln(4)
    
    # Section 3: Autonomous Swarm Resolution
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, safe_text("3. Autonomous Swarm Resolution & Policy Attribution"), 0, 1)
    pdf.set_font("Arial", "", 10)
    
    clean_res = re.sub(r'#+\s*', '', resolution_text)
    for line in clean_res.split('\n'):
        pdf.multi_cell(0, 6, safe_text(line))
    
    # Robust byte output handling for Python 3 FPDF
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin1', errors='ignore')
    return bytes(pdf_output)

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

    .stTextArea textarea, div[data-baseweb="textarea"] textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    .post-card {
        background-color: #ffffff;
        border: 1.5px solid #cbd5e1;
        border-radius: 12px;
        padding: 24px;
        margin-top: 18px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    }

    .card-title-post {
        color: #059669 !important;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 14px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-weight: 700;
        font-size: 15px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
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

    .policy-content-box {
        color: #1e293b !important;
        font-size: 15px;
        line-height: 1.8;
        background: #f8fafc;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

def clean_and_format_policy(text: str) -> str:
    cleaned = re.sub(r'^---[\s\S]*?---\s*', '', text, flags=re.MULTILINE).strip()
    return cleaned

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
        support_logs['order_id'] = support_logs['order_id'].astype(str) if 'order_id' in support_logs.columns else pd.Series()
        
        return orders, customers, order_items, products, pincodes, support_logs, holidays
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

orders_df, customers_df, order_items_df, products_df, pincodes_df, support_logs_df, holidays_df = load_all_datasets()

@st.cache_resource
def get_swarm():
    return SupportGenSwarm()

swarm = get_swarm()

# Header Display
st.markdown("""
<div class="brand-banner">
    <div class="brand-logo-badge">⚡ ZENTROMART</div>
    <span class="brand-title">SupportGen-AI Enterprise Hub</span>
</div>
""", unsafe_allow_html=True)

# Sidebar Control Panel
st.sidebar.markdown("### ⚙️ Control Panel")
st.sidebar.markdown("---")

selected_oid = None
current_order = {}
current_customer = {}
current_items = pd.DataFrame()
customer_logs = pd.DataFrame()

if not orders_df.empty:
    merged_context = orders_df.merge(customers_df, on='customer_id', how='left')
    
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
        
        if not support_logs_df.empty:
            if 'customer_id' in support_logs_df.columns:
                customer_logs = support_logs_df[support_logs_df['customer_id'].astype(str) == str(current_customer.get('customer_id', ''))]
            elif 'order_id' in support_logs_df.columns:
                customer_logs = support_logs_df[support_logs_df['order_id'].astype(str) == str(selected_oid)]
        
        pincode_val = str(current_order.get('delivery_pincode', ''))
        pin_info = pincodes_df[pincodes_df['pincode'].astype(str) == pincode_val]
        is_serviceable = pin_info['serviceable'].values[0] if not pin_info.empty else True
        cod_avail = pin_info['cod_available'].values[0] if not pin_info.empty else True
        
        st.sidebar.markdown("#### 👤 Comprehensive Customer Profile")
        st.sidebar.info(f"""
        * **Customer ID:** `{current_customer.get('customer_id', 'N/A')}`
        * **Name:** {current_customer.get('name', 'N/A')}
        * **Email:** {current_customer.get('email', 'N/A')}
        * **Phone:** {current_customer.get('phone', 'N/A')}
        * **Member Since:** {current_customer.get('created_at', 'N/A')}
        * **Location:** {pin_info['city'].values[0] if not pin_info.empty else 'N/A'}, {pin_info['state'].values[0] if not pin_info.empty else 'N/A'} (Pin: {pincode_val})
        * **Serviceable Area:** {'✅ Yes' if is_serviceable else '❌ No'} 
        * **COD Available in Pincode:** {'✅ Yes' if cod_avail else '❌ No'}
        """)
    else:
        st.sidebar.warning("No Order Selected. Select an order above.")

# Highly dynamic query generation based on exact order & support logs
default_query = ""
if not customer_logs.empty:
    for _, log_row in customer_logs.iterrows():
        for col in ['query', 'issue', 'message', 'description', 'ticket_query']:
            if col in customer_logs.columns and pd.notna(log_row[col]):
                val = str(log_row[col]).strip()
                if val and val.lower() not in ['nan', 'no details', 'none', '']:
                    default_query = val
                    break
        if default_query:
            break

if not default_query:
    status_val = str(current_order.get('status', '')).lower()
    pay_method = str(current_order.get('payment_method', 'online')).upper()
    total_amt = current_order.get('total_inr', 0)
    
    if status_val == 'delivered':
        default_query = f"Customer received order #{selected_oid} (Paid via {pay_method}, ₹{total_amt}) and is requesting information on replacement or return window eligibility."
    elif status_val == 'cancelled':
        default_query = f"Order #{selected_oid} was cancelled. Customer is asking for the exact cancellation reason and refund status for ₹{total_amt}."
    elif status_val == 'shipped':
        default_query = f"Customer is inquiring about live tracking and courier dispatch status for shipped order #{selected_oid}."
    else:
        default_query = f"Customer support inquiry regarding order #{selected_oid} fulfillment and SLA status."

# Main Layout: Two Columns
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("""
    <div class="clean-card">
        <span class="card-header-label">💬 Customer Support Dispatch</span>
    """, unsafe_allow_html=True)
    
    query = st.text_area(
        "Enter Support Query / Issue:",
        value=default_query,
        height=110
    )
    run_swarm = st.button("🚀 Run Autonomous Swarm Resolution")
    
    st.markdown("---")
    st.markdown("##### 📜 Past Support Tickets & Interaction Logs")
    if selected_oid and not customer_logs.empty:
        for idx, log in customer_logs.iterrows():
            log_id = log.get('ticket_id', log.get('support_id', f'TICKET-{idx+1}'))
            log_query = log.get('query', log.get('issue', log.get('message', log.get('description', 'Support query recorded'))))
            log_status = log.get('status', 'Resolved')
            st.markdown(f"- **{log_id}** [{log_status}]: _{log_query}_")
    elif selected_oid:
        st.caption("No prior support logs found for this customer ID.")
    else:
        st.caption("Select an order from sidebar to view customer support logs.")
        
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
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

# Output Section for Autonomous Swarm Resolution with PDF Download Button
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
        formatted_response = clean_and_format_policy(raw_response)
        
        st.success("Resolution Generated Successfully!")
        st.markdown(f"""
        <div class="post-card">
            <div class="card-title-post">📌 Final Agent Swarm Resolution & Policy Attribution</div>
            <div class="policy-content-box">
                {formatted_response.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Generation and Download Button
        if selected_oid:
            pdf_data = generate_support_pdf(
                order_id=selected_oid,
                customer_name=current_customer.get('name', 'N/A'),
                customer_email=current_customer.get('email', 'N/A'),
                query_text=query,
                resolution_text=formatted_response
            )
            
            st.markdown("---")
            st.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name=f"SupportGen_Report_{selected_oid}.pdf",
                mime="application/pdf"
            )
