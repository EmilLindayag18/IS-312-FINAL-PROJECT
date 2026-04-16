from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Configuration (Railway & XAMPP)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', os.environ.get('MYSQLHOST', 'localhost'))
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', os.environ.get('MYSQLUSER', 'root'))
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', os.environ.get('MYSQLPASSWORD', ''))
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', os.environ.get('MYSQLDATABASE', 'vsalon_db'))
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', os.environ.get('MYSQLPORT', 3306)))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ==================== DECORATORS ====================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services WHERE is_active = TRUE LIMIT 6")
    services = cur.fetchall()
    cur.execute("SELECT * FROM products WHERE is_active = TRUE LIMIT 4")
    products = cur.fetchall()
    cur.close()
    return render_template('homepage.html', services=services, products=products)

@app.route('/services')
def services_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services WHERE is_active = TRUE")
    services = cur.fetchall()
    cur.close()
    return render_template('services.html', services=services)

@app.route('/shop')
def shop():
    category = request.args.get('category', '')
    cur = mysql.connection.cursor()
    if category:
        cur.execute("SELECT * FROM products WHERE is_active = TRUE AND category = %s", (category,))
    else:
        cur.execute("SELECT * FROM products WHERE is_active = TRUE")
    products = cur.fetchall()
    cur.execute("SELECT DISTINCT category FROM products WHERE is_active = TRUE")
    categories = [row['category'] for row in cur.fetchall()]
    cur.close()
    return render_template('shop.html', products=products, categories=categories, selected_category=category)

@app.route('/about')
def about():
    return render_template('about.html')

# ==================== AUTH ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['role'] = user['role']
            session['email'] = user['email']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('customer_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            cur.close()
            return render_template('register.html')
        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO users (full_name, email, phone, password_hash, role) VALUES (%s,%s,%s,%s,'customer')",
                     (full_name, email, phone, hashed))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ==================== CUSTOMER ROUTES ====================

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT a.*, s.name as service_name, s.price, st.full_name as staff_name
                   FROM appointments a
                   JOIN services s ON a.service_id = s.id
                   LEFT JOIN staff st ON a.staff_id = st.id
                   WHERE a.customer_id = %s ORDER BY a.appointment_date DESC LIMIT 10""", (session['user_id'],))
    appointments = cur.fetchall()
    cur.execute("""SELECT o.*, COUNT(oi.id) as item_count FROM orders o
                   LEFT JOIN order_items oi ON o.id = oi.order_id
                   WHERE o.customer_id = %s GROUP BY o.id ORDER BY o.created_at DESC LIMIT 5""", (session['user_id'],))
    orders = cur.fetchall()
    cur.close()
    return render_template('customer/dashboard.html', appointments=appointments, orders=orders)

@app.route('/customer/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        service_id = request.form['service_id']
        staff_id = request.form.get('staff_id') or None
        date = request.form['appointment_date']
        time = request.form['appointment_time']
        notes = request.form.get('notes', '')
        cur.execute("""INSERT INTO appointments (customer_id, service_id, staff_id, appointment_date, appointment_time, notes)
                       VALUES (%s,%s,%s,%s,%s,%s)""", (session['user_id'], service_id, staff_id, date, time, notes))
        mysql.connection.commit()
        cur.close()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('customer_dashboard'))
    cur.execute("SELECT * FROM services WHERE is_active = TRUE")
    services = cur.fetchall()
    cur.execute("SELECT * FROM staff WHERE is_active = TRUE")
    staff = cur.fetchall()
    cur.close()
    return render_template('customer/book_appointment.html', services=services, staff=staff)

@app.route('/customer/appointments')
@login_required
def customer_appointments():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT a.*, s.name as service_name, s.price, s.duration_minutes, st.full_name as staff_name
                   FROM appointments a
                   JOIN services s ON a.service_id = s.id
                   LEFT JOIN staff st ON a.staff_id = st.id
                   WHERE a.customer_id = %s ORDER BY a.appointment_date DESC""", (session['user_id'],))
    appointments = cur.fetchall()
    cur.close()
    return render_template('customer/appointments.html', appointments=appointments)

@app.route('/customer/cancel_appointment/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE appointments SET status='cancelled' WHERE id=%s AND customer_id=%s", (appointment_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('customer_appointments'))

@app.route('/customer/reschedule/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        date = request.form['appointment_date']
        time = request.form['appointment_time']
        cur.execute("UPDATE appointments SET appointment_date=%s, appointment_time=%s, status='rescheduled' WHERE id=%s AND customer_id=%s",
                     (date, time, appointment_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        flash('Appointment rescheduled.', 'success')
        return redirect(url_for('customer_appointments'))
    cur.execute("""SELECT a.*, s.name as service_name FROM appointments a
                   JOIN services s ON a.service_id = s.id WHERE a.id=%s AND a.customer_id=%s""", (appointment_id, session['user_id']))
    appointment = cur.fetchone()
    cur.close()
    return render_template('customer/reschedule.html', appointment=appointment)

@app.route('/customer/shop/buy/<int:product_id>', methods=['POST'])
@login_required
def buy_product(product_id):
    quantity = int(request.form.get('quantity', 1))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cur.fetchone()
    if not product or product['stock_quantity'] < quantity:
        flash('Product not available or insufficient stock.', 'danger')
        cur.close()
        return redirect(url_for('shop'))
    total = product['price'] * quantity
    cur.execute("INSERT INTO orders (customer_id, total_amount, status, payment_method) VALUES (%s,%s,'completed','online')",
                 (session['user_id'], total))
    order_id = cur.lastrowid
    cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                 (order_id, product_id, quantity, product['price']))
    cur.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE id=%s", (quantity, product_id))
    cur.execute("INSERT INTO inventory_log (product_id, change_quantity, reason) VALUES (%s,%s,'Online purchase')",
                 (product_id, -quantity))
    cur.execute("INSERT INTO pos_transactions (order_id, amount, payment_method, transaction_type) VALUES (%s,%s,'online','product_sale')",
                 (order_id, total))
    mysql.connection.commit()
    cur.close()
    flash('Purchase successful!', 'success')
    return redirect(url_for('customer_dashboard'))

@app.route('/customer/profile', methods=['GET', 'POST'])
@login_required
def customer_profile():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        cur.execute("UPDATE users SET full_name=%s, phone=%s WHERE id=%s", (full_name, phone, session['user_id']))
        mysql.connection.commit()
        session['user_name'] = full_name
        flash('Profile updated.', 'success')
    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.execute("""SELECT a.appointment_date, s.name as service_name, st.full_name as staff_name
                   FROM appointments a JOIN services s ON a.service_id = s.id
                   LEFT JOIN staff st ON a.staff_id = st.id
                   WHERE a.customer_id = %s AND a.status='completed' ORDER BY a.appointment_date DESC""", (session['user_id'],))
    history = cur.fetchall()
    cur.close()
    return render_template('customer/profile.html', user=user, history=history)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as total FROM appointments WHERE status='pending'")
    pending = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM appointments WHERE appointment_date = CURDATE()")
    today_appts = cur.fetchone()['total']
    cur.execute("SELECT COALESCE(SUM(amount),0) as total FROM pos_transactions WHERE DATE(created_at) = CURDATE()")
    today_sales = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM products WHERE stock_quantity <= low_stock_threshold AND is_active = TRUE")
    low_stock = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM users WHERE role='customer'")
    total_customers = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM staff WHERE is_active = TRUE")
    total_staff = cur.fetchone()['total']
    cur.execute("""SELECT a.*, u.full_name as customer_name, s.name as service_name, st.full_name as staff_name
                   FROM appointments a JOIN users u ON a.customer_id = u.id
                   JOIN services s ON a.service_id = s.id LEFT JOIN staff st ON a.staff_id = st.id
                   ORDER BY a.created_at DESC LIMIT 10""")
    recent_appointments = cur.fetchall()
    cur.execute("SELECT * FROM pos_transactions ORDER BY created_at DESC LIMIT 10")
    recent_transactions = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html', pending=pending, today_appts=today_appts,
                           today_sales=today_sales, low_stock=low_stock, total_customers=total_customers,
                           total_staff=total_staff, recent_appointments=recent_appointments,
                           recent_transactions=recent_transactions)

@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    status_filter = request.args.get('status', '')
    cur = mysql.connection.cursor()
    if status_filter:
        cur.execute("""SELECT a.*, u.full_name as customer_name, s.name as service_name, st.full_name as staff_name
                       FROM appointments a JOIN users u ON a.customer_id = u.id
                       JOIN services s ON a.service_id = s.id LEFT JOIN staff st ON a.staff_id = st.id
                       WHERE a.status=%s ORDER BY a.appointment_date DESC""", (status_filter,))
    else:
        cur.execute("""SELECT a.*, u.full_name as customer_name, s.name as service_name, st.full_name as staff_name
                       FROM appointments a JOIN users u ON a.customer_id = u.id
                       JOIN services s ON a.service_id = s.id LEFT JOIN staff st ON a.staff_id = st.id
                       ORDER BY a.appointment_date DESC""")
    appointments = cur.fetchall()
    cur.execute("SELECT * FROM staff WHERE is_active = TRUE")
    staff = cur.fetchall()
    cur.close()
    return render_template('admin/appointments.html', appointments=appointments, staff=staff, selected_status=status_filter)

@app.route('/admin/appointments/update/<int:appt_id>', methods=['POST'])
@admin_required
def update_appointment(appt_id):
    status = request.form['status']
    staff_id = request.form.get('staff_id') or None
    cur = mysql.connection.cursor()
    cur.execute("UPDATE appointments SET status=%s, staff_id=%s WHERE id=%s", (status, staff_id, appt_id))
    if status == 'completed':
        cur.execute("""SELECT s.price FROM appointments a JOIN services s ON a.service_id = s.id WHERE a.id=%s""", (appt_id,))
        price = cur.fetchone()['price']
        cur.execute("INSERT INTO pos_transactions (appointment_id, amount, payment_method, transaction_type, processed_by) VALUES (%s,%s,'cash','service_payment',%s)",
                     (appt_id, price, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Appointment updated.', 'success')
    return redirect(url_for('admin_appointments'))

@app.route('/admin/staff', methods=['GET', 'POST'])
@admin_required
def admin_staff():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['full_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        spec = request.form.get('specialization', '')
        cur.execute("INSERT INTO staff (full_name, email, phone, specialization) VALUES (%s,%s,%s,%s)",
                     (name, email, phone, spec))
        mysql.connection.commit()
        flash('Staff added.', 'success')
    cur.execute("SELECT * FROM staff ORDER BY full_name")
    staff = cur.fetchall()
    cur.close()
    return render_template('admin/staff.html', staff=staff)

@app.route('/admin/staff/toggle/<int:staff_id>')
@admin_required
def toggle_staff(staff_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE staff SET is_active = NOT is_active WHERE id=%s", (staff_id,))
    mysql.connection.commit()
    cur.close()
    flash('Staff status updated.', 'info')
    return redirect(url_for('admin_staff'))

@app.route('/admin/inventory')
@admin_required
def admin_inventory():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products ORDER BY name")
    products = cur.fetchall()
    cur.execute("SELECT p.name, il.change_quantity, il.reason, il.created_at FROM inventory_log il JOIN products p ON il.product_id = p.id ORDER BY il.created_at DESC LIMIT 20")
    logs = cur.fetchall()
    cur.close()
    return render_template('admin/inventory.html', products=products, logs=logs)

@app.route('/admin/inventory/update/<int:product_id>', methods=['POST'])
@admin_required
def update_stock(product_id):
    quantity = int(request.form['quantity'])
    reason = request.form.get('reason', 'Manual adjustment')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE id=%s", (quantity, product_id))
    cur.execute("INSERT INTO inventory_log (product_id, change_quantity, reason) VALUES (%s,%s,%s)", (product_id, quantity, reason))
    mysql.connection.commit()
    cur.close()
    flash('Stock updated.', 'success')
    return redirect(url_for('admin_inventory'))

@app.route('/admin/products', methods=['GET', 'POST'])
@admin_required
def admin_products():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form.get('description', '')
        price = request.form['price']
        stock = request.form.get('stock_quantity', 0)
        category = request.form.get('category', '')
        threshold = request.form.get('low_stock_threshold', 5)
        cur.execute("INSERT INTO products (name, description, price, stock_quantity, category, low_stock_threshold) VALUES (%s,%s,%s,%s,%s,%s)",
                     (name, desc, price, stock, category, threshold))
        mysql.connection.commit()
        flash('Product added.', 'success')
    cur.execute("SELECT * FROM products ORDER BY name")
    products = cur.fetchall()
    cur.close()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/edit/<int:product_id>', methods=['POST'])
@admin_required
def edit_product(product_id):
    name = request.form['name']
    desc = request.form.get('description', '')
    price = request.form['price']
    category = request.form.get('category', '')
    is_active = 1 if request.form.get('is_active') else 0
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name=%s, description=%s, price=%s, category=%s, is_active=%s WHERE id=%s",
                 (name, desc, price, category, is_active, product_id))
    mysql.connection.commit()
    cur.close()
    flash('Product updated.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/pos', methods=['GET', 'POST'])
@admin_required
def admin_pos():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        payment = request.form['payment_method']
        cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cur.fetchone()
        if product and product['stock_quantity'] >= quantity:
            total = product['price'] * quantity
            cur.execute("INSERT INTO orders (customer_id, total_amount, status, payment_method) VALUES (%s,%s,'completed',%s)",
                         (session['user_id'], total, payment))
            order_id = cur.lastrowid
            cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                         (order_id, product_id, quantity, product['price']))
            cur.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE id=%s", (quantity, product_id))
            cur.execute("INSERT INTO inventory_log (product_id, change_quantity, reason) VALUES (%s,%s,'POS Sale')", (product_id, -quantity))
            cur.execute("INSERT INTO pos_transactions (order_id, amount, payment_method, transaction_type, processed_by) VALUES (%s,%s,%s,'product_sale',%s)",
                         (order_id, total, payment, session['user_id']))
            mysql.connection.commit()
            flash(f'Sale recorded! Total: ₱{total:.2f}', 'success')
        else:
            flash('Insufficient stock.', 'danger')
    cur.execute("SELECT * FROM products WHERE is_active = TRUE AND stock_quantity > 0 ORDER BY name")
    products = cur.fetchall()
    cur.execute("SELECT pt.*, p.name as product_name FROM pos_transactions pt LEFT JOIN orders o ON pt.order_id = o.id LEFT JOIN order_items oi ON o.id = oi.order_id LEFT JOIN products p ON oi.product_id = p.id ORDER BY pt.created_at DESC LIMIT 20")
    transactions = cur.fetchall()
    cur.close()
    return render_template('admin/pos.html', products=products, transactions=transactions)

@app.route('/admin/reports')
@admin_required
def admin_reports():
    cur = mysql.connection.cursor()
    # Sales by day (last 7 days)
    cur.execute("""SELECT DATE(created_at) as date, SUM(amount) as total, COUNT(*) as count
                   FROM pos_transactions WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                   GROUP BY DATE(created_at) ORDER BY date""")
    daily_sales = cur.fetchall()
    # Service popularity
    cur.execute("""SELECT s.name, COUNT(a.id) as bookings, SUM(s.price) as revenue
                   FROM appointments a JOIN services s ON a.service_id = s.id
                   GROUP BY s.id ORDER BY bookings DESC""")
    service_stats = cur.fetchall()
    # Product sales
    cur.execute("""SELECT p.name, SUM(oi.quantity) as sold, SUM(oi.quantity * oi.unit_price) as revenue
                   FROM order_items oi JOIN products p ON oi.product_id = p.id
                   GROUP BY p.id ORDER BY sold DESC""")
    product_stats = cur.fetchall()
    # Monthly revenue
    cur.execute("""SELECT DATE_FORMAT(created_at, '%%Y-%%m') as month, SUM(amount) as total
                   FROM pos_transactions GROUP BY month ORDER BY month DESC LIMIT 12""")
    monthly_revenue = cur.fetchall()
    cur.close()
    return render_template('admin/reports.html', daily_sales=daily_sales, service_stats=service_stats,
                           product_stats=product_stats, monthly_revenue=monthly_revenue)

@app.route('/admin/services', methods=['GET', 'POST'])
@admin_required
def admin_services():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form.get('description', '')
        duration = request.form.get('duration_minutes', 30)
        price = request.form['price']
        category = request.form.get('category', '')
        cur.execute("INSERT INTO services (name, description, duration_minutes, price, category) VALUES (%s,%s,%s,%s,%s)",
                     (name, desc, duration, price, category))
        mysql.connection.commit()
        flash('Service added.', 'success')
    cur.execute("SELECT * FROM services ORDER BY name")
    services = cur.fetchall()
    cur.close()
    return render_template('admin/services.html', services=services)

# ==================== API ROUTES ====================

@app.route('/api/check_availability')
def check_availability():
    date = request.args.get('date')
    staff_id = request.args.get('staff_id')
    cur = mysql.connection.cursor()
    cur.execute("""SELECT appointment_time FROM appointments
                   WHERE appointment_date=%s AND staff_id=%s AND status NOT IN ('cancelled')""", (date, staff_id))
    booked = [str(row['appointment_time']) for row in cur.fetchall()]
    cur.close()
    all_times = [f"{h:02d}:{m:02d}" for h in range(9, 18) for m in (0, 30)]
    available = [t for t in all_times if t + ':00' not in booked]
    return jsonify(available=available)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
