from flask import Flask, request, jsonify
from flask_cors import CORS
from odoo_fun import *
import pandas as pd


app = Flask(__name__)

CORS(app=app)


@app.route("/hello", methods=["GET"])
def say_hello():
    return jsonify({"text": "hello user what is up , what i have to do"}), 200


@app.route("/validate_po",methods=['POST'])
def verify_po():
    data = request.get_json()

    po_number = data.get('po_number')
    invoice_items = data.get('items', [])
    if not po_number:
        return jsonify({
            'status': 'error',
            'message': 'PO number is required for validation'
        }), 200
    
    if not invoice_items:
        return jsonify({
            'status': 'error',
            'message': 'Invoice items are required for validation'
        }), 200
    return jsonify(validate_po(po_number,invoice_items)),200


@app.route("/get_customer_id", methods=["GET"])
def get_customer_id():
    customer_name = request.args.get("coustomer_name")
    print("get customer")
    print(request.args)
    print(customer_name)
    data = get_customers_from_odoo()
    print(data)
    if data and customer_name:
        data = pd.DataFrame(data)
        ids = ((data[data["name"].str.lower() == customer_name.lower()])["id"]).tolist()
        print(ids)
        if not ids:
            return jsonify(
                {
                    "content": "Id found , please create a new customer or proper input is given "
                }
            ), 200
        print("get customer")
        print(ids)
        return jsonify({"id": (ids)[0]}), 200
    else:
        return jsonify(
            {
                "content": "Id found , please create a new customer or proper input is given "
            }
        ), 200


@app.route("/create_customer", methods=["POST"])
def create_custmer():
    data = request.get_json()
    print("create customer")
    print(data)
    new_customer = {
        "name": data.get("name"),
        "email": data.get("email") or "",
        "phone": data.get("phone") or "",
        "street": data.get("street") or "",
        "city": data.get("city") or "",
        "country_id": data.get("country_code") or "",  # US country ID
    }
    id = create_customer_in_odoo(new_customer)
    print("response")
    print(id)
    if id:
        return jsonify({"id": f"{id}"}), 200
    else:
        return jsonify({"text": "Not able to create suctomer"}), 500


@app.route("/get_product_ids", methods=["POST"])
def get_product_ids():
    data = request.get_json().get("product_names")
    response = []
    for product in data:
        response.append(
            {
                "product and product ids": {
                    product: get_product_id(product) or "no product id found"
                }
            }
        )
    print("product ids")
    print(data)
    print(response)
    return jsonify({"data": response}), 200


@app.route("/create_new_product", methods=["POST"])
def create_new_products():
    data = request.get_json().get("product")
    print("create new product")
    print(data)

    v = ["name", "standard_price", "list_price", "measurement_unit", "product_type"]
    response = []
    for d in data:
        response.append(
            {
                d["name"]: create_new_product(
                    d[v[0]], d[v[1]], d[v[2]], d[v[3]], d[v[4]]
                )
                or "not able to create product"
            }
        )
    print("resonse")
    print(response)
    return jsonify({"response": response}), 200


@app.route("/create_invoice", methods=["POST"])
def create_new_invoice():
    data = request.get_json()
    print(data)
    # {'custome_id': 36, 'invoice_date': '2025-09-21', 'invoice_items': [1], 'items_qty': [2], 'price_per_qty': [100]}
    try:
        number = create_invoice( #invoice_date
            data["invoice_date"],
            data["invoice_number"],
            data["invoice_items"],
            data["items_qty"],
            data["customer_id"]
        )
        return jsonify({"invoice_number": number}), 200
    except Exception as e:
        return jsonify({"error": e}), 200


if __name__ == "__main__":
    app.run(debug=True)
