from . import api
from ..models import Product, Cart
from ..apiauthhelper import token_auth
from flask import request, redirect
import stripe
import os

FRONT_END_URL = os.environ.get('FRONT_END_URL')

@api.get('/products')
def getProductsAPI(): 
    products = Product.query.all()
    return {
        'status':'ok',
        'results': len(products),
        'products': [p.to_dict() for p in products]
    }

@api.get('/cart')
@token_auth.login_required
def getCartAPI():
    user = token_auth.current_user()
    return {
        'status': 'ok',
        'cart': [Product.query.get(c.product_id).to_dict() for c in Cart.query.filter_by(user_id=user.id).all()]
    }
    
@api.post('/cart')
@token_auth.login_required
def addToCartAPI():
    user = token_auth.current_user()
    data = request.json

    product_id = data['product_id']
    product = Product.query.get(product_id)

    if product:

        cart_item = Cart(user.id, product.id)
        cart_item.saveToDB()

        return {
            'status': 'ok',
            'message': f'Succesfully added {product.product_name} to your cart!'
        }
    else:
        return {
            'status': 'not ok',
            'message': 'That product does not exist!'
        }
    
@api.delete('/cart/<int:product_id>')
@token_auth.login_required
def removeFromCartAPI(product_id):
    user = token_auth.current_user()
    product = Product.query.get(product_id)
    item = Cart.query.filter_by(user_id=user.id).filter_by(product_id=product_id).first()
    if item:
        item.deleteFromDB()
        return {
            'status': 'ok',
            'message': f"Successfully removed {product.product_name} from cart."
        }
    return {
            'status': 'not ok',
            'message': f"You do not have that item in your cart."
        }

stripe.api_key = os.environ.get('STRIPE_API_KEY')


@api.post('/checkout/stripe')
def checkout_homework():
    
    try:
        data = request.form         #get items in the cart
        print(data)
        line_items = []
        print(data.items())
        for name, list in data.items():
            newList = list.split(",")
            newPrice = newList[0][:(len(newList[0])-3)] + newList[0][len(newList[0])-2:len(newList[0])]
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': name,
                        'images':[newList[2]],
                        'description':newList[3],
                    },
                    
                    'unit_amount': newPrice ,
                },
                'quantity': newList[1],
            })
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url = FRONT_END_URL + '/shop?success=true',
            cancel_url=FRONT_END_URL + '/shop?canceled=true'
        )

    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)



@api.post('/checkout')
def checkout():
    try:
        data = request.form
        line_items = []
        for price, qty in data.items():
            line_items.append({
                'price': price,
                'quantity': qty
            })
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Lifetime Subscription to Shoha Fans"},
                    "unit_amount": 2000,
                    "tax_behavior": "exclusive",
                },
                'quantity':3
            }],
            mode='payment',
            success_url=FRONT_END_URL + '?success=true',
            cancel_url=FRONT_END_URL + '?canceled=true',
            customer={'email':'shohat@codingtemple.com'}
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)