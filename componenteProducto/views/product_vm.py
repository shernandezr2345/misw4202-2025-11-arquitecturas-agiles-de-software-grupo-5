from repositories.product_repo import ProductRepository
from flask import jsonify

class ProductView:

    @staticmethod
    def get_all_products():
        products = ProductRepository.get_all_products()
        if not products:
            return {"message": "No products found"}, 404
        
        return products, 200
    
    @staticmethod
    def get_product_by_id(product_id):
        product = ProductRepository.get_product_by_id(product_id)
        
        if not product:
            return {"message": "Product not found"}, 404
        
        return product, 200