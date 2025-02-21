from flask import Blueprint, request, jsonify, Response
from views.product_vm import ProductView
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

product_ctr = Blueprint('product_ctr', __name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total de requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Duración de requests', ['method', 'endpoint'])

@product_ctr.route('/products', methods=['GET'])
def get_products():
    REQUEST_COUNT.labels(method='GET', endpoint='/products').inc()
    with REQUEST_LATENCY.labels(method='GET', endpoint='/products').time():
        response, status = ProductView.get_all_products()
    return jsonify(response), status

@product_ctr.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    REQUEST_COUNT.labels(method='GET', endpoint='/products/<id>').inc()
    with REQUEST_LATENCY.labels(method='GET', endpoint='/products/<id>').time():
        response, status = ProductView.get_product_by_id(id)
    return jsonify(response), status

@product_ctr.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)