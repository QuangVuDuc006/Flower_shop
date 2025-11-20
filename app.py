import os
from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Product, Category, Order, OrderItem
from forms import LoginForm, RegisterForm, ProductForm, CheckoutForm
import uuid

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Context Processor (Injects data into all templates) ---
@app.context_processor
def inject_context():
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    categories = Category.query.all()
    return dict(cart_count=cart_count, categories=categories)

# --- Helper: Image Upload ---
def save_image(file):
    if not file: return None
    filename = secure_filename(file.filename)
    unique_name = str(uuid.uuid4()) + "_" + filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
    return unique_name

# --- Routes ---

@app.route('/')
def index():
    # Query params for filter
    cat_id = request.args.get('category')
    q = request.args.get('q')
    
    query = Product.query
    if cat_id:
        query = query.filter_by(category_id=cat_id)
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))
        
    products = query.all()
    return render_template('index.html', products=products, title="Home")

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related = Product.query.filter_by(category_id=product.category_id).filter(Product.id != id).limit(4).all()
    return render_template('product.html', product=product, related=related)

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + quantity
    session['cart'] = cart
    flash(f'Đã thêm vào giỏ hàng!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_data = session.get('cart', {})
    products = []
    total = 0
    
    if request.method == 'POST':
        # Update quantities
        new_cart = {}
        for pid, qty in cart_data.items():
            new_qty = int(request.form.get(f'qty_{pid}', qty))
            if new_qty > 0:
                new_cart[pid] = new_qty
        session['cart'] = new_cart
        if request.form.get('action') == 'checkout':
            return redirect(url_for('checkout'))
        return redirect(url_for('cart'))

    for pid, qty in cart_data.items():
        p = Product.query.get(int(pid))
        if p:
            products.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
            total += p.price * qty
            
    return render_template('cart.html', items=products, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_data = session.get('cart', {})
    if not cart_data:
        return redirect(url_for('index'))
    
    form = CheckoutForm()
    # Prefill if logged in
    if current_user.is_authenticated and request.method == 'GET':
        form.name.data = current_user.username
        form.phone.data = "0123456789" # Mock

    if form.validate_on_submit():
        total = 0
        # Calculate total again for security
        for pid, qty in cart_data.items():
            p = Product.query.get(int(pid))
            if p: total += p.price * qty
        
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=form.name.data,
            customer_phone=form.phone.data,
            customer_address=form.address.data,
            total_price=total
        )
        db.session.add(order)
        db.session.commit()

        # Add Items
        for pid, qty in cart_data.items():
            p = Product.query.get(int(pid))
            if p:
                item = OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price_at_purchase=p.price)
                db.session.add(item)
        
        db.session.commit()
        session.pop('cart', None)
        flash('Đặt hàng thành công! Chúng tôi sẽ liên hệ sớm.', 'success')
        return redirect(url_for('index'))
        
    return render_template('checkout.html', form=form)

# --- Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # --- DEBUG LOGS (Xem ở Terminal) ---
        print(f"Login attempt for: {form.email.data}")
        print(f"User found: {user}")
        if user:
            is_correct = check_password_hash(user.password, form.password.data)
            print(f"Password check result: {is_correct}")
            print(f"DB Hash: {user.password}")
        # -----------------------------------

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Sai email hoặc mật khẩu bạn ơi!', 'danger')
    else:
        # In lỗi form ra nếu validate sai
        print("Form validation errors:", form.errors)
        
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        
        # --- THÊM ĐOẠN NÀY ĐỂ CHECK EMAIL TRÙNG ---
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email này đã đăng ký rồi bạn ơi! Qua trang Login nhé.', 'warning')
            return redirect(url_for('login'))
        
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username này có người lấy rồi, chọn cái khác đi.', 'warning')
            return render_template('register.html', form=form)
        # ------------------------------------------

        # Lưu ý: Nhớ dùng method='pbkdf2:sha256' như tui dặn ở trên nhé
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Tạo tài khoản xong rồi đó, đăng nhập đi!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback() # Hoàn tác nếu lỗi
            flash(f'Lỗi hệ thống: {str(e)}', 'danger')
            
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Admin Routes ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin: return redirect(url_for('index'))
    products = Product.query.all()
    orders = Order.query.order_by(Order.date_ordered.desc()).all()
    return render_template('admin/dashboard.html', products=products, orders=orders)

@app.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if not current_user.is_admin: return redirect(url_for('index'))
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        filename = save_image(form.image.data) or 'default.jpg'
        product = Product(
            name=form.name.data, price=form.price.data,
            description=form.description.data, stock=form.stock.data,
            category_id=form.category.data, image=filename
        )
        db.session.add(product)
        db.session.commit()
        flash('Thêm sản phẩm thành công', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/product_form.html', form=form, title="New Product")

# Custom 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html'), 404 # Minimal fallback, usually separate template

if __name__ == '__main__':
    # Auto create folders
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True)