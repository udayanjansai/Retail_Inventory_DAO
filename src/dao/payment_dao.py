from typing import Optional, Dict
from src.config import get_supabase

class PaymentDAO:
    def __init__(self):
        self.sb = get_supabase()

    def create_payment(self, order_id: int, amount: float):
        payload = {
            "order_id": order_id,
            "amount": amount,
            "status": "PENDING",
            "method": None,
            "paid_at": None
        }
        resp = self.sb.table("payments").insert(payload).execute()
        return resp.data[0] if resp.data else None

    def update_payment(self, payment_id: int, fields: Dict) -> Dict:
        self.sb.table("payments").update(fields).eq("payment_id", payment_id).execute()
        resp = self.sb.table("payments").select("*").eq("payment_id", payment_id).limit(1).execute()
        return resp.data[0] if resp.data else {}

    def get_payment_by_order(self, order_id: int) -> Optional[Dict]:
        resp = self.sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None
