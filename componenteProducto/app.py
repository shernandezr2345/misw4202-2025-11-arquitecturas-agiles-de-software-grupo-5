from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from models.products import Product
from controllers.product_ctr import product_ctr
from db import init_db

app = Flask(__name__)
CORS(app)

init_db(app)

SWAGGER_URL = "/swagger"  
API_URL = "/static/swagger.json" 

swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "API de Productos"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

app.register_blueprint(product_ctr, url_prefix='/api')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)