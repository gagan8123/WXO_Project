import xmlrpc.client


url = "https://catnipit2.odoo.com"
db = "catnipit2"
username = "kushalcatnipit@gmail.com"
password = "Kushal@123456"


# ODOO_URL = 'https://catnipit2.odoo.com'
# ODOO_DB = 'catnipit2'
# ODOO_USERNAME = 'kushalcatnipit@gmail.com'
# ODOO_PASSWORD = 'Kushal@123456'


# def get_odoo_connection():
#     """Establish connection to Odoo"""
#     common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
#     uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
#     models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
#     return uid, models


def validate_po(po_number,invoice_items):
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        po_data = models.execute_kw(
            db,
            uid,
            password,
            "purchase.order",
            "search_read",
            [[["name", "=", po_number]]],
            {"fields": ["id", "name", "order_line"], "limit": 1},
        )
        if not po_data:
            return "no po details found"
        po_id = po_data[0]['id']
        po_lines = models.execute_kw(
            db, uid, password,
            'purchase.order.line', 'search_read',
            [[['order_id', '=', po_id]]],
            {'fields': ['product_id', 'name', 'product_qty', 'price_unit']}
        )
        validation_results = []

        
        for inv_item in invoice_items:
            matched = False
            for po_line in po_lines:
                # Check if description matches
                desc_match = inv_item['description'].lower() in po_line['name'].lower() or \
                            po_line['name'].lower() in inv_item['description'].lower()
                
                # Check if rate matches (with small tolerance for floating point)
                rate_match = abs(float(inv_item['rate']) - float(po_line['price_unit'])) < 0.01
                
                # HSN code validation (basic check)
                hsn_match = True  # Assuming HSN is matched if description and rate match
                
                if desc_match and rate_match and hsn_match:
                    matched = True
                    validation_results.append({
                        'item': inv_item['description'],
                        'status': 'matched',
                        'po_line': po_line['name'],
                        'hsn_code': inv_item.get('hsn_code', 'N/A'),
                        'rate_invoice': inv_item['rate'],
                        'rate_po': po_line['price_unit'],
                        'rate_match': True
                    })
                    break
            
        if not matched:
   
            return validation_results.append({
                'item': inv_item['description'],
                'status': 'unmatched',
                'hsn_code': inv_item.get('hsn_code', 'N/A'),
                'rate_invoice': inv_item['rate'],
                'reason': 'No matching PO line found with same description and rate'
            }) 
        return {"status": validation_results  }
    except Exception as e:
        print(e)
        return {"error": f"There was a error in matching the PO Details ({e})"}
    


def get_product_id(product_name):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    product_info = models.execute_kw(
        db,
        uid,
        password,
        "product.product",
        "search_read",
        [[["name", "ilike", product_name]]],
        {
            "fields": [
                "id",
                "name",
                "list_price",
                "standard_price",
                "type",
                "default_code",
            ],
            "limit": 1,
        },
    )

    # Print product details
    if product_info:
        product = product_info[0]
        return product["id"]
    else:
        return None


def create_new_product(
    product_name, standard_price, list_price, mesument_unit, product_type
):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    product_id = models.execute_kw(
        db,
        uid,
        password,
        "product.product",
        "create",
        [
            {
                "name": f"{product_name}",
                "type": product_type,  # 'consu' for consumable, 'product' for stockable, 'service' for services
                "list_price": list_price,  # Sales price
                "standard_price": standard_price,  # Cost
                # 'default_code': 'CONSULT-001',       # Internal reference
                "sale_ok": True,  # Allow sale
                "purchase_ok": False,  # Not purchasable
                "uom_id": mesument_unit,  # Unit of Measure (e.g., Units)
            }
        ],
    )

    return product_id


def get_customers_from_odoo(limit=None):
    try:
        # Connect to common endpoint
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")

        # Authenticate
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise Exception("Authentication failed")

        # Connect to object endpoint
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        # Search for customers (partners with is_company=True or customer_rank > 0)
        domain = ["|", ("is_company", "=", True), ("customer_rank", ">", 0)]

        # Get customer IDs
        customer_ids = models.execute_kw(
            db,
            uid,
            password,
            "res.partner",
            "search",
            [domain],
            {"limit": limit} if limit else {},
        )

        # Read customer data
        customers = models.execute_kw(
            db,
            uid,
            password,
            "res.partner",
            "read",
            [customer_ids],
            {"fields": ["id", "name"]},
        )

        return customers
    except Exception as e:
        print(f"Error connecting to Odoo: {e}")
        return []


def create_invoice(
    invoice_date: str,
    invoice_number: str,
    invoice_items: list[str],
    items_qty: list[int],
    customer_id: int,
) -> str:
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    line_items = []
    for i in range(len(invoice_items)):
        line_items.append(
            (
                0,
                0,
                {
                    # 'name': invoice_items[i],
                    "product_id": invoice_items[i],  # replace with real product ID
                    "quantity": items_qty[i],
                    # 'price_unit': price_per_qty[i],
                },
            )
        )
    print(line_items)
    invoice_id = models.execute_kw(
        db,
        uid,
        password,
        "account.move",
        "create",
        [
            {
                "move_type": "out_invoice",  # Customer invoice
                "partner_id": customer_id,  # replace with real customer ID
                "invoice_date": invoice_date,
                "name": invoice_number,
                "invoice_line_ids": line_items,
            }
        ],
    )
    # print()
    return f"Invoice id = {invoice_id}"


def create_customer_in_odoo(customer_data):
    """
    Create a new customer in Odoo

    Args:
        customer_data (dict): Customer information (name, email, phone, etc.)

    Returns:
        int: Created customer ID or None if failed
    """
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})

        if not uid:
            raise Exception("Authentication failed")

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        # Set default customer fields
        customer_data.update(
            {
                "is_company": customer_data.get("is_company", False),
                "customer_rank": 1,
                "supplier_rank": 0,
            }
        )

        customer_id = models.execute_kw(
            db, uid, password, "res.partner", "create", [customer_data]
        )

        return customer_id

    except Exception as e:
        print(f"Error creating customer: {e}")
        return None


# create_invoice(
#     invoice_date="2024-08-28",
#     invoice_number="7025019198",
#     invoice_items=[
#         "S.G. IRON MACHINED CASTING OF MAIN BEARING CAP ( FWE) F6.18° 027 00"
#     ],
#     items_qty=[30],
#     price_per_qty=[487.21])
# print(get_customers_from_odoo())

# new_customer = {
#     'name': 'John Doe',
#     'email': 'john@example.com',
#     'phone': '+1234567890',
#     'street': '123 Main St',
#     'city': 'New York',
#     'country_id': 233  # US country ID
# }

# customer_id = create_customer_in_odoo(
#      new_customer
# )
