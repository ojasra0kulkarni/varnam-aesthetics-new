import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from api.models import db, User, Product, Order, OrderItem, Payment
from api.utils import send_email, upload_to_supabase, get_supabase_public_url

admin = Blueprint('admin', __name__)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'ADMIN':
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        from app import bcrypt # Import here to avoid circular logic or use check_password_hash directly if stored with generate_password_hash
        # Actually it's better to use check_password_hash with bcrypt hash
        if user and user.role == 'ADMIN' and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
            
    return render_template('admin/login.html')

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'ADMIN':
        return redirect(url_for('main.index'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    products = Product.query.all()
    return render_template('admin/dashboard.html', orders=orders, products=products)

@admin.route('/product/add', methods=['POST'])
@login_required
def add_product():
    if current_user.role != 'ADMIN':
        return redirect(url_for('main.index'))
        
    name = request.form.get('name')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    stock = int(request.form.get('stock'))
    
    image = request.files.get('image')
    filename = None
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        import time
        filename = f"prod_{int(time.time())}_{filename}"
        
        # Try Supabase upload first
        supabase_filename = upload_to_supabase(image, filename, bucket_name="products", prefix="prod_")
        
        if supabase_filename:
            # Get public url to save to DB
            public_url_res = get_supabase_public_url(supabase_filename, bucket_name="products")
            # public_url_res is likely a string url or dict
            filename = public_url_res if isinstance(public_url_res, str) else supabase_filename
        else:
            # Fallback local upload
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            # Must seek to 0 because upload_to_supabase might have read it (though it returned None if not configured, so wait)
            image.seek(0)
            image.save(filepath)
        
    product = Product(name=name, description=description, price=price, stock=stock, image_url=filename)
    db.session.add(product)
    db.session.commit()
    flash('Product added successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/product/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    if current_user.role != 'ADMIN':
        return redirect(url_for('main.index'))
        
    product = Product.query.get_or_404(product_id)
    # Could potentially delete the image file from OS here.
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/order/confirm/<int:order_id>')
@login_required
def confirm_order(order_id):
    if current_user.role != 'ADMIN':
        return redirect(url_for('main.index'))
        
    order = Order.query.get_or_404(order_id)
    order.status = 'PAYMENT_CONFIRMED'
    
    if order.payment:
        order.payment.verified = True
        from datetime import datetime
        order.payment.verified_at = datetime.utcnow()
        
    db.session.commit()
    
    # Send Email to Customer
    subject = "Your Order Has Been Accepted – Varnam Aesthetics"
    body = f"""
Hello {order.customer_name},

Your order has been successfully verified and accepted.
We will begin preparing your ornaments soon.

Order ID: {order.id}

Thank you for choosing Varnam Aesthetics.
"""
    send_email(subject, order.customer_email, body)
    
    flash(f'Order #{order.id} confirmed successfully.', 'success')
    return redirect(url_for('admin.dashboard'))
