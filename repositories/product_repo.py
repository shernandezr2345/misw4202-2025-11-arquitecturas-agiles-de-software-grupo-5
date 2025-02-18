from db import get_db_connection
from models.products import Product

class ProductRepository:
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM products;")
        products = [Product(*row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return products
