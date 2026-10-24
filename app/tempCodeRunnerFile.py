"""
[SupportGen-AI] Main Application Runner
100% Original, Self-Authored Code for IIT Guwahati GenAI Capstone.
Brings together the Multi-Agent Swarm Pipeline and Support Execution Tools.
"""

import sys
from pathlib import Path

# Add src and tools to system path for clean execution
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "tools"))

from agent_swarm import SupportGenSwarm
from tools import SupportTools

def main():
    print("========================================================")
    print("🚀 Initializing [SupportGen-AI] Customer Support System")
    print("    IIT Guwahati GenAI Capstone Project (100% Original)")
    print("========================================================")

    # Initialize the Multi-Agent Swarm
    swarm = SupportGenSwarm()

    # Simulate an incoming customer support ticket
    customer_ticket = {
        "customer_id": "CUST-101",
        "name": "Priyanshu",
        "email": "priyanshu12tt@gmail.com",
        "order_id": "ORD-901",
        "query": "What is the return policy for damaged items and is my order eligible?"
    }

    print(f"\n📩 Incoming Ticket from {customer_ticket['name']} ({customer_ticket['email']}):")
    print(f"Query: \"{customer_ticket['query']}\"")

    # Step 1: Lookup order details using tools
    order_info = SupportTools.lookup_order(customer_ticket['order_id'])
    print(f"\n📦 Tool Execution [Order Lookup]: {order_info}")

    # Step 2: Process through Multi-Agent Swarm
    response = swarm.process_support_ticket(customer_ticket, customer_ticket['query'])

    # Step 3: Combine with tool output for final resolution
    print("\n================ FINAL SUPPORT RESOLUTION ================")
    print(response)
    print(f"📋 Order Status Context: Item '{order_info['item']}' delivered on {order_info['date']} (Status: {order_info['status']})")
    print("==========================================================")
    print("✅ SupportGen-AI Ticket Resolution Complete Successfully!")

if __name__ == "__main__":
    main()