import streamlit as st
import sys
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "tools"))

from agent_swarm import SupportGenSwarm
from tools import SupportTools

# Page configuration for mobile and desktop responsiveness
st.set_page_config(
    page_title="SupportGen-AI | ZentroMart",
    page_icon="⚡",
    layout="wide"
)

# Custom Colorful & Modern CSS Styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff416c 0%, #ff4b2b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 65, 108, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 65, 108, 0.6);
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("<h1 style='text-align: center; color: #1e293b;'>⚡ SupportGen-AI: ZentroMart Support</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 16px;'>IIT Guwahati GenAI Capstone | Next-Gen Multi-Agent Customer Support Swarm</p>", unsafe_allow_html=True)
st.divider()

# Initialize Swarm
@st.cache_resource
def load_swarm():
    return SupportGenSwarm()

swarm = load_swarm()

# Sidebar Layout
with st.sidebar:
    st.markdown("### 🛠️ Ticket Controls")
    customer_name = st.text_input("Customer Name", "Priyanshu")
    customer_email = st.text_input("Customer Email", "priyanshu12tt@gmail.com")
    order_id = st.text_input("Order ID", "ORD-901")
    
    st.divider()
    if st.button("🔍 Quick Order Lookup"):
        info = SupportTools.lookup_order(order_id)
        st.json(info)

# Main Dashboard Layout
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("### 💬 Ask Support Swarm")
    query = st.text_area(
        "Enter your support question:",
        "What is the return policy for damaged items and is my order eligible?",
        height=120
    )
    
    if st.button("🚀 Process Support Ticket"):
        ticket = {
            "customer_id": "CUST-101",
            "name": customer_name,
            "email": customer_email,
            "order_id": order_id,
            "query": query
        }
        
        with st.spinner("🤖 Multi-Agent Swarm is analyzing policy and database..."):
            order_info = SupportTools.lookup_order(order_id)
            response = swarm.process_support_ticket(ticket, query)
            
        st.success("✨ Resolution Generated Successfully!")
        st.markdown(f"<div class='card'><h4>📄 Final Resolution</h4><p>{response}</p></div>", unsafe_allow_html=True)

with col2:
    st.markdown("### 📦 Live Order Context")
    order_info = SupportTools.lookup_order(order_id)
    st.markdown(f"""
        <div class='card'>
            <p><b>Item:</b> {order_info.get('item', 'N/A')}</p>
            <p><b>Delivery Date:</b> {order_info.get('date', 'N/A')}</p>
            <p><b>Status:</b> <span style='color: green;'>{order_info.get('status', 'N/A')}</span></p>
            <p><b>Return Window:</b> Active (7 Days)</p>
        </div>
    """, unsafe_allow_html=True)