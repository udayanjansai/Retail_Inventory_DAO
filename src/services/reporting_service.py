from typing import List, Dict
from src.dao.product_dao import ProductDAO
from src.dao.order_dao import OrderDAO
from src.dao.customer_dao import CustomerDAO
from datetime import datetime, timedelta

class ReportingService:
    def __init__(self, product_dao: ProductDAO, order_dao: OrderDAO, customer_dao: CustomerDAO):
        self.product_dao = product_dao
        self.order_dao = order_dao
        self.customer_dao = customer_dao

    def top_selling_products(self, limit: int = 5) -> List[Dict]:
        all_orders = self.order_dao.list_all_orders()  # You may need a DAO method for all orders
        product_count = {}
        for order in all_orders:
            items = self.order_dao.get_order_items(order["order_id"])
            for item in items:
                pid = item["prod_id"]
                product_count[pid] = product_count.get(pid, 0) + item["quantity"]
        # Sort by quantity
        top_products = sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"prod_id": pid, "total_qty": qty} for pid, qty in top_products]

    def total_revenue_last_month(self) -> float:
        last_month = datetime.now() - timedelta(days=30)
        all_orders = self.order_dao.list_orders_after(last_month)
        return sum(order["total_amount"] or 0 for order in all_orders)

    def total_orders_by_customer(self) -> List[Dict]:
        customers = self.customer_dao.list_customers()
        result = []
        for c in customers:
            orders = self.order_dao.list_orders_by_customer(c["cust_id"])
            result.append({"cust_id": c["cust_id"], "name": c["name"], "order_count": len(orders)})
        return result

    def frequent_customers(self, min_orders: int = 2) -> List[Dict]:
        all_customers = self.customer_dao.list_customers()
        result = []
        for c in all_customers:
            orders = self.order_dao.list_orders_by_customer(c["cust_id"])
            if len(orders) > min_orders:
                result.append({"cust_id": c["cust_id"], "name": c["name"], "order_count": len(orders)})
        return result
