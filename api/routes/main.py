import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from api.models import db, Product, Order, OrderItem, Payment
from api.utils import send_email, upload_to_supabase, get_supabase_public_url

main = Blueprint('main', __name__)

@main.route('/')
def index():
    featured_products = Product.query.limit(4).all()
    return render_template('index.html', products=featured_products)

@main.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

@main.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/cart')
def cart():
    # Cart logic is mostly handled in JS with localStorage
    return render_template('cart.html')

@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # 1. Get cart items from request (assuming JSON or hidden inputs)
        # Using a simplified approach: we'll get JSON from the frontend
        data = request.form
        customer_name = data.get('name')
        customer_email = data.get('email')
        customer_address = data.get('address')
        customer_phone = data.get('phone') or 'Not provided'
        
        # Products and quantities should be sent as lists in the form
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        if not product_ids:
            flash('Your cart is empty', 'error')
            return redirect(url_for('main.cart'))
            
        screenshot = request.files.get('screenshot')
        if not screenshot or screenshot.filename == '':
            flash('Payment screenshot is required', 'error')
            return redirect(url_for('main.checkout'))

        # Secure filename and save
        filename = secure_filename(screenshot.filename)
        # Add timestamp to avoid overwriting
        import time
        filename = f"{int(time.time())}_{filename}"
        
        # Supabase upload
        supabase_filename = upload_to_supabase(screenshot, filename, bucket_name="payments", prefix="pay_")
        if supabase_filename:
            pub_url = get_supabase_public_url(supabase_filename, bucket_name="payments")
            filename = pub_url if isinstance(pub_url, str) else supabase_filename
        else:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            screenshot.seek(0)
            screenshot.save(filepath)

        # Create Order
        total_amount = 0
        order = Order(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address,
            customer_phone=customer_phone,
            status='PAYMENT_SUBMITTED',
            total_amount=0 # Will update after calculating items
        )
        db.session.add(order)
        db.session.flush() # Get order.id
        
        items_text = ""
        for pid, qty in zip(product_ids, quantities):
            product = Product.query.get(int(pid))
            if product:
                q = int(qty)
                price = product.price
                total_amount += price * q
                order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=q, price_at_purchase=price)
                db.session.add(order_item)
                items_text += f"- {product.name} x {q} (₹{price*q})\n"
                
        order.total_amount = total_amount
        
        # Create Payment
        payment = Payment(order_id=order.id, screenshot_url=filename)
        db.session.add(payment)
        db.session.commit()

        # Send Email to Admin
        subject = f"New Order Received – Varnam Aesthetics (#{order.id})"
        body = f"""
New order received!

Order ID: {order.id}
Customer Name: {customer_name}
Customer Email: {customer_email}
Shipping Address: {customer_address}
Phone: {customer_phone}
Total Price: ₹{total_amount}

Products Ordered:
{items_text}

Payment Screenshot saved as {filename} in uploads folder.
"""
        send_email(subject, "ojas.v.kulkarni@gmail.com", body)

        return render_template('checkout_success.html', order_id=order.id)

    return render_template('checkout.html')

@main.route('/custom-order', methods=['GET', 'POST'])
def custom_order():
    if request.method == 'POST':
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
            
            # Supabase upload
            supabase_filename = upload_to_supabase(reference_image, filename, bucket_name="products", prefix="req_")
            if supabase_filename:
                pub_url = get_supabase_public_url(supabase_filename, bucket_name="products")
                filename = pub_url if isinstance(pub_url, str) else supabase_filename
            else:
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                reference_image.seek(0)
                reference_image.save(filepath)

        # Email admin
        subject = "New Custom Order Request - Varnam Aesthetics"
        body = f"""
New custom order request:

Name: {name}
Email: {email}
Phone: {phone}
Description: {description}
Reference Image: {filename}
"""
        send_email(subject, "ojas.v.kulkarni@gmail.com", body)
        
        flash('Your custom order request has been submitted!', 'success')
        return redirect(url_for('main.custom_order'))
        
    return render_template('custom_order.html')
