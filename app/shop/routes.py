# from flask import Blueprint, request
# from ..models import Product, Cart, User
# from ..apiauthhelper import basic_auth_required, token_auth_required, basic_auth, token_auth

# shop = Blueprint('shop', __name__)


# @shop.route('/api/products')
# def getProducts():
#     products = Product.query.all()
    
#     return {
#         'status': 'ok',
#         'totalResults': len(products),
#         'products': [p.to_dict() for p in products]
#     }


# @shop.post('/api/cart/add')
# @token_auth.login_required
# def addToCartAPI():
#     data = request.json
#     user = token_auth.current_user()

#     product_id = data['productId']
#     product = Product.query.get(product_id)

#     c = Cart(user.id, product_id)
#     c.saveToDB()
    
#     return {
#         'status': 'ok',
#         'message': f'Succesfully added "{product.product_name}" to your cart!'
#     }

# @shop.get('/api/cart/get')
# @token_auth.login_required
# def getCartAPI():
#     user = token_auth.current_user()
#     cart = [Product.query.get(c.product_id).to_dict() for c in user.cart]
    
#     return {
#         'status': 'ok',
#         'cart': cart
#     }

# @shop.post('/api/cart/remove')
# @token_auth.login_required
# def removeFromCartAPI():
#     data = request.json
#     user = token_auth.current_user()

#     product_id = data['productId']
    

#     c = Cart.query.filter_by(user_id=user.id).filter_by(product_id=product_id).first()
#     print(c)
#     c.deleteFromDB()
    
#     return {
#         'status': 'ok',
#         'message': 'Succesfully removed item from cart!'
#     }