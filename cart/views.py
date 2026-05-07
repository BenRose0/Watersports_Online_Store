from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from Watersports_Online_Store.posts.models import Product
import stripe 
from django.conf import settings

def cart_detail(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
        })

    return render(request, 'cart/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart:cart_detail')

def increase_quantity(request, product_id):
    cart = request.session.get('cart',  {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')
    
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')

def create_checkout_session(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart:cart_detail')
    
    stripe.api_key = settings.STRIPE_SECRET_KEY

    line_items = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),
            },
            'quantity': quantity,
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/cart/success/'),
        cancel_url=request.build_absolute_uri('/cart/cancel/'),
    )

    return redirect(checkout_session.url, code=303)

def checkout_success(request):
    request.session['cart'] = {}
    request.session.modified = True
    return render(request, 'cart/success.html')

def checkout_cancel(request):
    return render(request, 'cart/cancel.html')