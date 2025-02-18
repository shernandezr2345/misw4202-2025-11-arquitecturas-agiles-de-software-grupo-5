from repositories.product_repo import ProductRepository

class ProductView:

    @staticmethod
    def get_all_products():
        products = ProductRepository.get_all()
        if not products:
            return {"message": "No products found"}, 404
        return [product.to_dict() for product in products], 200
