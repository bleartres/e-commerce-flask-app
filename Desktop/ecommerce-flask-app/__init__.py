from flask import Flask, render_template, url_for, session, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc


UPLOAD_FOLDER = os.getcwd() + '/static/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.secret_key = "7423894732744234234134"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def database filename
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'

# init DB object
db = SQLAlchemy(app)


shopping_cart = []

# User Model
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	surname = db.Column(db.String(120), nullable=False)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(80), unique=True, nullable=False)
	role = db.Column(db.Integer, default=1, nullable=False)

	categories = db.relationship('Category', backref='user', lazy=True)

	def __init__(self, name, surname, username, password):
		self.name = name
		self.surname = surname
		self.username = username
		self.password = password

	def __repr__(self):
		return "<User: %s>" % self.name


# Category Model
class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	

	def __init__(self, name, user_id):
		self.name = name
		self.user_id = user_id

	def __repr__(self):
		return "<Category: %s>" % self.name

# Product Model
class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	description = db.Column(db.String(500), nullable=False)
	price = db.Column(db.String(10), nullable=False)
	discount = db.Column(db.String(3), nullable=False)
	image = db.Column(db.String(500), nullable=False)

	user_id = db.Column(db.Integer, nullable=False)
	category_id = db.Column(db.Integer, nullable=False)

	def __init__(self, name, description, price, discount, image, user_id, category_id):
		self.name = name
		self.description = description
		self.price = price
		self.discount = discount
		self.image = image
		self.user_id = user_id
		self.category_id = category_id

	def __repr__(self):
		return "<Product: %s>" % self.name

#Slide Model
class Slide(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120), nullable=False)
	description = db.Column(db.String(500), nullable=False)
	image = db.Column(db.String(500), nullable=False)

	def __init__(self, title, description, image):
		self.title = title
		self.description = description
		self.image = image


	def __repr__(self):
		return "<Slide: %s>" % self.title

# Email Model
class Email(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(60), nullable=False)
	subject = db.Column(db.String(120), nullable=False)
	message = db.Column(db.String(500), nullable=False)

	def __init__(self, fullname, email, subject, message):
		self.fullname = fullname
		self.email = email
		self.subject = subject
		self.message = message

	def __repr__(self):
		return "<Email: %s>" % self.email



# Subscribe Model
class Subscribe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), nullable=False)
	
	def __init__(self, email):
		self.email = email

	def __repr__(self):
		return "<Subscribe: %s>" % self.email


# Orders Model
class Orders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), nullable=False)
	surname = db.Column(db.String(60), nullable=False)
	address = db.Column(db.String(500), nullable=False)
	city_town = db.Column(db.String(50), nullable=False)
	zip_code = db.Column(db.String(12), nullable=False)
	cart_id = db.Column(db.String(12), nullable=False)
	user_id = db.Column(db.String(12), nullable=False)

	def __init__(self, name, surname, address, city_town, zip_code, cart_id, user_id):
		self.name = name
		self.surname = surname
		self.address = address
		self.city_town = city_town
		self.zip_code = zip_code
		self.cart_id = cart_id
		self.user_id = user_id

	def __repr__(self):
		return "<Order: %s>" % self.id


# Cart Model
class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String(120), nullable=False)
	number = db.Column(db.String(16), nullable=False)
	ccv = db.Column(db.String(3), nullable=False)

	def __init__(self, fullname, number, ccv):
		self.fullname = fullname
		self.number = number
		self.ccv = ccv

	def __repr__(self):
		return "<Cart: %s>" % self.number

# OrderProducts Model
class OrderProducts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	image = db.Column(db.String(250), nullable=False)
	name = db.Column(db.String(120), nullable=False)
	qty = db.Column(db.String(12), nullable=False)
	price = db.Column(db.String(12), nullable=False)

	order_id = db.Column(db.Integer, nullable=False)

	def __init__(self, image, name, qty, price, order_id):
		self.image = image
		self.name = name
		self.qty = qty
		self.price = price
		self.order_id = order_id

	def __repr__(self):
		return "<OrderProduct: %s>" % self.id


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form['email']		
		password = request.form['password']		

		# login action
		users = User.query.all()
		is_logged_in = False
		role = 0
		user_id = None

		for user in users:
			if user.username == username and check_password_hash(user.password, password):
				is_logged_in = True
				role = user.role
				user_id = user.id
				break

		if is_logged_in:
			session['is_logged_in'] = True
			session['username'] = username
			session['role'] = role
			session['user_id'] = user_id

			if role == 1:
				return redirect(url_for('orders'))
			elif role == 2:
				return redirect(url_for('adminOrders'))
			else:
				return redirect(url_for('home'))
		else:
			flash("Invalid data or user does not exist!")
			return redirect(url_for('login'))
	else:
		if session.get('is_logged_in'):
			return redirect(url_for('orders'))
		else:
			return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))


@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		name = request.form['name']
		surname = request.form['surname']
		username = request.form['email']
		password = generate_password_hash(request.form['password'])

		# create new user
		user = User(name, surname, username, password)
		db.session.add(user)
		db.session.commit()

		flash('You was registered successfully. Please log in!')
		return redirect(url_for('login'))
	else:
		return render_template('register.html')

@app.route("/")
def home():
	# perform DB init
	db.create_all()

	# last three products
	products = Product.query.order_by(desc(Product.id)).limit(3).all()
	slides = Slide.query.order_by(desc(Slide.id)).all()

	categories = Category.query.all()

	# argumenti i dyte products=products
	return render_template('home.html', categories=categories, products=products, slides=slides)

@app.route('/shop')
def shop():
	#session.pop('cart')
	categories = Category.query.all()
	products = Product.query.order_by(desc(Product.id)).all()

	return render_template('shop.html', categories=categories, products=products)


@app.route('/shop/category/<int:category>')
def showProductsForCategory(category):
	categories = Category.query.all()
	products = Product.query.filter_by(category_id=category).order_by(desc(Product.id)).all()

	return render_template('shop.html', categories=categories, products=products)


@app.route('/about-us')
def about():
	categories = Category.query.all()
	return render_template('about-us.html', categories=categories)

@app.route('/contact-us', methods=["GET", "POST"])
def contact():
	db.create_all()
	categories = Category.query.all()
	if request.method == "GET":
		return render_template('contact-us.html', categories=categories)
	elif request.method == "POST":
		# get form field values
		fullname 	= request.form['name']
		email 		= request.form['email']
		subject 	= request.form['subject']
		message 	= request.form['message']

		# save form data to the database
		email = Email(fullname, email, subject, message)
		db.session.add(email)
		db.session.commit()

		flash("Email was send successfully!")
		return redirect(url_for('contact'))

@app.route('/cart')
def cart():
	categories = Category.query.all()
	categories = Category.query.all()
	return render_template('cart.html', categories=categories)

@app.route('/checkout', methods = ["GET", "POST"])
def checkout():

	if request.method == 'POST':
		#Cart
		cart_name_surname = request.form['cart_name_surname']
		cart_number = request.form['cart_number']
		cart_ccv = request.form['cart_ccv']

		cart  = Cart(cart_name_surname, cart_number, cart_ccv)

		db.session.add(cart)
		db.session.commit()

        #Order
		name = request.form['name']
		surname = request.form['surname']
		address = request.form['address']
		city_town = request.form['city_town']
		zip_code = request.form['zip_code']
		cart_id = cart.id
		user_id = session.get('user_id')

		order = Orders(name, surname, address, city_town, zip_code, cart_id, user_id)

		db.session.add(order)
		db.session.commit()

        #OrderProducts
		order_id = order.id
		if session.get('cart') and len(session.get('cart')):
			for product in session.get('cart'):
				if product['user'] == session.get('user_id'): 	
					product_order = OrderProducts(product['image'], product['name'], product['qty'], product['price'], order_id)
					db.session.add(product_order)
					db.session.commit()	
		
		session['cart'] = [];
		flash("Order completed successfully!")
		return redirect(url_for('shop'))		

	else:
		categories = Category.query.all()
		return render_template('checkout.html', categories=categories)


@app.route('/search', methods = ["GET", "POST"])
def search():
	categories = Category.query.all()
	
	if request.method == 'POST':
		name = request.form['search']
		search = "%{}%".format(name)
		products = Product.query.filter(Product.name.like(search)).all()
		return render_template('search.html', categories=categories, products=products)
	else:
		flash('You havent specified any value')
		return render_template('search.html', categories=categories)

@app.route('/subscribe', methods=['POST'])
def subscribe():
	categories = Category.query.all()
	email = request.form['email']
	subscribe = Subscribe(email)
	db.session.add(subscribe)
	db.session.commit()
	flash('You are subscribed successfully')
	return redirect(url_for('home'))

@app.route('/subscribers')
def subscribers():
	role = session.get('role')
	route = 'administrator/subscribers.html'
	categories = Category.query.all()
	subscribers = Subscribe.query.all()

	if isAdminPage(role):
		return render_template(route, categories=categories, subscribers=subscribers)
	else:
		flash('You are not an administrator. This is an administrator page only!')
		return redirect(url_for('home'))

@app.route('/subscriber/<int:id>/delete')
def deleteSubscriberById(id):
	subscriber = Subscribe.query.get_or_404(id)
	db.session.delete(subscriber)
	db.session.commit()

	flash('Subscriber was deleted successfully!')
	return redirect(url_for('subscribers'))



#SLIDES
@app.route('/slides')
def slides():
	slides = Slide.query.all();
	categories = Category.query.all()

	role = session.get('role')
	route = 'administrator/slides/list.html'
	if isAdminPage(role):
		return render_template(route, categories=categories, slides=slides)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))

@app.route('/slides/<int:id>/delete')
def deleteSlideById(id):
	slide = Slide.query.get_or_404(id)
	db.session.delete(slide)
	db.session.commit()
	return redirect(url_for('slides'))

@app.route('/slides/new', methods=["GET", "POST"])
def createNewSlide():
	role = session.get('role')
	route = 'administrator/slides/new.html'

	if isAdminPage(role):
		if request.method == "POST":
			title = request.form['title']
			description = request.form['description']
			image_filename = "no-image.png"

			if request.files['image']:
				image = request.files['image']
				image_filename = image.filename


				if image and allowed_file(image.filename):
					filename = secure_filename(image.filename)
					image.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/slides/", filename))

			# DB
			slide = Slide(title, description, image_filename)
			db.session.add(slide)
			db.session.commit()

			flash('Slide was created successfully')
			return redirect(url_for('slides'))
		else:
			return render_template(route)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))

@app.route('/slides/<int:id>/edit', methods=["GET"])
def updateSlides(id):
	role = session.get('role')
	route = 'administrator/slides/edit.html'
	categories = Category.query.all()

	if isAdminPage(role):
		slide = Slide.query.get_or_404(id)
		return render_template(route, slide=slide, categories=categories)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))


@app.route('/slides/edit/action', methods=["POST"])
def updateSlideAction():
	role = session.get('role')
	route = 'administrator/slides/list.htm'
	id = request.form['id']

	slide = Slide.query.get_or_404(id)

	if len(slide.image) > 0:
		image_filename = slide.image
	else:
		image_filename = "no-image.png"

	if isAdminPage(role):
		title = request.form['title']
		description = request.form['description']

		if request.files['image']:
			image = request.files['image']
			image_filename = image.filename


			if image and allowed_file(image.filename):
				filename = secure_filename(image.filename)
				image.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/slides/", filename))

		slide = Slide.query.get_or_404(id)
		slide.title = title
		slide.description = description
		slide.image = image_filename
		db.session.commit()

		return redirect(url_for('slides'))
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))





# CLIENT
@app.route('/customer/orders')
def orders():
	role = session.get('role')
	route = 'customer/orders.html'
	categories = Category.query.all()
	orders = Orders.query.filter_by(user_id=session.get('user_id')).all()
	if isCustomerPage(role):
		return render_template(route, categories=categories, orders=orders)
	else:
		flash('You are not a customer. This is a customer page only!')
		return redirect(url_for('home'))

@app.route('/order/<int:id>/view')
def viewOrder(id):
	categories = Category.query.all()
	order = Orders.query.get_or_404(id)
	products = OrderProducts.query.filter_by(order_id=id).all()
	return render_template('customer/view-order.html', categories=categories, order=order, products=products)

# ADMINISTRATOR
@app.route('/administrator/orders')
def adminOrders():
	role = session.get('role')
	route = 'administrator/orders.html'
	categories = Category.query.all()
	if isAdminPage(role):
		orders = Orders.query.all()
		return render_template(route, categories=categories, orders=orders)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))

@app.route('/order/<int:id>/delete')
def deleteOrderById(id):
	order = Orders.query.get_or_404(id)

	if session.get('role'):
		if int(session.get('role')) == 1: # Customer
			if int(session.get('user_id')) == int(order.user_id):
				db.session.delete(order)
				db.session.commit()
				flash("Order was deleted successfully!")
				return redirect(url_for('orders'))
			else:
				flash('Cannot delete this order!')
				return redirect(url_for('orders'))
		elif int(session.get('role')) == 2:
			db.session.delete(order)
			db.session.commit()
			return redirect(url_for('adminOrders'))

@app.route('/categories')
def categories():
	user_id = session.get('user_id')
	user_categories = Category.query.filter_by(user_id=user_id).all();
	categories = Category.query.all()

	role = session.get('role')
	route = 'administrator/categories/list.html'
	if isAdminPage(role):
		return render_template(route, categories=categories, user_categories=user_categories)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))

@app.route('/category/<int:id>/delete')
def deleteCategoryById(id):
	category = Category.query.get_or_404(id)
	db.session.delete(category)
	db.session.commit()
	return redirect(url_for('categories'))

@app.route('/categories/new', methods=["GET", "POST"])
def createNewCategory():
	role = session.get('role')
	route = 'administrator/categories/new.html'

	if isAdminPage(role):
		if request.method == "POST":
			name = request.form['name']
			# DB
			user_id = session.get('user_id')
			category = Category(name, user_id)
			db.session.add(category)
			db.session.commit()

			flash('Category was created successfully')
			return redirect(url_for('categories'))
		else:
			return render_template(route)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))

@app.route('/categories/<int:id>/edit', methods=["GET"])
def updateCategory(id):
	role = session.get('role')
	route = 'administrator/categories/edit.html'
	categories = Category.query.all()

	if isAdminPage(role):
		category = Category.query.get_or_404(id)
		return render_template(route, category=category, categories=categories)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))


@app.route('/categories/edit/action', methods=["POST"])
def updateCategoryAction():
	role = session.get('role')
	route = 'administrator/categories/list.html'

	if isAdminPage(role):
		name = request.form['name']
		id = request.form['id']
		category = Category.query.get_or_404(id)
		category.name = name
		db.session.commit()

		user_id = session.get('user_id')
		categories = Category.query.filter_by(user_id=user_id)

		return redirect(url_for('categories'))
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))

@app.route('/products')
def products():
	role = session.get('role')
	route = 'administrator/products/list.html'
	categories = Category.query.all()
	products = Product.query.all()

	if isAdminPage(role):
		return render_template(route, categories=categories, products=products)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))


@app.route('/product/<int:id>/view')
def viewProductById(id):
	product = Product.query.get_or_404(id)
	return render_template('view-product.html', product=product)

@app.route('/products/new', methods=['GET', 'POST'])
def addNewProduct():
	role = session.get('role')
	route = 'administrator/products/new.html'
	categories = Category.query.all()

	if isAdminPage(role):
		if request.method == "POST":
			name = request.form['name']
			category_id = request.form['category']
			description = request.form['description']
			price = request.form['price']
			discount = request.form['discount']

			# DB
			user_id = session.get('user_id')

			image_filename = "no-image.png"

			if request.files['image']:
				image = request.files['image']
				image_filename = image.filename


				if image and allowed_file(image.filename):
					filename = secure_filename(image.filename)
					image.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/products/", filename))

			product = Product(name, description, price, discount, image_filename, user_id, category_id)
			db.session.add(product)
			db.session.commit()

			flash('Product was created successfully')
			return redirect(url_for('products'))
		else:
			return render_template(route, categories=categories)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))


@app.route('/products/<int:id>/edit')
def updateProduct(id):
	role = session.get('role')
	route = 'administrator/products/edit.html'
	categories = Category.query.all()

	if isAdminPage(role):
		product = Product.query.get_or_404(id)
		return render_template(route, categories=categories, product=product)
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))


@app.route('/product/update', methods=["POST"])
def updateProductAction():
	role = session.get('role')
	route = 'administrator/products/edit.html'
	categories = Category.query.all()

	if isAdminPage(role):
		id = request.form['id']
		product = Product.query.get_or_404(id)

		name = request.form['name']
		category_id = request.form['category']
		description = request.form['description']
		price = request.form['price']
		discount = request.form['discount']

		if request.files['image']:
			image = request.files['image']
			image_filename = image.filename


			if image and allowed_file(image.filename):
				filename = secure_filename(image.filename)
				image.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/products/", filename))


			product.image = image_filename


		product.name = name
		product.category_id = category_id
		product.description = description
		product.price = price
		product.discount = discount

		db.session.commit()

		return redirect(url_for('products'))
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))



@app.route('/products/<int:id>/delete')
def deleteProduct(id):
	role = session.get('role')
	product = Product.query.get_or_404(id)
	db.session.delete(product)
	db.session.commit()

	if isAdminPage(role):
		return redirect(url_for('products'))
	else:
		flash('You are not an admin. This is an admin page only!')
		return redirect(url_for('home'))


# CART
@app.route('/cart/add', methods=["POST"])
def addToCart():
	id = request.form['id']
	if session.get('is_logged_in'):
		if session.get('is_logged_in') == True:
			qty = request.form['qty']
			product = Product.query.get_or_404(id)
			price = product.price
			if int(product.discount) > 0:
				price = (float(product.price) * int(product.discount)) / 100
			cart_product = {
				"id" : product.id, 
				"image" : product.image, 
				"name" : product.name, 
				"qty" : qty, 
				"price" : price,
				"user" : session.get('user_id')
			}
			
			shopping_cart.append(cart_product)
			session['cart'] = shopping_cart

			return redirect(url_for('shop'))
	else:
		flash('Cannot add to cart without being logged in!')
		return redirect(url_for('viewProductById', id=id))

@app.route('/cart/product/<int:id>/remove')
def removeProductFromCart(id):
	updated_cart = []
	if session.get('cart') and session.get('is_logged_in'):
		if len(session['cart']) > 0:
			for product in session['cart']:
				if product['id'] != id:
					updated_cart.append(product)

	session['cart'] = updated_cart
	return redirect(url_for('cart'))


# HELPER FUNCTIONS
def checkValidRole(role):
	if role in [1,2]:
		return True
	else:
		return False

def isCustomer(role):
	return role == 1

def isAdministrator(role):
	return role == 2

def isAdminPage(role):
	if session.get('is_logged_in') and checkValidRole(role) and isAdministrator(role):
		return True
	else:
		return False


def isCustomerPage(role):
	if session.get('is_logged_in') and checkValidRole(role) and isCustomer(role):
		return True
	else:
		return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def removeSpacesFromString(word):
	return str(word).strip()


def generateImageForProduct(image):
	if len(image) == 0:
		return 'no-image.png'
	return image

def generateImageForSlide(image):
	if len(image) == 0:
		return 'no-image.png'
	return image

def countProductsForCategory(cat_id):
	return len(Product.query.filter_by(category_id=cat_id).all())

def countSearchedProducts(products):
	return len(products)

def cartTotal():
	total = 0
	if session.get('cart'):
		if len(session.get('cart')) > 0:
			for product in session['cart']:
				total += (int(product['qty']) * float(product['price']))
	return total

def countCartItems():
	total = 0
	if session.get('cart'):
		for product in session.get('cart'):
			if session.get('user_id') == product['user']:
				total += 1
	return total

def orderTotal(id):
	order_products = OrderProducts.query.filter_by(order_id=id).all()
	total = 0

	if len(order_products) > 0:
		for product in order_products:
			total += (int(product.qty) * float(product.price))

	return total

def userOrdersTotal(user_id):
	total = 0
	orders = Orders.query.filter_by(user_id=user_id).all()

	if len(orders) > 0:
		for order in orders:
			total += orderTotal(order.id)

	return total

def allOrdersTotal():
	total = 0
	orders = Orders.query.all()

	if len(orders) > 0:
		for order in orders:
			total += orderTotal(order.id)

	return total

def countCartProductsOfLoggedInUser():
	total = 0
	if session.get('cart') and len(session.get('cart')) > 0:
		for product in session.get('cart'):
			if product['user'] == session.get('user_id'):
				total += 1
	return total





app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(float=float)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(str=str)
app.jinja_env.globals.update(print=print)
app.jinja_env.globals.update(remove_spaces=removeSpacesFromString)
app.jinja_env.globals.update(generateImageForProduct=generateImageForProduct)
app.jinja_env.globals.update(countProductsForCategory=countProductsForCategory)
app.jinja_env.globals.update(countSearchedProducts=countSearchedProducts)
app.jinja_env.globals.update(generateImageForSlide=generateImageForSlide)
app.jinja_env.globals.update(countCartItems=countCartItems)
app.jinja_env.globals.update(cartTotal=cartTotal)
app.jinja_env.globals.update(orderTotal=orderTotal)
app.jinja_env.globals.update(userOrdersTotal=userOrdersTotal)
app.jinja_env.globals.update(allOrdersTotal=allOrdersTotal)
app.jinja_env.globals.update(countCartProductsOfLoggedInUser=countCartProductsOfLoggedInUser)


if '__name__' == '__init__':
	app.run(debug=True)