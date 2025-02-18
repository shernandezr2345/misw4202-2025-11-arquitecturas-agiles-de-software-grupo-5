from flask import Blueprint, request, jsonify
from views.product_vm import ProductView
product_ctr = Blueprint('product_ctr', __name__)

@product_ctr.route('/products', methods=['GET'])
def get_products():
    response, status = ProductView.get_all_products()
    return jsonify(response), status