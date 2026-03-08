import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from api.models import db, Product, Order, OrderItem, Payment
from api.utils import upload_to_supabase, get_supabase_public_url

api = Blueprint('api', __name__)

@api.route('/products', methods=['GET'])
def get_products():
    limit = request.args.get('limit', type=int)
    query = Product.query
    if limit:
        query = query.limit(limit)
    products = query.all()
    
    products_list = []
    for p in products:
        image = p.image_url
        if image and not image.startswith('http'):
            # Fallback local path
            image = f"/static/uploads/{image}"
            
        products_list.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'stock': p.stock,
            'image_url': image
        })
    return jsonify(products_list)

@api.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    image = p.image_url
    if image and not image.startswith('http'):
        image = f"/static/uploads/{image}"
        
    return jsonify({
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price': p.price,
        'stock': p.stock,
        'image_url': image
    })

@api.route('/checkout', methods=['POST'])
def checkout():
    # Expects multipart/form-data for the image
    customer_name = request.form.get('customerName')
    customer_email = request.form.get('customerEmail')
    customer_address = request.form.get('customerAddress')
    customer_phone = request.form.get('customerPhone')
    cart_items_json = request.form.get('cart')
    
    screenshot = request.files.get('screenshot')
    if not screenshot or screenshot.filename == '':
        return jsonify({'error': 'Payment screenshot is required'}), 400
        
    try:
        cart_items = json.loads(cart_items_json)
    except Exception:
        return jsonify({'error': 'Invalid cart data'}), 400
        
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Upload screenshot
    import time
    filename = secure_filename(screenshot.filename)
    filename = f"{int(time.time())}_{filename}"
    
    supabase_filename = upload_to_supabase(screenshot, filename, bucket_name="payments", prefix="pay_")
    if supabase_filename:
        pub_url = get_supabase_public_url(supabase_filename, bucket_name="payments")
        filename = pub_url if isinstance(pub_url, str) else supabase_filename
    else:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        screenshot.seek(0)
        screenshot.save(filepath)

    # Create Order
    order = Order(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_address=customer_address,
        customer_phone=customer_phone,
        status='PAYMENT_SUBMITTED',
        total_amount=0 
    )
    db.session.add(order)
    db.session.flush() # Get order.id
    
    total_amount = 0
    for item in cart_items:
        product = Product.query.get(int(item['id']))
        if product:
            qty = int(item['quantity'])
            price = product.price
            total_amount += price * qty
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price_at_purchase=price
            )
            db.session.add(order_item)
            
    order.total_amount = total_amount
    
    payment = Payment(
        order_id=order.id,
        screenshot_url=filename
    )
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({'success': True, 'order_id': order.id, 'message': 'Order submitted successfully'})

@api.route('/custom_order', methods=['POST'])
def custom_order():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    description = request.form.get('description')
    
    reference_image = request.files.get('reference_image')
    filename = "No image uploaded"
    if reference_image and reference_image.filename != '':
        filename = secure_filename(reference_image.filename)
        import time
        filename = f"custom_req_{int(time.time())}_{filename}"
        
        supabase_filename = upload_to_supabase(reference_image, filename, bucket_name="products", prefix="req_")
        if supabase_filename:
            pub_url = get_supabase_public_url(supabase_filename, bucket_name="products")
            filename = pub_url if isinstance(pub_url, str) else supabase_filename
        else:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            reference_image.seek(0)
            reference_image.save(filepath)

    from api.utils import send_email
    subject = "New Custom Order Request - Varnam Aesthetics"
    body = f"""
New custom order request:

Name: {name}
Email: {email}
Phone: {phone}

Description:
{description}

Reference Image URL/Filename: {filename}
"""
    send_email(subject, current_app.config['MAIL_USERNAME'], body)
    
    return jsonify({'success': True, 'message': 'Custom order request sent successfully!'})
