# src/services/order_service.py
from typing import List, Dict
from src.dao.order_dao import OrderDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.product_dao import ProductDAO
from src.dao.payment_dao import PaymentDAO  # Add payment DAO

class OrderError(Exception):
    pass

class OrderService:
    def __init__(
        self,
        order_dao: OrderDAO,
        product_dao: ProductDAO,
        customer_dao: CustomerDAO,
        payment_dao: PaymentDAO  # Pass PaymentDAO here
    ):
        self.order_dao = order_dao
        self.product_dao = product_dao
        self.customer_dao = customer_dao
        self.payment_dao = payment_dao

    def create_order(self, customer_id: int, items: List[Dict]) -> Dict:
        # Check customer exists
        customer = self.customer_dao.get_customer_by_id(customer_id)
        if not customer:
            raise OrderError(f"Customer {customer_id} does not exist")

        total_amount = 0
        # Check stock and calculate total
        for item in items:
            product = self.product_dao.get_product_by_id(item["prod_id"])
            if not product:
                raise OrderError(f"Product {item['prod_id']} does not exist")
            if (product["stock"] or 0) < item["quantity"]:
                raise OrderError(f"Insufficient stock for product {product['name']}")
            total_amount += product["price"] * item["quantity"]

        # Deduct stock
        for item in items:
            product = self.product_dao.get_product_by_id(item["prod_id"])
            new_stock = (product["stock"] or 0) - item["quantity"]
            self.product_dao.update_product(product["prod_id"], {"stock": new_stock})

        # Insert order
        order = self.order_dao.create_order(customer_id, items, total_amount)

        # Create a pending payment record
        self.payment_dao.create_payment(order["order_id"], total_amount)

        return self.get_order_details(order["order_id"])

    def get_order_details(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError(f"Order {order_id} not found")
        items = self.order_dao.get_order_items(order_id)
        customer = self.customer_dao.get_customer_by_id(order["customer_id"])
        return {
            "order": order,
            "customer": customer,
            "items": items
        }

    def list_orders_by_customer(self, customer_id: int) -> List[Dict]:
        return self.order_dao.list_orders_by_customer(customer_id)

    def cancel_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order["status"] != "PLACED":
            raise OrderError("Only PLACED orders can be cancelled")

        # Restore stock
        items = self.order_dao.get_order_items(order_id)
        for item in items:
            product = self.product_dao.get_product_by_id(item["prod_id"])
            new_stock = (product["stock"] or 0) + item["quantity"]
            self.product_dao.update_product(product["prod_id"], {"stock": new_stock})

        # Update order status
        cancelled_order = self.order_dao.update_order(order_id, {"status": "CANCELLED"})

        # Refund payment
        self.payment_dao.refund_payment(order_id)

        return cancelled_order

    def mark_completed(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError("Order not found")
        if order["status"] != "PLACED":
            raise OrderError("Only PLACED orders can be completed")
        return self.order_dao.update_order(order_id, {"status": "COMPLETED"})
