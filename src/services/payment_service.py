# src/services/payment_service.py
from src.dao.payment_dao import PaymentDAO
from src.dao.order_dao import OrderDAO
from typing import Dict

class PaymentError(Exception):
    pass

class PaymentService:
    def __init__(self, payment_dao: PaymentDAO, order_dao: OrderDAO):
        self.payment_dao = payment_dao
        self.order_dao = order_dao

    def process_payment(self, order_id: int, method: str) -> Dict:
        """
        Process payment for a given order.
        Marks payment as PAID and updates order status to COMPLETED.
        """
        payment = self.payment_dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentError("Payment record not found")

        if payment["status"] != "PENDING":
            raise PaymentError(f"Payment already {payment['status']}")

        # Mark payment as PAID
        updated_payment = self.payment_dao.update_payment(payment["payment_id"], {
            "status": "PAID",
            "method": method,
            "paid_at": "now()"  # if using supabase timestamp, else Python datetime
        })

        # Update order status to COMPLETED
        updated_order = self.order_dao.update_order(order_id, {"status": "COMPLETED"})

        return {
            "order": updated_order,
            "payment": updated_payment
        }

    def refund_payment(self, order_id: int) -> Dict:
        """
        Refund payment for a cancelled order.
        Marks payment as REFUNDED.
        """
        payment = self.payment_dao.get_payment_by_order(order_id)
        if not payment:
            raise PaymentError("Payment record not found")

        if payment["status"] != "PAID":
            raise PaymentError(f"Cannot refund payment with status {payment['status']}")

        updated_payment = self.payment_dao.update_payment(payment["payment_id"], {"status": "REFUNDED"})
        return updated_payment
