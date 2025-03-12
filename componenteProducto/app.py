import db
import pandas as pd
from flask import Flask, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from models.products import Product
from controllers.product_ctr import product_ctr
from controllers.auth_ctr import auth_ctr
from db import init_db
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask_jwt_extended import JWTManager


app = Flask(__name__)
CORS(app)

init_db(app)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'

jwt = JWTManager(app)

SWAGGER_URL = "/swagger"  
API_URL = "/static/swagger.json" 

swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "API de Productos"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

app.register_blueprint(product_ctr, url_prefix='/api')
app.register_blueprint(auth_ctr, url_prefix='/auth') 

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def llenar_tabla_products():
    # Leer el archivo csv
    products_data = pd.read_csv("MOCK_DATA.csv")
    conx = db.connect()
    for row in products_data.rows:
        producto = Product(id = row['id'], name = row['name'])
        conx.session.add(producto)
        conx.session.commit()



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
    llenar_tabla_products()