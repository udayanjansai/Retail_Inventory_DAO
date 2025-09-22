# import argparse
# import json
# from src.services import product_service, order_service
# from src.dao import product_dao, customer_dao
 
# def cmd_product_add(args):
#     try:
#         p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
#         print("Created product:")
#         print(json.dumps(p, indent=2, default=str))
#     except Exception as e:
#         print("Error:", e)
 
# def cmd_product_list(args):
#     ps = product_dao.list_products(limit=100)
#     print(json.dumps(ps, indent=2, default=str))
 
# def cmd_customer_add(args):
#     try:
#         c = customer_dao.create_customer(args.name, args.email, args.phone, args.city)
#         print("Created customer:")
#         print(json.dumps(c, indent=2, default=str))
#     except Exception as e:
#         print("Error:", e)
 
# def cmd_order_create(args):
#     # items provided as prod_id:qty strings
#     items = []
#     for item in args.item:
#         try:
#             pid, qty = item.split(":")
#             items.append({"prod_id": int(pid), "quantity": int(qty)})
#         except Exception:
#             print("Invalid item format:", item)
#             return
#     try:
#         ord = order_service.create_order(args.customer, items)
#         print("Order created:")
#         print(json.dumps(ord, indent=2, default=str))
#     except Exception as e:
#         print("Error:", e)
 
# def cmd_order_show(args):
#     try:
#         o = order_service.get_order_details(args.order)
#         print(json.dumps(o, indent=2, default=str))
#     except Exception as e:
#         print("Error:", e)
 
# def cmd_order_cancel(args):
#     try:
#         o = order_service.cancel_order(args.order)
#         print("Order cancelled (updated):")
#         print(json.dumps(o, indent=2, default=str))
#     except Exception as e:
#         print("Error:", e)
 
# def build_parser():
#     parser = argparse.ArgumentParser(prog="retail-cli")
#     sub = parser.add_subparsers(dest="cmd")
 
#     # product add/list
#     p_prod = sub.add_parser("product", help="product commands")
#     pprod_sub = p_prod.add_subparsers(dest="action")
#     addp = pprod_sub.add_parser("add")
#     addp.add_argument("--name", required=True)
#     addp.add_argument("--sku", required=True)
#     addp.add_argument("--price", type=float, required=True)
#     addp.add_argument("--stock", type=int, default=0)
#     addp.add_argument("--category", default=None)
#     addp.set_defaults(func=cmd_product_add)
 
#     listp = pprod_sub.add_parser("list")
#     listp.set_defaults(func=cmd_product_list)
 
#     # customer add
#     pcust = sub.add_parser("customer")
#     pcust_sub = pcust.add_subparsers(dest="action")
#     addc = pcust_sub.add_parser("add")
#     addc.add_argument("--name", required=True)
#     addc.add_argument("--email", required=True)
#     addc.add_argument("--phone", required=True)
#     addc.add_argument("--city", default=None)
#     addc.set_defaults(func=cmd_customer_add)
 
#     # order
#     porder = sub.add_parser("order")
#     porder_sub = porder.add_subparsers(dest="action")
 
#     createo = porder_sub.add_parser("create")
#     createo.add_argument("--customer", type=int, required=True)
#     createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
#     createo.set_defaults(func=cmd_order_create)
 
#     showo = porder_sub.add_parser("show")
#     showo.add_argument("--order", type=int, required=True)
#     showo.set_defaults(func=cmd_order_show)
 
#     cano = porder_sub.add_parser("cancel")
#     cano.add_argument("--order", type=int, required=True)
#     cano.set_defaults(func=cmd_order_cancel)
 
#     return parser
 
# def main():
#     parser = build_parser()
#     args = parser.parse_args()
#     if not hasattr(args, "func"):
#         parser.print_help()
#         return
#     args.func(args)
 
# if __name__ == "__main__":
#     main()
import argparse
import json
from src.services.product_service import ProductService, ProductError
from src.services.customer_services import CustomerService,CustomerError
from src.dao.product_dao import ProductDAO
from src.dao.customer_dao import *
from src.services import order_service
from src.services.order_service import OrderService, OrderError
from src.dao import order_dao
from src.services.payment_service import PaymentService, PaymentError
from src.services.reporting_service import ReportingService
from src.dao.payment_dao import PaymentDAO

class RetailCLI:
    
    def __init__(self):
        self.product_dao = ProductDAO()
        self.customer_dao = CustomerDAO()
        self.order_dao = order_dao.OrderDAO()  # Ensure proper import
        self.payment_dao = PaymentDAO()
        self.product_service = ProductService(self.product_dao)
        self.customer_service = CustomerService()
        self.order_service = OrderService(
            self.order_dao,
            self.product_dao,
            self.customer_dao,
            self.payment_dao
        )
        self.payment_service = PaymentService(self.payment_dao, self.order_service)
        self.reporting_service = ReportingService(self.product_dao, self.order_dao, self.customer_dao)

        self.parser = self.build_parser()

    def cmd_product_add(self, args):
        try:
            p = self.product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
            print("Created product:")
            print(json.dumps(p, indent=2, default=str))
        except ProductError as e:
            print("Validation Error:", e)
        except Exception as e:
            print("Error:", e)

    def cmd_product_list(self, args):
        ps = self.product_service.dao.list_products(limit=100)
        print(json.dumps(ps, indent=2, default=str))

    def cmd_customer_add(self, args):
        try:
            c = self.customer_service.add_customer(args.name, args.email, args.phone, args.city)
            print("Created customer:")
            print(json.dumps(c, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_create(self, args):
        items = []
        for item in args.item:
            try:
                pid, qty = item.split(":")
                items.append({"prod_id": int(pid), "quantity": int(qty)})
            except Exception:
                print("Invalid item format:", item)
                return
        try:
            ord = self.order_service.create_order(args.customer, items)
            print("Order created:")
            print(json.dumps(ord, indent=2, default=str))
        except Exception as e:
            print("Error:", e)
    def cmd_customer_update(self, args):
        try:
            c = self.customer_service.update_customer(args.id, args.phone, args.city)
            print("Updated customer:")
            print(json.dumps(c, indent=2, default=str))
        except Exception as e:
            print("Error:", e)
    def cmd_customer_delete(self, args):
        try:
            c = self.customer_service.delete_customer(args.id)
            print("Deleted customer:")
            print(json.dumps(c, indent=2, default=str))
        except Exception as e:
            print("Error:", e)
    def cmd_customer_list(self, args):
        try:
            cs = self.customer_service.list_customers()
            print(json.dumps(cs, indent=2, default=str))
        except Exception as e:
            print("Error:", e)
    def cmd_customer_search(self, args):
        try:
            cs = self.customer_service.search_customers(args.email, args.city)
            print(json.dumps(cs, indent=2, default=str))
        except Exception as e:
            print("Error:", e)
    def cmd_order_show(self, args):
        try:
            o = order_service.get_order_details(args.order)
            print(json.dumps(o, indent=2, default=str))
        except Exception as e:
            print("Error:", e)

    def cmd_order_cancel(self, args):
        try:
            o = self.order_service.cancel_order(args.order)
            print("Order cancelled (updated):")
            print(json.dumps(o, indent=2, default=str))
        except Exception as e:
            print("Error:", e)
    def cmd_payment_process(self, args):
        try:
            payment = self.payment_service.process_payment(args.order, args.method)
            print("Payment processed:")
            print(json.dumps(payment, indent=2, default=str))
        except PaymentError as e:
            print("Payment Error:", e)
        except Exception as e:
            print("Error:", e)

# Refund a payment
    def cmd_payment_refund(self, args):
        try:
            payment = self.payment_service.refund_payment(args.order)
            print("Payment refunded:")
            print(json.dumps(payment, indent=2, default=str))
        except PaymentError as e:
            print("Payment Error:", e)
        except Exception as e:
            print("Error:", e)
    # ---------------- Reporting Commands ----------------
    def cmd_report_top_products(self, args):
        top = self.reporting_service.top_selling_products()
        print("Top selling products:")
        print(json.dumps(top, indent=2, default=str))

    def cmd_report_total_revenue(self, args):
        revenue = self.reporting_service.total_revenue_last_month()
        print(f"Total revenue in last month: {revenue}")

    def cmd_report_customer_orders(self, args):
        data = self.reporting_service.total_orders_by_customer()
        print("Total orders by customer:")
        print(json.dumps(data, indent=2, default=str))

    def cmd_report_frequent_customers(self, args):
        data = self.reporting_service.frequent_customers()
        print("Frequent customers (more than 2 orders):")
        print(json.dumps(data, indent=2, default=str))
    def cmd_payment_process(self, args):
        try:
            payment_service = PaymentService(self.payment_dao, self.order_dao)
            payment = payment_service.process_payment(args.order, args.method)
            print("Payment processed:")
            print(json.dumps(payment, indent=2, default=str))
        except PaymentError as e:
            print("Payment Error:", e)
        except Exception as e:
            print("Error:", e)
    def build_parser(self):
        parser = argparse.ArgumentParser(prog="retail-cli")
        sub = parser.add_subparsers(dest="cmd")

        # product add/list
        p_prod = sub.add_parser("product", help="product commands")
        pprod_sub = p_prod.add_subparsers(dest="action")
        addp = pprod_sub.add_parser("add")
        addp.add_argument("--name", required=True)
        addp.add_argument("--sku", required=True)
        addp.add_argument("--price", type=float, required=True)
        addp.add_argument("--stock", type=int, default=0)
        addp.add_argument("--category", default=None)
        addp.set_defaults(func=self.cmd_product_add)

        listp = pprod_sub.add_parser("list")
        listp.set_defaults(func=self.cmd_product_list)

        

        # order
        porder = sub.add_parser("order")
        porder_sub = porder.add_subparsers(dest="action")

        createo = porder_sub.add_parser("create")
        createo.add_argument("--customer", type=int, required=True)
        createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
        createo.set_defaults(func=self.cmd_order_create)

        showo = porder_sub.add_parser("show")
        showo.add_argument("--order", type=int, required=True)
        showo.set_defaults(func=self.cmd_order_show)

        cano = porder_sub.add_parser("cancel")
        cano.add_argument("--order", type=int, required=True)
        cano.set_defaults(func=self.cmd_order_cancel)
        pcust = sub.add_parser("customer", help="customer commands")
        pcust_sub = pcust.add_subparsers(dest="action")

        addc = pcust_sub.add_parser("add")
        addc.add_argument("--name", required=True)
        addc.add_argument("--email", required=True)
        addc.add_argument("--phone", required=True)
        addc.add_argument("--city", default=None)
        addc.set_defaults(func=self.cmd_customer_add)

        upc = pcust_sub.add_parser("update")
        upc.add_argument("--id", type=int, required=True)
        upc.add_argument("--phone")
        upc.add_argument("--city")
        upc.set_defaults(func=self.cmd_customer_update)

        delc = pcust_sub.add_parser("delete")
        delc.add_argument("--id", type=int, required=True)
        delc.set_defaults(func=self.cmd_customer_delete)

        listc = pcust_sub.add_parser("list")
        listc.set_defaults(func=self.cmd_customer_list)

        searchc = pcust_sub.add_parser("search")
        searchc.add_argument("--email", default=None)
        searchc.add_argument("--city", default=None)
        searchc.set_defaults(func=self.cmd_customer_search)
        ppay = sub.add_parser("payment", help="payment commands")
        ppay_sub = ppay.add_subparsers(dest="action")

        # process payment
        proc = ppay_sub.add_parser("process")
        proc.add_argument("--order", type=int, required=True)
        proc.add_argument("--method", required=True, choices=["Cash","Card","UPI"])
        proc.set_defaults(func=self.cmd_payment_process)

        # refund payment
        refund = ppay_sub.add_parser("refund")
        refund.add_argument("--order", type=int, required=True)
        refund.set_defaults(func=self.cmd_payment_refund)
        # Reporting commands
        preport = sub.add_parser("report")
        preport_sub = preport.add_subparsers(dest="action")
        top_products = preport_sub.add_parser("top-products")
        top_products.set_defaults(func=self.cmd_report_top_products)
        revenue = preport_sub.add_parser("total-revenue")
        revenue.set_defaults(func=self.cmd_report_total_revenue)
        cust_orders = preport_sub.add_parser("customer-orders")
        cust_orders.set_defaults(func=self.cmd_report_customer_orders)
        frequent_cust = preport_sub.add_parser("frequent-customers")
        frequent_cust.set_defaults(func=self.cmd_report_frequent_customers)

        return parser

    def run(self):
        args = self.parser.parse_args()
        if not hasattr(args, "func"):
            self.parser.print_help()
            return
        args.func(args)


if __name__ == "__main__":
    RetailCLI().run()
