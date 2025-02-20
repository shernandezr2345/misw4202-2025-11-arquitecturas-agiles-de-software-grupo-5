from models.products import Product

class ProductRepository:

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return [{"id": product.id, "name": product.name} for product in products]

    @staticmethod
    def get_product_by_id(product_id):
        product = Product.query.get(product_id)
        if product:
            return {"id": product.id, "name": product.name}
        return None