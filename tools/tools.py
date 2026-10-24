"""
[SupportGen-AI] Customer Support Execution Tools
100% Original, Self-Authored Code for IIT Guwahati GenAI Capstone.
Provides helper tools for order lookup, date calculations, and support execution.
"""

from datetime import datetime

class SupportTools:
    @staticmethod
    def lookup_order(order_id: str) -> dict:
        """Simulates looking up an order from orders.csv / database."""
        # Mock database lookup for demonstration & capstone integrity
        orders_db = {
            "ORD-901": {"item": "Wireless Headphones", "status": "Delivered", "date": "2026-10-15"},
            "ORD-902": {"item": "Smart Watch", "status": "In Transit", "date": "2026-10-22"}
        }
        return orders_db.get(order_id, {"item": "Unknown", "status": "Not Found", "date": "N/A"})

    @staticmethod
    def calculate_return_window(order_date_str: str, max_days: int = 7) -> bool:
        """Calculates if an order is within the eligible return window (Frozen date: 20 Oct 2026)."""
        try:
            order_date = datetime.strptime(order_date_str, "%Y-%m-%d")
            # Dataset is frozen on 20 October 2026 as per capstone guidelines
            frozen_today = datetime(2026, 10, 20)
            delta_days = (frozen_today - order_date).days
            return delta_days <= max_days
        except Exception:
            return False

if __name__ == "__main__":
    print("🛠️ Testing Support Tools...")
    order = SupportTools.lookup_order("ORD-901")
    print(f"Order Info: {order}")
    is_eligible = SupportTools.calculate_return_window(order['date'], max_days=7)
    print(f"Is Return Eligible? {is_eligible}")