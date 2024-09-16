from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from database import db  # type: ignore
from models import Review, User, Product, Order, OrderItem  # type: ignore
import os
import mysql.connector
import sqlite3

app = Flask(
    __name__,
    template_folder=os.path.join('..', 'frontend', 'templates'),
    static_folder=os.path.join('..', 'frontend', 'static')
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:hawaii2005@localhost:3307/products'
app.config['SECRET_KEY'] = 'harry porter'
db.init_app(app)
migrate = Migrate(app, db)

ABA_API_URL = 'https://api.aba.com/payment'
ABA_API_KEY = 'your_api_key_here'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit-order', methods=['POST'])
def submit_order():
    order_data = request.json
    
    payment_data = {
        'amount': calculate_total_amount(order_data['cart']),
        'currency': 'KHR',
        'customer_name': order_data['customer_name'],
        'customer_email': order_data['customer_email'],
        # Add other required fields
    }
    
    response = requests.post(ABA_API_URL, json=payment_data, headers={
        'Authorization': f'Bearer {ABA_API_KEY}',
        'Content-Type': 'application/json'
    })
    
    if response.status_code == 200:
        return jsonify({'message': 'Order submitted successfully!'})
    else:
        return jsonify({'message': 'Payment failed. Please try again.'}), 400

def calculate_total_amount(cart):
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']

        if password != repeat_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('welcome', name=name))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',      
        port=3307,              
        user='root',   
        password='hawaii2005', 
        database='products'     
    )
    return connection

@app.route('/products')
def products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT pro_id AS id, type, weight, price, description, quantity, image AS image_filename FROM rice_product"
    cursor.execute(query)
    
    products = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('products.html', products=products)

@app.route('/order/<int:product_id>', methods=['POST'])
def order(product_id):
    if 'user_id' not in session:
        flash('You need to log in to place an order.')
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)
    quantity = int(request.form['quantity'])

    if quantity > product.stock:
        flash('Not enough stock available.')
        return redirect(url_for('products'))

    order = Order(user_id=session['user_id'])
    db.session.add(order)
    db.session.commit()

    order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, price=product.price)
    db.session.add(order_item)
    product.stock -= quantity
    db.session.commit()

    flash('Order placed successfully!')
    return redirect(url_for('index'))

@app.route('/admin/login', methods=['POST'])
def do_admin_login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        flash('Login successful!')
        return redirect(url_for('admin_orders'))  # Redirect to an appropriate page
    else:
        flash('Invalid email or password.')
        return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/welcome')
def welcome():
    name = request.args.get('name', 'Guest')
    return render_template('welcome.html', name=name)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')  # Ensure this template exists

@app.route('/submit_review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    review_text = request.form['review']
    rating = int(request.form['rating'])

    new_review = Review(
        product_id=product.id,
        user_name=session.get('user_name', 'Anonymous'),  # Assuming you have a way to get the user's name
        text=review_text,
        rating=rating
    )

    db.session.add(new_review)
    db.session.commit()

    flash('Review submitted successfully!')
    return redirect(url_for('products'))

@app.route('/more-products/<category>', methods=['GET'])
def more_products(category):
    products = Product.query.filter_by(category=category).all()
    product_list = [{
        'id': product.id,
        'type': product.type,
        'price': product.price,
        'description': product.description,
        'image_filename': product.image_filename,
        'rating': sum(review.rating for review in product.reviews) // len(product.reviews) if product.reviews else 0
    } for product in products]
    return jsonify({'products': product_list})

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/initiate-payment', methods=['POST'])
def initiate_payment():
    order_data = request.json
    payment_request = {
        "amount": order_data['total_price'],
        "currency": "USD",
        "order_id": order_data['order_id'],
        "return_url": "http://yourdomain.com/payment-success",
        "cancel_url": "http://yourdomain.com/payment-cancel"
    }
    
    response = requests.post('https://abaapi.com/payment', json=payment_request)
    
    return jsonify(response.json())

@app.route('/payment-success')
def payment_success():
    return "Payment successful! Thank you for your purchase."

@app.route('/payment-cancel')
def payment_cancel():
    return "Payment was cancelled."

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        flash('Search query is empty.')
        return redirect(url_for('index'))

    products = Product.query.filter(Product.type.ilike(f'%{query}%')).all()
    return render_template('search.html', products=products, query=query)


if __name__ == '__main__':
    app.run(debug=True)
