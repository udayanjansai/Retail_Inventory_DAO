from typing import List, Dict, Optional
from src.config import get_supabase

class OrderDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_order(self, customer_id: int, items: List[Dict], total_amount: float) -> Dict:
        payload = {
            "customer_id": customer_id,
            "total_amount": total_amount,
            "status": "PLACED"
        }
        resp = self.sb.table("orders").insert(payload).execute()
        order_id = resp.data[0]["order_id"]

        # Insert order_items with price
        for item in items:
            product = self.sb.table("products").select("*").eq("prod_id", item["prod_id"]).limit(1).execute()
            if not product.data:
                raise ValueError(f"Product {item['prod_id']} not found")
            price = product.data[0]["price"]

            self.sb.table("order_items").insert({
                "order_id": order_id,
                "prod_id": item["prod_id"],
                "quantity": item["quantity"],
                "price": price
            }).execute()

        return self.get_order_by_id(order_id)

    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        resp = self.sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_order_items(self, order_id: int) -> List[Dict]:
        resp = self.sb.table("order_items").select("*").eq("order_id", order_id).execute()
        return resp.data or []

    def list_orders_by_customer(self, customer_id: int) -> List[Dict]:
        resp = self.sb.table("orders").select("*").eq("customer_id", customer_id).execute()
        return resp.data or []

    def update_order(self, order_id: int, fields: Dict) -> Dict:
        self.sb.table("orders").update(fields).eq("order_id", order_id).execute()
        return self.get_order_by_id(order_id)

    # --- NEW METHOD ---
    def get_order_details(self, order_id: int, customer_dao=None) -> Dict:
        """
        Fetch full order details: order info, items, and optionally customer info.
        customer_dao: an instance of CustomerDAO to fetch customer details.
        """
        order = self.get_order_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        items = self.get_order_items(order_id)
        customer = None
        if customer_dao:
            customer = customer_dao.get_customer_by_id(order["customer_id"])

        return {
            "order": order,
            "items": items,
            "customer": customer
        }
    def list_all_orders(self) -> List[Dict]:
        """Fetch all orders from the orders table."""
        resp = self.sb.table("orders").select("*").execute()
        return resp.data or []
    def list_orders_after(self, date_str: str) -> List[Dict]:
        """
        Fetch all orders placed after the given timestamp.
        date_str should be an ISO 8601 string (e.g., '2025-08-01T00:00:00Z')
        """
        resp = (
            self.sb.table("orders")
            .select("*")
            .gte("order_date", date_str)
            .execute()
        )
        return resp.data or []