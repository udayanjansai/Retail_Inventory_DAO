from src.dao.customer_dao import CustomerDAO
class CustomerError(Exception):
    pass
class CustomerService:
    def __init__(self):
        self.dao = CustomerDAO()

    def add_customer(self, name: str, email: str, phone: str, city: str | None = None):
        existing = self.dao.get_customer_by_email(email)
        if existing:
            raise CustomerError(f"Email already exists: {email}")
        return self.dao.create_customer(name, email, phone, city)

    def update_customer(self, cust_id: int, phone: str | None = None, city: str | None = None):
        c = self.dao.get_customer_by_id(cust_id)
        if not c:
            raise CustomerError("Customer not found")
        fields = {}
        if phone:
            fields["phone"] = phone
        if city:
            fields["city"] = city
        if not fields:
            raise CustomerError("Nothing to update")
        return self.dao.update_customer(cust_id, fields)

    def delete_customer(self, cust_id: int):
        c = self.dao.get_customer_by_id(cust_id)
        if not c:
            raise CustomerError("Customer not found")
        # Optional: check orders here
        return self.dao.delete_customer(cust_id)

    def list_customers(self):
        return self.dao.list_customers()

    def search_customers(self, email: str | None = None, city: str | None = None):
        return self.dao.search_customers(email=email, city=city)
